"""Etapa 2/4 — Normalizar e corrigir campos dos pedidos."""
from __future__ import annotations

import pandas as pd

from .. import config
from .log import make_correcao
from .text import norm_cidade, norm_upper, parse_data_br, parse_valor_br

# Correções de cidade conhecidas (typos do protótipo). Chave normalizada -> destino.
CITY_TYPOS = {
    "IPAPORAGA": "IPAPORANGA",
}

NORM_COLS = ["pedido", "data", "cidade", "cidade_original", "vendedor", "situacao",
             "logistica", "situacao_csv_entrega", "valor", "qtd_itens", "itens_resumo", "semana"]


def normalizar(df: pd.DataFrame) -> tuple[pd.DataFrame, list[dict]]:
    """Retorna (df_normalizado, correcoes). Não filtra — só limpa e registra."""
    correcoes: list[dict] = []
    rows = []
    for _, r in df.iterrows():
        pedido = r["Pedido"].strip()

        # cidade
        cidade_raw = r["Cidade"]
        cidade = norm_cidade(cidade_raw)
        if isinstance(cidade_raw, str) and cidade_raw != cidade_raw.strip():
            correcoes.append(make_correcao(
                pedido, "cidade", cidade_raw, cidade,
                "cidade_trailing_space", "strip_espacos", "PADRONIZADA"))
        if cidade in CITY_TYPOS:
            novo = CITY_TYPOS[cidade]
            correcoes.append(make_correcao(
                pedido, "cidade", cidade, novo,
                "cidade_typo", "dicionario_controlado", "PADRONIZADA"))
            cidade = novo

        # data
        data, regra_data = parse_data_br(r["Data"], config.LOTE_ANO)
        if regra_data:
            correcoes.append(make_correcao(
                pedido, "data", r["Data"], data.date().isoformat(),
                regra_data, f"lote_ano_{config.LOTE_ANO}", "CORRIGIDA"))

        rows.append({
            "pedido": pedido,
            "data": data,
            "cidade": cidade,
            "cidade_original": cidade_raw.strip() if isinstance(cidade_raw, str) else "",
            "vendedor": norm_upper(r["Vendedor"]),
            "situacao": norm_upper(r["Situacao"]),
            "logistica": norm_upper(r["Logistica"]),
            "situacao_csv_entrega": norm_upper(r["Situacao_CSV_Entrega"]),
            "valor": parse_valor_br(r["Valor_Pedido"]),
            "qtd_itens": r["Qtd_Itens"],
            "itens_resumo": r["Itens_Resumo"],
            "semana": int(r["semana"]),
        })
    return pd.DataFrame(rows, columns=NORM_COLS), correcoes
