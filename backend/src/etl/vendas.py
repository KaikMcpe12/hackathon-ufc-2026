"""Enriquecimento com o CSV de Vendas/Faturamento/Entregas (PRD-10 §2.1).

Cruza os pedidos processados com o dado bruto oficial para trazer o status REAL de
faturamento e entrega, sem alterar a elegibilidade nem a cubagem (não muda o gate).
Divergências de cidade viram anomalia sinalizada no log de qualidade.
"""
from __future__ import annotations

import re

import pandas as pd

from .log import make_correcao
from .text import norm_cidade, norm_upper

COLS_ADD = ["status_faturamento", "status_entrega", "entregue", "veiculo_historico",
            "divergencia_cidade"]


def _pid(pedido: str) -> str:
    """Chave de join: pedido sem o prefixo 'L' (semanas usam L..., vendas não)."""
    return re.sub(r"^L", "", str(pedido).strip())


def enriquecer(proc: pd.DataFrame, vendas: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    """Adiciona colunas de status e divergência. Retorna (df, correcoes_divergencia)."""
    proc = proc.copy()
    if proc.empty or vendas.empty:
        for c in COLS_ADD:
            proc[c] = None
        return proc, []

    vendas = vendas.copy()
    vendas["_pid"] = vendas["PEDIDO"].map(_pid)
    vendas = vendas.drop_duplicates(subset="_pid", keep="last").set_index("_pid")

    correcoes: list[dict] = []
    sf, se, ent, vh, dv = [], [], [], [], []
    for _, r in proc.iterrows():
        v = vendas.loc[_pid(r["pedido"])] if _pid(r["pedido"]) in vendas.index else None
        if v is None:
            sf.append(None); se.append(None); ent.append(None); vh.append(None); dv.append(None)
            continue
        sf.append(norm_upper(v.get("FATURAMENTO", "")))
        se.append(norm_upper(v.get("LOGISTICA", "")))
        ent.append(bool(str(v.get("ENTREGUE DATA", "")).strip()))
        vh.append(norm_upper(v.get("VEÍCULO", "")))
        cidade_v = norm_cidade(v.get("CIDADE", ""))
        diverge = bool(cidade_v) and cidade_v != r["cidade"]
        dv.append(diverge)
        if diverge:
            correcoes.append(make_correcao(
                r["pedido"], "cidade", r["cidade"], cidade_v,
                "cidade_divergente", "cruzamento_vendas_faturamento", "SINALIZADA"))

    proc["status_faturamento"] = sf
    proc["status_entrega"] = se
    proc["entregue"] = ent
    proc["veiculo_historico"] = vh
    proc["divergencia_cidade"] = dv
    return proc, correcoes
