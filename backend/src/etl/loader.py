"""Etapa 1 — Carregar. Lê os CSVs de pedidos (4 semanas) e o ranking."""
from __future__ import annotations

from pathlib import Path

import pandas as pd

PEDIDOS_COLS = [
    "Pedido", "Data", "Vendedor", "Situacao", "Cidade",
    "Logistica", "Situacao_CSV_Entrega", "Valor_Pedido", "Qtd_Itens", "Itens_Resumo",
]


def carregar_semana(path: Path, semana: int) -> pd.DataFrame:
    """Lê um CSV de pedidos (sep ';', UTF-8 com BOM) mantendo texto cru."""
    df = pd.read_csv(path, sep=";", dtype=str, encoding="utf-8-sig", keep_default_na=False)
    df.columns = [c.strip() for c in df.columns]
    df["semana"] = semana
    return df


RANKING_COLS = ["Rank", "Codigo", "Produto", "Pedidos", "Qtd_Entregue",
                "Unidade_Venda", "Peso_kg", "Volume_m3", "Dado_Estimado", "Fonte"]


def carregar_pedidos(data_dir: Path) -> pd.DataFrame:
    """Concatena as semanas presentes com coluna extra `semana` (1–4).

    Tolerante a arquivos ausentes: pula os que não existem. Se nenhum existir,
    retorna DataFrame vazio com as colunas esperadas (sistema inicia sem dados).
    """
    frames = []
    for n in range(1, 5):
        p = data_dir / f"pedidos_semana_{n}.csv"
        if p.exists():
            frames.append(carregar_semana(p, n))
    if not frames:
        return pd.DataFrame(columns=[*PEDIDOS_COLS, "semana"])
    return pd.concat(frames, ignore_index=True)


def carregar_ranking(data_dir: Path) -> pd.DataFrame:
    """Ranking Top 85 (sep ';', UTF-8 com BOM). Vazio (com colunas) se ausente."""
    p = data_dir / "ranking_top85.csv"
    if not p.exists():
        return pd.DataFrame(columns=RANKING_COLS)
    df = pd.read_csv(p, sep=";", dtype=str, encoding="utf-8-sig", keep_default_na=False)
    df.columns = [c.strip() for c in df.columns]
    return df


def carregar_vendas(data_dir: Path) -> pd.DataFrame:
    """Vendas/Faturamento/Entregas (sep ','). Auditoria/enriquecimento — opcional."""
    p = data_dir / "vendas_faturamento.csv"
    if not p.exists():
        return pd.DataFrame()
    df = pd.read_csv(p, sep=",", dtype=str, encoding="utf-8-sig", keep_default_na=False)
    df.columns = [c.strip() for c in df.columns]
    return df


def carregar_referencias_sinteticas(data_dir: Path) -> pd.DataFrame:
    """Estimativas sintéticas do protótipo (opcional). Vazio se ausente."""
    p = data_dir / "referencias_sinteticas.csv"
    if not p.exists():
        return pd.DataFrame()
    df = pd.read_csv(p, sep=";", dtype=str, encoding="utf-8-sig", keep_default_na=False)
    df.columns = [c.strip() for c in df.columns]
    return df
