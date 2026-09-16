"""Cubagem de um item: cruza com Ranking (real) ou referências sintéticas.

Regras validadas contra o protótipo (etapa4b):
- Item de ranking vendido em m² (unidade_venda com 'm²') e pedido em MT →
  caixas = ceil(qtd_m² / m²_por_caixa); peso/volume = caixas × valor_por_caixa.
- Item de ranking em unidade direta → qtd × valor_por_unidade.
- Item sintético → qtd × (valor_exemplo / quantidade_exemplo) [taxa por unidade, m² contínuo].
- Faixa de peso → valor maior (conservador).
"""
from __future__ import annotations

import math
import re

from ..etl.text import parse_faixa_maior, parse_valor_br

M2_RE = re.compile(r"([\d]+[.,]?[\d]*)\s*m²", re.IGNORECASE)
_UN_AREA = {"MT", "M2", "M²"}


def m2_por_caixa(unidade_venda: str) -> float | None:
    """Extrai m² por caixa de 'Caixa 2,30 m²' / 'Caixa (3 peças = 2,18 m²)'."""
    m = M2_RE.search(unidade_venda or "")
    return parse_valor_br(m.group(1)) if m else None


def cubar_item(item: dict, ranking_idx: dict, sint_idx: dict) -> dict:
    """Enriquece o item com peso/volume físicos e metadados de fonte/selo.

    ranking_idx: codigo -> row (Series). sint_idx: codigo -> row (Series).
    Retorna dict no formato do schema Item + campos internos (fonte, selo_item).
    """
    cod = item["codigo"]
    qtd = item["quantidade"]
    un = item["unidade_venda"].upper()
    base = {**item, "peso_kg_unit": float("nan"), "volume_m3_unit": float("nan"),
            "peso_total_kg": float("nan"), "volume_total_m3": float("nan"),
            "caixas": None, "dado_estimado": True, "fonte": None, "selo_item": "AUSENTE"}

    if cod in ranking_idx:
        row = ranking_idx[cod]
        peso_u = parse_faixa_maior(row["Peso_kg"])
        vol_u = parse_faixa_maior(row["Volume_m3"])
        m2pc = m2_por_caixa(row["Unidade_Venda"])
        estimado = str(row.get("Dado_Estimado", "")).strip().upper() == "SIM"
        if m2pc and un in _UN_AREA:
            caixas = math.ceil(qtd / m2pc)
            peso_total, vol_total = caixas * peso_u, caixas * vol_u
        else:
            caixas = None
            peso_total, vol_total = qtd * peso_u, qtd * vol_u
        base.update(peso_kg_unit=peso_u, volume_m3_unit=vol_u,
                    peso_total_kg=peso_total, volume_total_m3=vol_total,
                    caixas=caixas, dado_estimado=estimado,
                    fonte=str(row.get("Fonte", "ranking")), selo_item="COMPLETA")
        return base

    if cod in sint_idx:
        row = sint_idx[cod]
        qex = float(row["Quantidade_Exemplo"])
        taxa_p = float(row["Peso_Item_Exemplo_kg"]) / qex
        taxa_v = float(row["Volume_Item_Exemplo_m3"]) / qex
        base.update(peso_kg_unit=taxa_p, volume_m3_unit=taxa_v,
                    peso_total_kg=qtd * taxa_p, volume_total_m3=qtd * taxa_v,
                    caixas=None, dado_estimado=True,
                    fonte=f"sintetico:{row.get('Base_Estimativa', '')}", selo_item="ESTIMADA")
        return base

    return base  # AUSENTE — peso/volume NaN (nunca zero — Charter §3.2)
