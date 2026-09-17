"""Persistência SQLite (PRD-12): reproduz o gate + cadastro por upsert + persistência."""
import pytest

from src import config, state
from src.optim.planejador import otimizar_cenario


@pytest.fixture
def sqlite_state(tmp_path, monkeypatch):
    monkeypatch.setattr(config, "STATE_BACKEND", "sqlite")
    monkeypatch.setattr(config, "DB_PATH", tmp_path / "t.db")
    st = state.bootstrap(config.DATA_DIR)
    yield st
    # restaura o backend memory para os demais testes
    state._repo = None
    monkeypatch.setattr(config, "STATE_BACKEND", "memory")
    state.bootstrap(config.DATA_DIR)


def test_sqlite_reproduz_gate(sqlite_state):
    assert sqlite_state.stats["elegiveis"] == 81          # pipeline lossless
    p = otimizar_cenario(sqlite_state, 4, "ACELLO 815")
    assert abs(p["totais"]["peso_utilizado"] - 4797.335) < 0.01


def test_sqlite_cadastro_upsert(sqlite_state):
    n0 = state.contagem_db()["produtos"]
    rel = state.cadastrar_produtos([
        {"codigo": "88888", "produto": "X", "unidade_venda": "UN",
         "peso_kg": "5,0", "volume_m3": "0,02", "dado_estimado": "NAO"}])
    assert rel["inseridos"] == 1
    assert state.contagem_db()["produtos"] == n0 + 1
    # reenvio do mesmo código ATUALIZA (não duplica PK)
    rel2 = state.cadastrar_produtos([
        {"codigo": "88888", "produto": "X2", "unidade_venda": "UN",
         "peso_kg": "6,0", "volume_m3": "0,03", "dado_estimado": "NAO"}])
    assert rel2["atualizados"] == 1
    assert state.contagem_db()["produtos"] == n0 + 1


def test_sqlite_persiste_apos_reabrir(sqlite_state):
    from src.db.repository import SqliteRepo
    state.cadastrar_produtos([{"codigo": "77777", "produto": "Y", "unidade_venda": "UN",
                               "peso_kg": "1,0", "volume_m3": "0,01"}])
    r2 = SqliteRepo(config.DB_PATH)  # "reinício"
    assert r2.contagem()["produtos"] >= 86
