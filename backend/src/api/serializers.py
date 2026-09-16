"""Converte linhas do estado (pandas) para os contratos JSON de [[api/contratos]]."""
from __future__ import annotations

import math

import pandas as pd

_ITEM_FIELDS = ["codigo", "descricao", "quantidade", "unidade_venda", "peso_kg_unit",
                "volume_m3_unit", "peso_total_kg", "volume_total_m3", "caixas", "dado_estimado"]
_ITEM_NUM = ["quantidade", "peso_kg_unit", "volume_m3_unit", "peso_total_kg", "volume_total_m3"]


def _num(x, nd: int | None = None):
    """NaN/None → None; senão float (arredondado se nd)."""
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return None
    return round(float(x), nd) if nd is not None else float(x)


def item_to_dict(it: dict) -> dict:
    out = {k: it.get(k) for k in _ITEM_FIELDS}
    for k in _ITEM_NUM:
        out[k] = _num(out[k])
    return out


def pedido_to_dict(row: pd.Series | dict) -> dict:
    r = row if isinstance(row, dict) else row.to_dict()
    data = r.get("data")
    itens = r.get("itens") or []
    return {
        "pedido": r["pedido"],
        "data": data.date().isoformat() if pd.notna(data) else None,
        "cidade": r["cidade"],
        "eixo_id": int(r["eixo_id"]),
        "semana": int(r["semana"]),
        "valor": _num(r.get("valor"), 2),
        "vendedor": r.get("vendedor"),
        "situacao": r.get("situacao"),
        "logistica": r.get("logistica"),
        "peso_kg": _num(r.get("peso_kg"), 3),
        "volume_m3": _num(r.get("volume_m3"), 5),
        "qualidade_cubagem": r.get("qualidade_cubagem"),
        "elegivel": True,
        "motivo_exclusao": None,
        "itens": [item_to_dict(i) for i in itens],
    }


def veiculo_to_dict(row: pd.Series) -> dict:
    return {
        "nome": row["nome"],
        "capacidade_peso": float(row["capacidade_peso"]),
        "capacidade_volume": float(row["capacidade_volume"]),
        "descricao": row["descricao"],
        "selecionavel": bool(row["selecionavel"]),
    }


def eixo_to_dict(row: pd.Series) -> dict:
    return {"id": int(row["id"]), "nome": row["nome"], "cidades": list(row["cidades"])}
