"""Log rastreável de correções + enum canônico de motivos de exclusão (PRD-00 I6/E5)."""
from __future__ import annotations

from datetime import datetime, timezone


# Motivos de exclusão canônicos (código -> rótulo exibido).
MOTIVOS = {
    "CANCELADO": "Cancelado",
    "RETIRADA_BALCAO": "Retirada no balcão",
    "CRATEUS": "Crateús",
    "CIDADE_FORA_EIXO": "Cidade fora dos eixos",
    "CUBAGEM_AUSENTE": "Cubagem ausente",
    "DATA_INCONSISTENTE": "Data inconsistente",
}

# Ações para o painel de anomalias (PRD-00 E5).
ACOES = {"CORRIGIDA", "SINALIZADA", "ESTIMADO", "PADRONIZADA"}


def make_correcao(
    pedido: str, campo: str, valor_original: str, valor_novo: str,
    regra: str, criterio: str, acao: str,
) -> dict:
    """Constrói uma entrada de correção (valor_novo em ISO quando for data — I2)."""
    assert acao in ACOES, f"ação inválida: {acao}"
    return {
        "pedido": pedido,
        "campo": campo,
        "valor_original": valor_original,
        "valor_novo": valor_novo,
        "regra": regra,
        "criterio": criterio,
        "acao": acao,
        "aplicada_em": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
