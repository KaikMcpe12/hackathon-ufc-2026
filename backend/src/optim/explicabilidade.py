"""Motivo explicável para cada pedido rejeitado. Ver [[dominio/otimizacao]]#explicabilidade."""
from __future__ import annotations


def motivo_rejeicao(
    peso_i: float, vol_i: float, peso_sel: float, vol_sel: float,
    cap_peso: float, cap_vol: float,
) -> str:
    """Gera a mensagem em linguagem natural para um pedido não selecionado."""
    delta_peso = (peso_sel + peso_i) - cap_peso
    delta_vol = (vol_sel + vol_i) - cap_vol
    excede_peso = peso_i > cap_peso or delta_peso > 0
    excede_vol = vol_i > cap_vol or delta_vol > 0

    if peso_i > cap_peso and vol_i > cap_vol:
        return "Excederia peso e volume."
    if peso_i > cap_peso:
        return f"Excederia a capacidade de peso em {peso_i - cap_peso:.2f} kg."
    if vol_i > cap_vol:
        return f"Excederia a capacidade de volume em {vol_i - cap_vol:.4f} m³."
    if excede_peso and excede_vol:
        return "Excederia peso e volume."
    if excede_peso:
        return f"Excederia a capacidade de peso em {delta_peso:.2f} kg."
    if excede_vol:
        return f"Excederia a capacidade de volume em {delta_vol:.4f} m³."
    return "Outra combinação aproveita melhor o caminhão."
