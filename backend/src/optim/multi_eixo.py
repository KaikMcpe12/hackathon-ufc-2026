"""Otimização multi-eixo (desafio bônus). Ver PRD-10 §2.2.

Fase A: designa cada veículo da frota ao eixo de melhor encaixe (designacao.py).
Fase B: resolve cada par (eixo, veículo) com o solver mono-eixo existente.
Pedidos permanecem atômicos e cada veículo atende no máximo 1 eixo.
"""
from __future__ import annotations

from datetime import date, datetime, timezone

from .designacao import designar
from .planejador import CenarioInvalido, otimizar_cenario


def _frota(state, veiculos: list[str] | None) -> list[dict]:
    if veiculos:
        frota = []
        for nome in veiculos:
            row = state.veiculos[state.veiculos["nome"] == nome]
            if row.empty or not bool(row.iloc[0]["selecionavel"]):
                raise CenarioInvalido(f"Veículo inválido/não selecionável: {nome!r}")
            r = row.iloc[0]
            frota.append({"nome": r["nome"], "capacidade_peso": float(r["capacidade_peso"]),
                          "capacidade_volume": float(r["capacidade_volume"])})
        return frota
    return [{"nome": r["nome"], "capacidade_peso": float(r["capacidade_peso"]),
             "capacidade_volume": float(r["capacidade_volume"])}
            for _, r in state.veiculos[state.veiculos["selecionavel"]].iterrows()]


def _demanda(state, semana: int | None, incluir_estimadas: bool) -> dict[int, tuple[float, float]]:
    proc = state.pedidos_processados
    demanda: dict[int, tuple[float, float]] = {}
    for eid in sorted(int(e) for e in state.eixos["id"].tolist()):
        pool = proc[(proc["eixo_id"] == eid) & (proc["qualidade_cubagem"] != "AUSENTE")]
        if semana is not None:
            pool = pool[pool["semana"] == semana]
        if not incluir_estimadas:
            pool = pool[pool["qualidade_cubagem"] == "COMPLETA"]
        pool = pool.dropna(subset=["peso_kg", "volume_m3"])
        demanda[eid] = (float(pool["peso_kg"].sum()), float(pool["volume_m3"].sum()))
    return demanda


def otimizar_multi(
    state, semana: int | None = None, veiculos: list[str] | None = None,
    incluir_estimadas: bool = True, data_carga: date | None = None,
) -> dict:
    """Retorna {planos[], resumo_global, designacao, gerado_em}."""
    frota = _frota(state, veiculos)
    if not frota:
        raise CenarioInvalido("Sem veículos selecionáveis.")
    demanda = _demanda(state, semana, incluir_estimadas)
    if not demanda:
        raise CenarioInvalido("Sem eixos/dados. Importe os dados.")

    atrib = designar(demanda, frota)  # {eixo_id: slot}

    planos = []
    op = ov = valor = 0.0
    for eid, slot in sorted(atrib.items()):
        try:
            plano = otimizar_cenario(state, eid, frota[slot]["nome"], semana,
                                     incluir_estimadas, data_carga)
        except CenarioInvalido:
            continue  # eixo sem pedidos → veículo fica ocioso
        if plano["totais"]["quantidade_pedidos"] == 0:
            continue
        planos.append({"eixo_id": eid, "veiculo": frota[slot]["nome"], "plano": plano})
        op += plano["totais"]["ocupacao_peso"]
        ov += plano["totais"]["ocupacao_volume"]
        valor += plano["totais"]["valor_total"]

    n = len(planos)
    todos = {int(e) for e in state.eixos["id"].tolist()}
    atendidos = {p["eixo_id"] for p in planos}
    resumo = {
        "ocupacao_media_peso": round(op / n, 4) if n else 0.0,
        "ocupacao_media_volume": round(ov / n, 4) if n else 0.0,
        "valor_total": round(valor, 2),
        "veiculos_usados": n,
        "veiculos_ociosos": len(frota) - n,
        "eixos_atendidos": sorted(atendidos),
        "eixos_nao_atendidos": sorted(todos - atendidos),
    }
    return {
        "planos": planos,
        "resumo_global": resumo,
        "designacao": "GULOSA_2OPT",
        "gerado_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
