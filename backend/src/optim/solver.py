"""Resolve o MILP com CBC de forma determinística."""
from __future__ import annotations

import pandas as pd
import pulp

from .. import config
from .modelo import montar


def resolver(
    pedidos: pd.DataFrame, cap_peso: float, cap_vol: float,
    eps: float = config.DESEMPATE_EPSILON, time_limit: int = config.SOLVER_TIME_LIMIT,
) -> dict[str, int]:
    """Retorna {pedido_id: 0|1}. Ordena por índice para reproduzibilidade."""
    pedidos = pedidos.sort_index()
    prob, x = montar(pedidos, cap_peso, cap_vol, eps)
    prob.solve(pulp.PULP_CBC_CMD(msg=False, timeLimit=time_limit))
    return {i: int(round(pulp.value(x[i]) or 0)) for i in x}
