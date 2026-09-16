"""Deriva `eixos` e `veiculos` do CSV ROTAS E COLETAS (semi-estruturado).

Não existe `eixos.csv` de entrada (ver PRD-00 B2): os eixos são derivados aqui.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

from .text import norm_cidade, parse_valor_br

# Ordem das colunas de valor por rota: eixos 1..5 e depois Crateús.
_EIXO_NOME_CURTO = 3  # nº de cidades usadas no rótulo "A → B → C"


def _raw(data_dir: Path) -> pd.DataFrame | None:
    p = data_dir / "rotas_coletas.csv"
    if not p.exists():
        return None
    return pd.read_csv(p, sep=",", header=None, dtype=str,
                       encoding="utf-8-sig", keep_default_na=False)


def parse_eixos(data_dir: Path) -> pd.DataFrame:
    """DataFrame com colunas: id, nome, cidades. Vazio se rotas ausente/ilegível."""
    raw = _raw(data_dir)
    if raw is None:
        return pd.DataFrame(columns=["id", "nome", "cidades"])
    try:
        return _parse_eixos(raw)
    except (ValueError, IndexError, KeyError):
        return pd.DataFrame(columns=["id", "nome", "cidades"])


def _parse_eixos(raw: pd.DataFrame) -> pd.DataFrame:
    # localizar a coluna/linha do cabeçalho "VALOR DOS PEDIDOS POR ROTA"
    header_pos = None
    for i in range(len(raw)):
        for j in range(raw.shape[1]):
            if "VALOR DOS PEDIDOS POR ROTA" in raw.iat[i, j].upper():
                header_pos = (i, j)
                break
        if header_pos:
            break
    if not header_pos:
        raise ValueError("Cabeçalho de rotas não encontrado no CSV de rotas.")
    hi, hj = header_pos
    city_row = raw.iloc[hi + 1]  # linha com as listas de cidades por eixo
    eixos = []
    for k in range(5):  # eixos 1..5
        cell = city_row.iat[hj + k]
        cidades = [norm_cidade(c) for c in cell.split(" - ") if c.strip()]
        if not cidades:
            continue
        titulo = [c.title() for c in cidades[:_EIXO_NOME_CURTO]]
        nome = " → ".join(titulo)
        eixos.append({"id": k + 1, "nome": nome, "cidades": cidades})
    return pd.DataFrame(eixos)


_VEIC_COLS = ["nome", "capacidade_peso", "capacidade_volume", "descricao", "selecionavel"]


def parse_veiculos(data_dir: Path) -> pd.DataFrame:
    """DataFrame de veículos. Vazio (com colunas) se rotas ausente/ilegível."""
    raw = _raw(data_dir)
    if raw is None:
        return pd.DataFrame(columns=_VEIC_COLS)
    try:
        return _parse_veiculos(raw)
    except (ValueError, IndexError, KeyError):
        return pd.DataFrame(columns=_VEIC_COLS)


def _parse_veiculos(raw: pd.DataFrame) -> pd.DataFrame:
    cap_i = None
    for i in range(len(raw)):
        joined = " ".join(raw.iloc[i].tolist()).upper()
        if "CAPACIDADE UTILIZADA" in joined:
            cap_i = i
            break
    if cap_i is None:
        raise ValueError("Bloco de capacidades não encontrado no CSV de rotas.")
    header = raw.iloc[cap_i]
    # coluna onde começam os nomes de veículo (após a célula "Capacidade utilizada")
    start_j = None
    for j in range(raw.shape[1]):
        if "CAPACIDADE UTILIZADA" in header.iat[j].upper():
            start_j = j + 1
            break
    peso_row = raw.iloc[cap_i + 1]
    vol_row = raw.iloc[cap_i + 2]

    descricoes = {
        "HR / BONGO": "Utilitário leve (eixos curtos, cargas pequenas)",
        "ACELLO 815": "Caminhão médio (ideal para eixos longos)",
        "MOTOS": "Moto — atende só Crateús urbano (fora do escopo da otimização)",
    }
    veiculos = []
    for j in range(start_j, raw.shape[1]):
        nome = header.iat[j].strip()
        if not nome:
            continue
        cap_peso = parse_valor_br(peso_row.iat[j])
        cap_vol = parse_valor_br(vol_row.iat[j])
        if cap_peso != cap_peso:  # NaN → coluna vazia
            continue
        veiculos.append({
            "nome": nome,
            "capacidade_peso": cap_peso,
            "capacidade_volume": cap_vol,
            "descricao": descricoes.get(nome, ""),
            "selecionavel": nome.upper() != "MOTOS",  # PRD-00 I3
        })
    return pd.DataFrame(veiculos)
