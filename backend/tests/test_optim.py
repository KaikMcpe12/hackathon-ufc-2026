import pytest

from src.optim.planejador import CenarioInvalido, otimizar_cenario


def test_caso_oficial_eixo4_acello(state):
    """GATE (bloqueia PR): Eixo 4 + ACELLO 815 reproduz o protótipo."""
    p = otimizar_cenario(state, 4, "ACELLO 815", semana=None, incluir_estimadas=True)
    t = p["totais"]
    assert t["quantidade_pedidos"] == 7
    assert abs(t["peso_utilizado"] - 4797.335) < 0.01
    assert abs(t["volume_utilizado"] - 2.4421) < 0.01
    assert p["gargalo"] == "PESO"
    assert p["violacoes"] == 0
    assert abs(t["valor_total"] - 16770.85) < 0.01


def test_nunca_viola_capacidade(state):
    for eixo in range(1, 6):
        p = otimizar_cenario(state, eixo, "ACELLO 815", semana=None)
        assert p["totais"]["peso_utilizado"] <= p["totais"]["peso_capacidade"] + 0.01
        assert p["totais"]["volume_utilizado"] <= p["totais"]["volume_capacidade"] + 0.001
        assert p["violacoes"] == 0


def test_determinismo_reexecucao(state):
    a = otimizar_cenario(state, 4, "ACELLO 815", semana=None)
    b = otimizar_cenario(state, 4, "ACELLO 815", semana=None)
    assert [s["pedido"] for s in a["pedidos_selecionados"]] == \
           [s["pedido"] for s in b["pedidos_selecionados"]]


def test_motivos_rejeicao_gerados(state):
    p = otimizar_cenario(state, 4, "ACELLO 815", semana=None)
    assert p["pedidos_rejeitados"]
    assert all(r["motivo"] for r in p["pedidos_rejeitados"])


def test_veiculo_nao_selecionavel_barra(state):
    with pytest.raises(CenarioInvalido):
        otimizar_cenario(state, 4, "MOTOS", semana=None)


def test_pedidos_selecionados_tem_itens(state):
    p = otimizar_cenario(state, 4, "ACELLO 815", semana=None)
    s = p["pedidos_selecionados"][0]
    assert s["qtd_itens"] >= 1
    assert s["itens"] and "descricao" in s["itens"][0]


def test_organizacao_zonas_lifo(state):
    """Zona do fundo = última cidade a ser entregue (LIFO pela rota)."""
    p = otimizar_cenario(state, 4, "ACELLO 815", semana=None)
    o = p["organizacao_carga"]
    assert o["zonas"] and o["zonas"][0]["posicao"] == "Fundo"
    # Eixo 4 entrega Ipaporanga→Poranga; com pedidos nas duas, fundo = Poranga
    assert o["zonas"][0]["cidade"] == "PORANGA"
    assert o["densidade_carga"] and o["densidade_carga"] > 0


def test_ocupacao_minima_flag(state):
    o = otimizar_cenario(state, 4, "ACELLO 815", semana=None)["organizacao_carga"]
    # caso oficial ocupa ~99,94% no gargalo → não está abaixo do mínimo
    assert o["abaixo_minimo"] is False
    assert o["ocupacao_gargalo"] >= o["ocupacao_minima"]
