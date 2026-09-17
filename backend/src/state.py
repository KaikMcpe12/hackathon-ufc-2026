"""Estado in-memory (ADR 0001). Carregado no startup; substituível por upload (ADR 0002)."""
from __future__ import annotations

import logging
import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import pandas as pd

from . import config
from .pipeline import build

# slot de upload -> nome canônico do arquivo em data_dir (ADR 0002)
_SLOT_ARQUIVO = {
    "semana_1": "pedidos_semana_1.csv",
    "semana_2": "pedidos_semana_2.csv",
    "semana_3": "pedidos_semana_3.csv",
    "semana_4": "pedidos_semana_4.csv",
    "ranking": "ranking_top85.csv",
    "rotas": "rotas_coletas.csv",
}
_COLS_PEDIDOS = {"Pedido", "Data", "Cidade", "Situacao", "Situacao_CSV_Entrega",
                 "Valor_Pedido", "Itens_Resumo"}
_COLS_RANKING = {"Codigo", "Unidade_Venda", "Peso_kg", "Volume_m3"}


class ColunasInvalidas(Exception):
    """Upload sem as colunas esperadas (→ 400)."""


@dataclass
class AppState:
    pedidos_raw: pd.DataFrame
    pedidos_processados: pd.DataFrame
    ranking: pd.DataFrame
    referencias_sinteticas: pd.DataFrame
    veiculos: pd.DataFrame
    eixos: pd.DataFrame
    log_correcoes: list[dict] = field(default_factory=list)
    motivos_exclusao: list[dict] = field(default_factory=list)
    stats: dict = field(default_factory=dict)


_state: AppState | None = None
# Diretório de trabalho em runtime (temporário, efêmero). Guarda os CSVs seed +
# uploads acumulados. Reinício do processo o recria (ADR 0001 — sem persistência em disco).
_runtime_dir: Path | None = None
_repo = None  # SqliteRepo quando STATE_BACKEND=sqlite (PRD-12)


def _from_artefatos(a: dict) -> AppState:
    return AppState(
        pedidos_raw=a["pedidos_raw"],
        pedidos_processados=a["pedidos_processados"],
        ranking=a["ranking"],
        referencias_sinteticas=a["referencias_sinteticas"],
        veiculos=a["veiculos"],
        eixos=a["eixos"],
        log_correcoes=a["log_correcoes"],
        motivos_exclusao=a["motivos_exclusao"],
        stats=a["stats"],
    )


def _novo_runtime_dir(seed: Path | None) -> Path:
    """Cria um dir de runtime e copia os CSVs do seed (se houver)."""
    d = Path(tempfile.mkdtemp(prefix="nobrelog_state_"))
    if seed and seed.exists():
        for arq in seed.iterdir():
            if arq.is_file() and arq.suffix == ".csv":
                shutil.copy(arq, d / arq.name)
    return d


def bootstrap(data_dir: Path | None = None) -> AppState:
    """Publica o estado inicial. Chamado no startup do FastAPI.

    - `USE_SEED_DATA=true` (default): carrega os CSVs seed (mock/demo).
    - `USE_SEED_DATA=false`: inicia VAZIO (produção — o usuário importa via /etl/ingest).
    Resiliente: dados ausentes/corrompidos → estado vazio em vez de derrubar o app.
    """
    global _state, _runtime_dir, _repo
    if _runtime_dir is not None:
        shutil.rmtree(_runtime_dir, ignore_errors=True)  # limpa runtime anterior

    if config.STATE_BACKEND == "sqlite":  # persistência opt-in (PRD-12)
        try:
            from .db.repository import SqliteRepo
            _repo = SqliteRepo(config.DB_PATH)
            if config.USE_SEED_DATA:
                _repo.seed_from_csv(data_dir or config.DATA_DIR)
            _rebuild_from_repo(data_dir or config.DATA_DIR)
            return _state
        except Exception:
            logging.getLogger("nobrelog").exception("bootstrap sqlite falhou — caindo p/ memória")

    seed = (data_dir or config.DATA_DIR) if config.USE_SEED_DATA else None
    try:
        _runtime_dir = _novo_runtime_dir(seed)
        _state = _from_artefatos(build(_runtime_dir))
    except Exception:
        logging.getLogger("nobrelog").exception("bootstrap falhou — iniciando com estado vazio")
        _runtime_dir = _novo_runtime_dir(None)
        _state = _from_artefatos(build(_runtime_dir))
    return _state


def _rebuild_from_repo(seed_dir: Path | None = None) -> AppState:
    """Re-materializa o banco em CSVs e reconstrói o estado (após seed/upsert)."""
    global _state, _runtime_dir
    if _runtime_dir is not None:
        shutil.rmtree(_runtime_dir, ignore_errors=True)
    _runtime_dir = _novo_runtime_dir(None)
    _repo.materialize(_runtime_dir, seed_dir or config.DATA_DIR)
    _state = _from_artefatos(build(_runtime_dir))
    return _state


def cadastrar_produtos(rows: list[dict]) -> dict:
    """Upsert de produtos (form/CSV) + reprocessa o pipeline. Requer STATE_BACKEND=sqlite."""
    if _repo is None:
        raise RuntimeError("Cadastro exige STATE_BACKEND=sqlite.")
    rel = _repo.upsert_produtos(rows)
    _rebuild_from_repo()
    return rel


def cadastrar_pedidos(rows: list[dict]) -> dict:
    if _repo is None:
        raise RuntimeError("Cadastro exige STATE_BACKEND=sqlite.")
    rel = _repo.upsert_pedidos(rows)
    _rebuild_from_repo()
    return rel


def repo_ativo() -> bool:
    return _repo is not None


def contagem_db() -> dict:
    return _repo.contagem() if _repo is not None else {}


def get_state() -> AppState:
    if _state is None:
        return bootstrap()
    return _state


def tem_dados() -> bool:
    return bool(_state and _state.stats.get("registros_processados", 0) > 0)


def _valida_colunas(slot: str, raw: bytes) -> None:
    header = raw.split(b"\n", 1)[0].decode("utf-8-sig", errors="replace")
    cols = {c.strip() for c in header.split(";")}
    faltando: set[str] = set()
    if slot.startswith("semana_"):
        faltando = _COLS_PEDIDOS - cols
    elif slot == "ranking":
        faltando = _COLS_RANKING - cols
    if faltando:
        raise ColunasInvalidas(f"{slot}: colunas ausentes {sorted(faltando)}")


def reingest(files: dict[str, bytes]) -> AppState:
    """Aplica um upload por cima do estado ATUAL, acumulando importações.

    Só os slots enviados são sobrescritos; os demais (imports anteriores ou seed)
    permanecem. Grava no dir de runtime efêmero — reinício do processo volta ao
    seed/vazio (ADR 0001/0002). Para reter entre reinícios, ver ADR 0010.
    """
    global _state, _runtime_dir
    for slot, raw in files.items():
        if slot not in _SLOT_ARQUIVO:
            raise ColunasInvalidas(f"slot desconhecido: {slot}")
        _valida_colunas(slot, raw)

    if _runtime_dir is None:  # garante dir de runtime (respeitando o toggle de seed)
        _runtime_dir = _novo_runtime_dir(config.DATA_DIR if config.USE_SEED_DATA else None)
    for slot, raw in files.items():  # sobrepõe só os slots enviados; retém o resto
        (_runtime_dir / _SLOT_ARQUIVO[slot]).write_bytes(raw)
    _state = _from_artefatos(build(_runtime_dir))
    return _state
