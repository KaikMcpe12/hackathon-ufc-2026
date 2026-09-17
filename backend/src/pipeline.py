"""Pipeline completo: ETL → cubagem → estatísticas de qualidade."""
from __future__ import annotations

from pathlib import Path

from .cubagem.calculadora import aplicar_cubagem
from .etl.loader import carregar_vendas
from .etl.pipeline import rodar_etl
from .etl.vendas import enriquecer


def build(data_dir: Path) -> dict:
    """Roda o pipeline inteiro e devolve os artefatos para o AppState."""
    etl = rodar_etl(data_dir)
    processados = aplicar_cubagem(etl["elegiveis"], etl["ranking"], etl["referencias_sinteticas"])

    # Enriquecimento com Vendas/Faturamento (não altera elegibilidade/cubagem/gate).
    processados, correcoes_div = enriquecer(processados, carregar_vendas(data_dir))
    correcoes = etl["correcoes"] + correcoes_div

    selos = processados["qualidade_cubagem"].value_counts().to_dict()
    stats = {
        "registros_processados": etl["n_registros"],
        "pos_situacao": etl["checkpoints"]["pos_situacao"],
        "elegiveis": int(etl["checkpoints"]["com_eixo"]),
        "materiais_ranking": len(etl["ranking"]),
        "pedidos_completa": int(selos.get("COMPLETA", 0)),
        "pedidos_estimada": int(selos.get("ESTIMADA", 0)),
        "pedidos_ausente": int(selos.get("AUSENTE", 0)),
        "inconsistencias_detectadas": len(correcoes),
        "divergencias_cidade": int(processados["divergencia_cidade"].eq(True).sum())
        if "divergencia_cidade" in processados else 0,
    }
    # estágios do pipeline para o dashboard (688 → 93 → 81 → cubagem)
    n = etl["n_registros"]
    def pct(x): return round(100 * x / n, 1) if n else 0.0
    stats["pipeline_stages"] = [
        {"nome": "Importacao", "registros": n, "percentual": 100.0},
        {"nome": "Situacao", "registros": etl["checkpoints"]["pos_situacao"],
         "percentual": pct(etl["checkpoints"]["pos_situacao"])},
        {"nome": "Eixo", "registros": etl["checkpoints"]["com_eixo"],
         "percentual": pct(etl["checkpoints"]["com_eixo"])},
        {"nome": "Cubagem", "registros": stats["pedidos_completa"] + stats["pedidos_estimada"],
         "percentual": pct(stats["pedidos_completa"] + stats["pedidos_estimada"])},
    ]

    return {
        "pedidos_raw": etl["pedidos_raw"],
        "pedidos_processados": processados,
        "ranking": etl["ranking"],
        "referencias_sinteticas": etl["referencias_sinteticas"],
        "veiculos": etl["veiculos"],
        "eixos": etl["eixos"],
        "log_correcoes": correcoes,
        "motivos_exclusao": etl["motivos_exclusao"],
        "stats": stats,
    }
