"""Monta o PlanoDeCarga: seleciona pedidos, calcula totais, gargalo, LIFO, rejeições."""
from __future__ import annotations

import math
from datetime import date, datetime, timezone

import pandas as pd

from .. import config
from .explicabilidade import motivo_rejeicao
from .gargalo import diagnosticar
from .organizacao import organizar_carga
from .solver import resolver


class CenarioInvalido(Exception):
    """Sem pedidos elegíveis ou veículo não selecionável."""


def _num(x, nd):
    if x is None or (isinstance(x, float) and math.isnan(x)):
        return None
    return round(float(x), nd)


def _item_publico(it: dict) -> dict:
    """Projeção pública de um item para o PlanoDeCarga (produtos do pedido)."""
    return {
        "codigo": it.get("codigo"),
        "descricao": it.get("descricao"),
        "quantidade": _num(it.get("quantidade"), 2),
        "unidade_venda": it.get("unidade_venda"),
        "caixas": it.get("caixas"),
        "peso_total_kg": _num(it.get("peso_total_kg"), 3),
        "volume_total_m3": _num(it.get("volume_total_m3"), 5),
        "dado_estimado": bool(it.get("dado_estimado")),
    }


def _pool(state, eixo_id: int, semana: int | None, incluir_estimadas: bool) -> pd.DataFrame:
    proc = state.pedidos_processados
    pool = proc[proc["eixo_id"] == eixo_id]
    if semana is not None:
        pool = pool[pool["semana"] == semana]
    pool = pool[pool["qualidade_cubagem"] != "AUSENTE"]
    if not incluir_estimadas:
        pool = pool[pool["qualidade_cubagem"] == "COMPLETA"]
    pool = pool.dropna(subset=["peso_kg", "volume_m3"])
    return pool.set_index("pedido")


def otimizar_cenario(
    state, eixo_id: int, veiculo_nome: str, semana: int | None = None,
    incluir_estimadas: bool = True, data_carga: date | None = None,
) -> dict:
    """Retorna um PlanoDeCarga (dict) para 1 eixo + 1 veículo.

    `semana=None` usa todos os pedidos do eixo (comportamento do protótipo/gate).
    """
    veic = state.veiculos[state.veiculos["nome"] == veiculo_nome]
    if veic.empty:
        raise CenarioInvalido(f"Veículo desconhecido: {veiculo_nome!r}")
    veic = veic.iloc[0]
    if not bool(veic["selecionavel"]):
        raise CenarioInvalido(f"Veículo fora do escopo da otimização: {veiculo_nome!r}")
    cap_peso = float(veic["capacidade_peso"])
    cap_vol = float(veic["capacidade_volume"])

    eixo_sel = state.eixos[state.eixos["id"] == eixo_id]
    if eixo_sel.empty:
        raise CenarioInvalido(f"Eixo {eixo_id} não encontrado. Importe os dados de rotas.")
    eixo = eixo_sel.iloc[0]
    ordem_cidade = {c: i for i, c in enumerate(eixo["cidades"])}

    pool = _pool(state, eixo_id, semana, incluir_estimadas)
    if pool.empty:
        raise CenarioInvalido("Sem pedidos elegíveis para o cenário.")

    sel = resolver(pool, cap_peso, cap_vol)
    escolhidos = [i for i, v in sel.items() if v == 1]

    peso_util = float(pool.loc[escolhidos, "peso_kg"].sum())
    vol_util = float(pool.loc[escolhidos, "volume_m3"].sum())
    valor_total = float(pool.loc[escolhidos, "valor"].sum())
    ocup_peso = peso_util / cap_peso
    ocup_vol = vol_util / cap_vol
    violacoes = int(peso_util > cap_peso + 1e-6) + int(vol_util > cap_vol + 1e-6)

    def chave(pid):
        return (ordem_cidade.get(pool.loc[pid, "cidade"], 999), pid)

    selecionados = []
    for ordem, pid in enumerate(sorted(escolhidos, key=chave), start=1):
        r = pool.loc[pid]
        itens = r["itens"] if isinstance(r["itens"], list) else []
        selecionados.append({
            "ordem": ordem, "pedido": pid, "cidade": r["cidade"],
            "valor": round(float(r["valor"]), 2),
            "peso_kg": round(float(r["peso_kg"]), 3),
            "volume_m3": round(float(r["volume_m3"]), 5),
            "qtd_itens": len(itens),
            "itens": [_item_publico(it) for it in itens],
        })

    rejeitados = []
    for pid in pool.index:
        if pid in escolhidos:
            continue
        r = pool.loc[pid]
        rejeitados.append({
            "pedido": pid, "cidade": r["cidade"],
            "peso_kg": round(float(r["peso_kg"]), 3),
            "volume_m3": round(float(r["volume_m3"]), 5),
            "motivo": motivo_rejeicao(float(r["peso_kg"]), float(r["volume_m3"]),
                                      peso_util, vol_util, cap_peso, cap_vol),
        })

    # sequência de descarga: todas as cidades do eixo, com contagem (inclui zeradas)
    cont = {c: 0 for c in eixo["cidades"]}
    for s in selecionados:
        cont[s["cidade"]] = cont.get(s["cidade"], 0) + 1
    sequencia = [{"ordem": i + 1, "cidade": c, "qtd_pedidos": cont[c]}
                 for i, c in enumerate(eixo["cidades"])]
    cidades_com_pedido = [c for c in eixo["cidades"] if cont[c] > 0]
    inversa = [c.title() for c in reversed(cidades_com_pedido)]
    descricao = ("Carregue primeiro os pedidos de " + ", depois ".join(inversa) + "."
                 if inversa else "Sem pedidos para carregar.")

    gargalo = diagnosticar(ocup_peso, ocup_vol)
    organizacao = organizar_carga(selecionados, sequencia, cap_peso, cap_vol,
                                  ocup_peso, ocup_vol, gargalo)

    return {
        "id": f"plano_e{eixo_id}_{veiculo_nome.replace(' ', '').replace('/', '').lower()}",
        "eixo": {"id": int(eixo["id"]), "nome": eixo["nome"], "cidades": list(eixo["cidades"])},
        "veiculo": {"nome": veic["nome"], "capacidade_peso": cap_peso,
                    "capacidade_volume": cap_vol, "descricao": veic["descricao"],
                    "selecionavel": bool(veic["selecionavel"])},
        "semana": semana,
        "data_carga": (data_carga or date.today()).isoformat(),
        "totais": {
            "peso_utilizado": round(peso_util, 3), "peso_capacidade": cap_peso,
            "ocupacao_peso": round(ocup_peso, 4),
            "volume_utilizado": round(vol_util, 4), "volume_capacidade": cap_vol,
            "ocupacao_volume": round(ocup_vol, 4),
            "valor_total": round(valor_total, 2), "quantidade_pedidos": len(escolhidos),
        },
        "gargalo": gargalo,
        "violacoes": violacoes,
        "pedidos_selecionados": selecionados,
        "pedidos_rejeitados": rejeitados,
        "sequencia_descarga": sequencia,
        "orientacao_carregamento": {"modo": "LIFO", "descricao": descricao},
        "organizacao_carga": organizacao,
        "gerado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
