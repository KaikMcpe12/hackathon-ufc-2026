from src.etl.text import parse_data_br, parse_valor_br


def test_pipeline_688_93_81(state):
    s = state.stats
    assert s["registros_processados"] == 688
    assert s["pos_situacao"] == 93          # pós-situação (pitch: 688 → 93)
    assert s["elegiveis"] == 81             # com eixo (pool do solver)


def test_normaliza_valor_brasileiro():
    assert parse_valor_br("R$ 1.811,87") == 1811.87
    assert parse_valor_br("4.800 kg") == 4800.0
    assert parse_valor_br("2,4543") == 2.4543


def test_corrige_data_fora_lote():
    data, regra = parse_data_br("26/08/2014", 2026)
    assert regra == "ano_fora_do_lote"
    assert data.year == 2026 and data.month == 8 and data.day == 26


def test_veiculos_capacidades(state):
    v = state.veiculos.set_index("nome")
    assert v.loc["ACELLO 815", "capacidade_peso"] == 4800.0
    assert v.loc["HR / BONGO", "capacidade_peso"] == 1700.0
    assert v.loc["MOTOS", "selecionavel"] is False or not v.loc["MOTOS", "selecionavel"]


def test_motivos_exclusao_soma(state):
    total = sum(m["total"] for m in state.motivos_exclusao)
    assert total == 688 - 81  # todos os excluídos


def test_eixo4_cidades(state):
    e4 = state.eixos.set_index("id").loc[4]
    assert e4["cidades"][:3] == ["IPAPORANGA", "PORANGA", "ARARENDA"]


def test_enriquecimento_vendas_faturamento(state):
    """Vendas/Faturamento enriquece sem alterar o pipeline (688→93→81 intacto)."""
    assert state.stats["elegiveis"] == 81  # gate/pipeline preservado
    proc = state.pedidos_processados
    # a maioria dos elegíveis casa com o CSV de vendas (status preenchido)
    assert proc["status_faturamento"].notna().sum() >= 70
    assert "divergencias_cidade" in state.stats
