"""Designação veículo → eixo (heurística gulosa + busca local 2-opt). Ver PRD-10 §2.2.

Funções puras: recebem a demanda por eixo e a frota (slots), devolvem a atribuição.
"""
from __future__ import annotations


def fit_score(peso: float, vol: float, cap_peso: float, cap_vol: float) -> float:
    """Quanto da capacidade do veículo o eixo preencheria (0..1). Maior = melhor encaixe."""
    fp = min(1.0, peso / cap_peso) if cap_peso else 0.0
    fv = min(1.0, vol / cap_vol) if cap_vol else 0.0
    return 0.5 * fp + 0.5 * fv


def _total_fit(atrib: dict[int, int], demanda: dict[int, tuple[float, float]], frota: list[dict]) -> float:
    tot = 0.0
    for e, s in atrib.items():
        p, v = demanda[e]
        tot += fit_score(p, v, frota[s]["capacidade_peso"], frota[s]["capacidade_volume"])
    return tot


def _dois_opt(atrib: dict[int, int], demanda: dict, frota: list[dict]) -> dict[int, int]:
    """Troca designações de 2 eixos enquanto melhorar o fit global (determinístico)."""
    melhor = dict(atrib)
    eixos = sorted(atrib)
    improved = True
    while improved:
        improved = False
        for i in range(len(eixos)):
            for j in range(i + 1, len(eixos)):
                e1, e2 = eixos[i], eixos[j]
                cand = dict(melhor)
                cand[e1], cand[e2] = melhor[e2], melhor[e1]
                if _total_fit(cand, demanda, frota) > _total_fit(melhor, demanda, frota) + 1e-9:
                    melhor = cand
                    improved = True
    return melhor


def designar(demanda: dict[int, tuple[float, float]], frota: list[dict]) -> dict[int, int]:
    """demanda: {eixo_id: (peso, vol)} · frota: lista de slots {capacidade_peso, capacidade_volume}.

    Retorna {eixo_id: indice_slot}. Cada eixo recebe ≤1 veículo e cada veículo 1 eixo.
    """
    pares = []
    for e, (p, v) in demanda.items():
        for s, veic in enumerate(frota):
            pares.append((fit_score(p, v, veic["capacidade_peso"], veic["capacidade_volume"]), e, s))
    pares.sort(key=lambda x: (-x[0], x[1], x[2]))  # fit desc, depois estável

    atrib: dict[int, int] = {}
    usados_e: set[int] = set()
    usados_s: set[int] = set()
    for _, e, s in pares:
        if e in usados_e or s in usados_s:
            continue
        atrib[e] = s
        usados_e.add(e)
        usados_s.add(s)
    return _dois_opt(atrib, demanda, frota)
