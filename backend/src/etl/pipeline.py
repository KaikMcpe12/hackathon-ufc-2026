"""Orquestra o pipeline ETL (etapas 1–4). Cubagem entra em cubagem/pipeline."""
from __future__ import annotations

from pathlib import Path

from .filters import filtrar
from .loader import carregar_pedidos, carregar_ranking, carregar_referencias_sinteticas
from .normalizer import normalizar
from .rotas import parse_eixos, parse_veiculos


def rodar_etl(data_dir: Path) -> dict:
    """Carrega, normaliza e filtra. Retorna dict com dataframes e metadados."""
    raw = carregar_pedidos(data_dir)
    eixos = parse_eixos(data_dir)
    veiculos = parse_veiculos(data_dir)
    ranking = carregar_ranking(data_dir)
    sinteticas = carregar_referencias_sinteticas(data_dir)

    norm, correcoes = normalizar(raw)
    elegiveis, motivos, excluidos, checkpoints = filtrar(norm, eixos)

    return {
        "pedidos_raw": raw,
        "eixos": eixos,
        "veiculos": veiculos,
        "ranking": ranking,
        "referencias_sinteticas": sinteticas,
        "elegiveis": elegiveis,
        "excluidos": excluidos,
        "correcoes": correcoes,
        "motivos_exclusao": motivos,
        "checkpoints": checkpoints,
        "n_registros": len(raw),
    }
