"""Classificação do selo de cubagem por pedido (🟢🟡🔴).

Definição calibrada contra o protótipo (Status_Cubagem_Prototipo):
- 🔴 AUSENTE  — algum item sem cubagem (nem ranking nem sintético).
- 🟡 ESTIMADA — algum item veio de estimativa sintética.
- 🟢 COMPLETA — todos os itens têm referência do Ranking Top 85.
"""
from __future__ import annotations

_PRIORIDADE = {"AUSENTE": 3, "ESTIMADA": 2, "COMPLETA": 1}


def selo_pedido(selos_itens: list[str]) -> str:
    """Pior selo entre os itens (🔴 > 🟡 > 🟢)."""
    if not selos_itens:
        return "AUSENTE"
    return max(selos_itens, key=lambda s: _PRIORIDADE.get(s, 3))
