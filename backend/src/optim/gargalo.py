"""Diagnóstico do gargalo (PESO vs VOLUME)."""
from __future__ import annotations


def diagnosticar(ocupacao_peso: float, ocupacao_volume: float) -> str:
    return "PESO" if ocupacao_peso > ocupacao_volume else "VOLUME"
