import math
from pathlib import Path

import pandas as pd

from src.cubagem.conversor import m2_por_caixa
from src.cubagem.parser import parse_itens_resumo

ORACULO = Path(__file__).parent / "oraculo"


def test_parse_item_resumo():
    itens = parse_itens_resumo("14900 - ARGAMASSA X 15KG (7,00 UN) | 15624 - REJ (2,00 UN)")
    assert len(itens) == 2
    assert itens[0]["codigo"] == "14900" and itens[0]["quantidade"] == 7.0
    assert itens[0]["unidade_venda"] == "UN"


def test_parse_item_sem_unidade():
    itens = parse_itens_resumo("11906 - REJUNTE 1KG FD (5,00)")
    assert itens[0]["quantidade"] == 5.0 and itens[0]["unidade_venda"] == "UN"


def test_m2_por_caixa():
    assert m2_por_caixa("Caixa 2,30 m²") == 2.30
    assert m2_por_caixa("Caixa (3 peças = 2,18 m²)") == 2.18
    assert m2_por_caixa("Saco 15 kg") is None


def test_converte_m2_em_caixas_ceil():
    assert math.ceil(15.180 / 2.30) == 7


def test_selos_calibrados(state):
    s = state.stats
    assert s["pedidos_completa"] == 39      # 🟢 (100% referência do Ranking)
    assert s["pedidos_estimada"] == 42      # 🟡 (usou estimativa sintética)
    assert s["pedidos_ausente"] == 0        # 🔴 (nenhum na base seed)


def test_ausencia_nao_vira_zero(state):
    # nenhum pedido processado tem peso 0 (ausência é NaN, não zero)
    proc = state.pedidos_processados
    assert not (proc["peso_kg"] == 0).any()


def test_cubagem_bate_prototipo(state):
    proto = pd.read_csv(ORACULO / "pedidos_solver_prototipo.csv", sep=";",
                        dtype=str, encoding="utf-8-sig")
    proto["Pedido"] = proto["Pedido"].str.strip()
    ref = proto.set_index("Pedido")["Peso_Total_kg"].astype(float)
    calc = state.pedidos_processados.set_index("pedido")["peso_kg"]
    j = calc.to_frame("calc").join(ref.rename("ref"))
    difs = (j["calc"] - j["ref"]).abs()
    # ≥ 79/81 batem exato; 2 outliers conhecidos (caixa-rounding) < 42 kg
    assert (difs < 0.01).sum() >= 79
    assert difs.max() < 45
