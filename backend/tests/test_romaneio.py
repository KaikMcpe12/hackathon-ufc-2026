import pytest

from src.optim.planejador import otimizar_cenario
from src.romaneio.gerador import PlanoComViolacoes, gerar_pdf


def test_gera_pdf_do_caso_oficial(state):
    plano = otimizar_cenario(state, 4, "ACELLO 815", semana=None)
    pdf = gerar_pdf(plano, coordenador="Demo", data_carga="2026-08-24")
    assert pdf[:5] == b"%PDF-"
    assert len(pdf) > 2000


def test_422_quando_ha_violacoes(state):
    plano = otimizar_cenario(state, 4, "ACELLO 815", semana=None)
    plano["violacoes"] = 1
    with pytest.raises(PlanoComViolacoes):
        gerar_pdf(plano)
