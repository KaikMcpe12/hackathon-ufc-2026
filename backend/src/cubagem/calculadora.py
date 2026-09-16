"""Agrega a cubagem por pedido: parse → cubagem por item → soma → selo."""
from __future__ import annotations

import pandas as pd

from .classificador import selo_pedido
from .conversor import cubar_item
from .parser import parse_itens_resumo


def _indices(ranking: pd.DataFrame, sinteticas: pd.DataFrame) -> tuple[dict, dict]:
    ridx = {r["Codigo"].strip(): r for _, r in ranking.iterrows()}
    sidx = (
        {r["Codigo_Produto"].strip(): r for _, r in sinteticas.iterrows()}
        if len(sinteticas) else {}
    )
    return ridx, sidx


def cubar_pedido(itens_resumo: str, ridx: dict, sidx: dict) -> dict:
    """Retorna {peso_kg, volume_m3, qualidade_cubagem, itens[]} para um pedido."""
    itens = [cubar_item(it, ridx, sidx) for it in parse_itens_resumo(itens_resumo)]
    selo = selo_pedido([c["selo_item"] for c in itens])
    if selo == "AUSENTE":
        peso = vol = float("nan")  # ausência nunca vira zero (Charter §3.2)
    else:
        peso = sum(c["peso_total_kg"] for c in itens)
        vol = sum(c["volume_total_m3"] for c in itens)
    return {"peso_kg": peso, "volume_m3": vol, "qualidade_cubagem": selo, "itens": itens}


def aplicar_cubagem(
    elegiveis: pd.DataFrame, ranking: pd.DataFrame, sinteticas: pd.DataFrame
) -> pd.DataFrame:
    """Adiciona peso_kg, volume_m3, qualidade_cubagem e itens aos elegíveis."""
    if elegiveis.empty:
        out = elegiveis.copy()
        for c in ["peso_kg", "volume_m3", "qualidade_cubagem", "itens"]:
            out[c] = pd.Series(dtype="object")
        return out
    ridx, sidx = _indices(ranking, sinteticas)
    recs = []
    for _, ped in elegiveis.iterrows():
        recs.append({**ped.to_dict(), **cubar_pedido(ped["itens_resumo"], ridx, sidx)})
    return pd.DataFrame(recs)
