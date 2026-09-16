"""Etapa 3 — Filtrar (elegibilidade). Ordem fixa, contagem por motivo (PRD-00 I8)."""
from __future__ import annotations

import pandas as pd


def mapa_cidade_eixo(eixos: pd.DataFrame) -> dict[str, int]:
    """cidade normalizada -> eixo_id. Cidades compostas do eixo entram individualmente."""
    m: dict[str, int] = {}
    for _, e in eixos.iterrows():
        for cidade in e["cidades"]:
            m.setdefault(cidade, int(e["id"]))
    return m


def filtrar(
    df: pd.DataFrame, eixos: pd.DataFrame
) -> tuple[pd.DataFrame, list[dict], pd.DataFrame, dict[str, int]]:
    """Aplica os 4 filtros na ordem canônica.

    Retorna (elegiveis, motivos[{codigo,motivo,total,percentual}], excluidos[+motivo],
    checkpoints{importacao,pos_situacao,com_eixo}). O pipeline é 688 → 93 (pós-situação)
    → 81 (com eixo). Um pedido é contabilizado pelo PRIMEIRO motivo na ordem.
    """
    cidade_eixo = mapa_cidade_eixo(eixos)
    df = df.copy()
    df["eixo_id"] = df["cidade"].map(cidade_eixo)

    total = len(df)
    restante = df
    excluidos = []
    contagem: list[tuple[str, str, int]] = []  # (codigo, rotulo, n)
    checkpoints: dict[str, int] = {"importacao": total}

    def aplica(mask_excluir: pd.Series, codigo: str, rotulo: str):
        nonlocal restante
        fora = restante[mask_excluir]
        for _, r in fora.iterrows():
            row = r.to_dict()
            row["motivo"] = rotulo
            row["motivo_codigo"] = codigo
            excluidos.append(row)
        contagem.append((codigo, rotulo, len(fora)))
        restante = restante[~mask_excluir]

    aplica(restante["situacao"].str.contains("CANCELADO", na=False),
           "CANCELADO", "Cancelado")
    aplica(restante["situacao_csv_entrega"].eq("RETIRADA"),
           "RETIRADA_BALCAO", "Retirada no balcão")
    aplica(restante["cidade"].isin(["CRATEUS"]),
           "CRATEUS", "Crateús")
    # checkpoint "pós-situação" = os 93 do pitch (688 → 93)
    checkpoints["pos_situacao"] = len(restante)
    aplica(restante["eixo_id"].isna(),
           "CIDADE_FORA_EIXO", "Cidade fora dos eixos")
    checkpoints["com_eixo"] = len(restante)  # = 81, pool do solver

    total_excluidos = total - len(restante)
    motivos = [
        {
            "codigo": cod,
            "motivo": rot,
            "total": n,
            "percentual": round(100 * n / total_excluidos, 1) if total_excluidos else 0.0,
        }
        for cod, rot, n in contagem
    ]
    elegiveis = restante.copy()
    elegiveis["eixo_id"] = elegiveis["eixo_id"].astype(int)
    return elegiveis, motivos, pd.DataFrame(excluidos), checkpoints
