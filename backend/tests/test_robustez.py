"""Robustez: o sistema deve iniciar mesmo sem dados (esperando upload) — não crashar."""
from pathlib import Path

import pytest

from src.optim.planejador import CenarioInvalido, otimizar_cenario
from src.state import bootstrap


@pytest.fixture(scope="module")
def estado_vazio(tmp_path_factory):
    vazio = tmp_path_factory.mktemp("sem_dados")
    return bootstrap(vazio)


def test_boot_sem_dados_nao_crasha(estado_vazio):
    assert estado_vazio.stats["registros_processados"] == 0
    assert len(estado_vazio.eixos) == 0
    assert len(estado_vazio.veiculos) == 0
    assert len(estado_vazio.pedidos_processados) == 0


def test_otimizar_sem_dados_barra(estado_vazio):
    with pytest.raises(CenarioInvalido):
        otimizar_cenario(estado_vazio, 4, "ACELLO 815")


def test_boot_dir_inexistente_nao_crasha():
    st = bootstrap(Path("/nao/existe/mesmo"))
    assert st.stats["registros_processados"] == 0
