"""Validação do ETL contra os números de referência (688 -> 93). Rodar:
    python -m scripts.validate_etl
"""
from __future__ import annotations

from src import config
from src.etl.pipeline import rodar_etl


def main() -> None:
    r = rodar_etl(config.DATA_DIR)
    print(f"Registros carregados: {r['n_registros']}  (esperado 688)")
    print(f"Pedidos elegíveis:    {len(r['elegiveis'])}  (esperado ~93)")
    print(f"Eixos:                {len(r['eixos'])}  -> {list(r['eixos']['nome'])}")
    print("Veículos:")
    for _, v in r["veiculos"].iterrows():
        print(f"   - {v['nome']!r:16} peso={v['capacidade_peso']} vol={v['capacidade_volume']} "
              f"selecionavel={v['selecionavel']}")
    print("Motivos de exclusão:")
    for m in r["motivos_exclusao"]:
        print(f"   - {m['motivo']:24} {m['total']:>4}  ({m['percentual']}%)")
    print(f"Correções registradas: {len(r['correcoes'])}")
    # distribuição por eixo dos elegíveis
    print("Elegíveis por eixo:")
    print(r["elegiveis"]["eixo_id"].value_counts().sort_index().to_string())


if __name__ == "__main__":
    main()
