"""Plano de organização de carga: zonas (fundo→porta) por rota LIFO + densidade.

Mantém pedidos atômicos (não divide). Objetivo: eficiência de descarga (LIFO pela
rota do eixo) + melhor arrumação física (densos/pesados na base) + perfil de densidade
(kg/m³) para orientar o encaixe de cargas densas com leves.
"""
from __future__ import annotations

from .. import config


def _dens(peso: float | None, vol: float | None) -> float | None:
    if not peso or not vol or vol <= 0:
        return None
    return round(peso / vol, 1)


def _posicao(i: int, n: int) -> str:
    if n == 1:
        return "Fundo → Porta"
    if i == 0:
        return "Fundo"
    if i == n - 1:
        return "Porta"
    return "Meio"


def organizar_carga(
    selecionados: list[dict], sequencia_descarga: list[dict],
    cap_peso: float, cap_vol: float, ocup_peso: float, ocup_vol: float, gargalo: str,
) -> dict:
    """Constrói a estrutura de organização da carga a partir dos pedidos selecionados."""
    # ordem de entrega = cidades do eixo com pedido (ordem asc); LIFO = inverso
    cidades_entrega = [s["cidade"] for s in sequencia_descarga if s["qtd_pedidos"] > 0]
    ordem_carregamento = list(reversed(cidades_entrega))

    zonas = []
    n = len(ordem_carregamento)
    for i, cidade in enumerate(ordem_carregamento):
        peds = [p for p in selecionados if p["cidade"] == cidade]
        # densos/pesados primeiro (base da zona)
        peds = sorted(peds, key=lambda p: _dens(p["peso_kg"], p["volume_m3"]) or 0, reverse=True)
        peso_z = round(sum(p["peso_kg"] or 0 for p in peds), 3)
        vol_z = round(sum(p["volume_m3"] or 0 for p in peds), 5)
        pedidos_zona = []
        for p in peds:
            itens = sorted(p.get("itens", []), key=lambda it: it.get("peso_total_kg") or 0, reverse=True)
            pedidos_zona.append({
                "pedido": p["pedido"],
                "peso_kg": p["peso_kg"], "volume_m3": p["volume_m3"],
                "densidade": _dens(p["peso_kg"], p["volume_m3"]),
                "itens_base": [it["descricao"] for it in itens[:2]],  # itens mais pesados (na base)
            })
        zonas.append({
            "ordem": i + 1, "posicao": _posicao(i, n), "cidade": cidade,
            "qtd_pedidos": len(peds), "peso_kg": peso_z, "volume_m3": vol_z,
            "densidade": _dens(peso_z, vol_z), "pedidos": pedidos_zona,
        })

    peso_util = sum(p["peso_kg"] or 0 for p in selecionados)
    vol_util = sum(p["volume_m3"] or 0 for p in selecionados)
    dens_carga = _dens(peso_util, vol_util)
    dens_veic = _dens(cap_peso, cap_vol)

    if gargalo == "PESO":
        perfil = "DENSA — limitada por peso"
        sugestao = "Sobra volume: encaixe pedidos leves/volumosos (baixa densidade) para preencher o espaço."
    else:
        perfil = "VOLUMOSA — limitada por volume"
        sugestao = "Sobra peso: encaixe pedidos densos/pesados (alta densidade) para aproveitar a capacidade."

    ocup_gargalo = round(max(ocup_peso, ocup_vol), 4)
    abaixo = ocup_gargalo < config.OCUPACAO_MINIMA

    return {
        "densidade_carga": dens_carga,
        "densidade_veiculo": dens_veic,
        "perfil": perfil,
        "sugestao": sugestao,
        "ocupacao_gargalo": ocup_gargalo,
        "ocupacao_minima": config.OCUPACAO_MINIMA,
        "abaixo_minimo": abaixo,
        "alerta_minimo": (
            f"Ocupação de {ocup_gargalo*100:.1f}% no gargalo ({gargalo}) abaixo do mínimo "
            f"de {config.OCUPACAO_MINIMA*100:.0f}% — avaliar se compensa o frete."
            if abaixo else None
        ),
        "zonas": zonas,
    }
