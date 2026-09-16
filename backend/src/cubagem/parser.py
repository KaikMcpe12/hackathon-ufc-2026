"""Parse do `Itens_Resumo` do pedido em itens estruturados.

Formato real: itens separados por ' | '; cada item
`CODIGO - DESCRICAO (QTD UN)`. A unidade pode faltar, ex.: '(5,00)'.
"""
from __future__ import annotations

import re

from ..etl.text import parse_valor_br

ITEM_RE = re.compile(
    r"(?P<codigo>\d+)\s*-\s*(?P<descricao>.+?)\s*\((?P<qtd>[\d,\.]+)\s*(?P<un>[A-Za-z²]*)\)"
)


def parse_itens_resumo(resumo: str) -> list[dict]:
    """Retorna lista de {codigo, descricao, quantidade, unidade_venda}."""
    itens = []
    for parte in str(resumo).split(" | "):
        m = ITEM_RE.search(parte)
        if not m:
            continue
        itens.append({
            "codigo": m.group("codigo").strip(),
            "descricao": m.group("descricao").strip(),
            "quantidade": parse_valor_br(m.group("qtd")),
            "unidade_venda": (m.group("un") or "UN").upper(),
        })
    return itens
