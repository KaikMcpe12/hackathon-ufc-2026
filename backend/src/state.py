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


def bootstrap(data_dir: Path | None = None) -> AppState:
    """Carrega os CSVs seed e publica o estado. Chamado no startup do FastAPI.

    Resiliente: se os dados estiverem ausentes ou um CSV presente estiver corrompido,
    inicia com estado VAZIO (o usuário importa via /etl/ingest) em vez de derrubar o app.
    """
    global _state
    try:
        _state = _from_artefatos(build(data_dir or config.DATA_DIR))
    except Exception:
        logging.getLogger("nobrelog").exception("bootstrap falhou — iniciando com estado vazio")
        _state = _from_artefatos(build(Path("/nonexistent_nobrelog_data")))
    return _state


def get_state() -> AppState:
    if _state is None:
        return bootstrap()
    return _state


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
    """Substitui em memória só os arquivos enviados; demais vêm do seed atual.

    Não grava no diretório versionado — usa um dir temporário (ADR 0001/0002).
    Reinício do servidor volta ao seed de `backend/data/`.
    """
    global _state
    for slot, raw in files.items():
        if slot not in _SLOT_ARQUIVO:
            raise ColunasInvalidas(f"slot desconhecido: {slot}")
        _valida_colunas(slot, raw)

    tmp = Path(tempfile.mkdtemp(prefix="nobrelog_ingest_"))
    try:
        for arq in config.DATA_DIR.iterdir():  # base = seed atual
            if arq.is_file():
                shutil.copy(arq, tmp / arq.name)
        for slot, raw in files.items():  # sobrepõe os enviados
            (tmp / _SLOT_ARQUIVO[slot]).write_bytes(raw)
        _state = _from_artefatos(build(tmp))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return _state
