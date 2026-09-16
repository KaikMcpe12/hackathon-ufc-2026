"""Modelagem MILP (Knapsack 2D) com PuLP. Ver [[dominio/otimizacao]] e ADR 0008."""
from __future__ import annotations

import pandas as pd
import pulp


def montar(pedidos: pd.DataFrame, cap_peso: float, cap_vol: float, eps: float):
    """Monta o problema. `pedidos` indexado por pedido_id, ordenado (determinismo).

    Objetivo: 0,5·Op + 0,5·Ov + ε·(valor/valor_ref)  (desempate por valor — ADR 0008).
    Restrições hard: Σpeso·x ≤ cap_peso ; Σvol·x ≤ cap_vol.
    """
    ids = list(pedidos.index)
    peso = pedidos["peso_kg"].to_dict()
    vol = pedidos["volume_m3"].to_dict()
    valor = pedidos["valor"].to_dict()
    valor_ref = float(sum(valor.values())) or 1.0

    prob = pulp.LpProblem("nobrelog", pulp.LpMaximize)
    x = {i: pulp.LpVariable(f"x_{i}", cat="Binary") for i in ids}

    op = pulp.lpSum(peso[i] * x[i] for i in ids) / cap_peso
    ov = pulp.lpSum(vol[i] * x[i] for i in ids) / cap_vol
    val = pulp.lpSum(valor[i] * x[i] for i in ids) / valor_ref
    prob += 0.5 * op + 0.5 * ov + eps * val

    prob += pulp.lpSum(peso[i] * x[i] for i in ids) <= cap_peso
    prob += pulp.lpSum(vol[i] * x[i] for i in ids) <= cap_vol
    return prob, x
