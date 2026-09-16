"""Monta o prompt determinístico a partir do PlanoDeCarga. Ver [[dominio/llm_insights]]."""
from __future__ import annotations

SISTEMA = (
    "Você é um assistente de logística do Grupo Nobre Lar. Recebe o resultado de um "
    "otimizador de carga (determinístico) e escreve 1–2 parágrafos curtos em português, "
    "para um coordenador. REGRAS: (1) nunca altere os números — só os interprete; "
    "(2) nunca diga se a carga é válida (isso o solver já garante); (3) seja objetivo e "
    "operacional. Se algum pedido foi rejeitado por pouco (< 5% da capacidade do gargalo), "
    "sugira revisão."
)


def montar_prompt(plano: dict) -> str:
    t = plano["totais"]
    rej = plano.get("pedidos_rejeitados", [])
    linhas = [
        f"Eixo: {plano['eixo']['nome']} | Veículo: {plano['veiculo']['nome']}",
        f"Gargalo: {plano['gargalo']} | Violações: {plano['violacoes']}",
        f"Peso: {t['peso_utilizado']} / {t['peso_capacidade']} kg "
        f"({t['ocupacao_peso']*100:.2f}%)",
        f"Volume: {t['volume_utilizado']} / {t['volume_capacidade']} m³ "
        f"({t['ocupacao_volume']*100:.2f}%)",
        f"Valor total: R$ {t['valor_total']} | Pedidos: {t['quantidade_pedidos']} "
        f"selecionados, {len(rej)} rejeitados",
    ]
    return SISTEMA + "\n\nDADOS DO PLANO:\n" + "\n".join(linhas)
