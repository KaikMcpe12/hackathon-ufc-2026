"""Robustez: o sistema deve iniciar mesmo sem dados (esperando upload) — não crashar."""
from pathlib import Path

import pytest

from src import config, state
from src.optim.planejador import CenarioInvalido, otimizar_cenario
from src.state import bootstrap

PEDIDOS_HEADER = (
    b"Pedido;Data;Vendedor;Situacao;Cidade;Logistica;"
    b"Situacao_CSV_Entrega;Valor_Pedido;Qtd_Itens;Itens_Resumo\n"
)


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


def test_toggle_use_seed_false_inicia_vazio(monkeypatch):
    """USE_SEED_DATA=false → inicia vazio mesmo com CSVs presentes."""
    monkeypatch.setattr(config, "USE_SEED_DATA", False)
    st = state.bootstrap(config.DATA_DIR)
    assert st.stats["registros_processados"] == 0
    state.bootstrap(config.DATA_DIR)  # restaura seed p/ os demais testes


def test_reingest_acumula_importacoes(monkeypatch):
    """Uploads sucessivos acumulam: sobrescreve só o slot enviado, retém os anteriores."""
    monkeypatch.setattr(config, "USE_SEED_DATA", True)
    base = state.bootstrap(config.DATA_DIR)
    n0 = base.stats["registros_processados"]
    n1 = state.reingest({"semana_4": PEDIDOS_HEADER}).stats["registros_processados"]
    assert n1 < n0  # semana 4 zerada
    with open(config.DATA_DIR / "ranking_top85.csv", "rb") as f:
        n2 = state.reingest({"ranking": f.read()}).stats["registros_processados"]
    assert n2 == n1  # semana 4 PERMANECE vazia (acumulou, não voltou ao seed)
    state.bootstrap(config.DATA_DIR)  # restaura
