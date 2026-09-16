# ADR 0007 — Motor híbrido: Matemático + LLM

**Status:** Aceita
**Data:** 2026-09-16

## Contexto

O núcleo do sistema é determinístico (MILP). Queremos agregar valor com insights operacionais em linguagem natural — mas sem comprometer a garantia de zero violações e a reproduzibilidade dos números.

## Decisão

Adotar **arquitetura híbrida em duas etapas**:

```
[ Requisição: Eixo + Veículo + Semana ]
                ↓
   [ 1. Motor Matemático (PuLP/CBC) ]  →  dados determinísticos (JSON/tabela)
                ↓                          (0 violações — hard constraint)
   [ 2. Camada LLM (opcional) ]        →  texto de recomendação
                                          (insights, alertas, resumo)
```

## Regras invioláveis do LLM

1. **LLM nunca altera números do solver.** Entrada do LLM = saída do solver + contexto. Saída do LLM = *texto*.
2. **LLM nunca decide se a carga é válida.** Validação = solver.
3. **Fallback silencioso:** se LLM falhar (rate limit, offline, sem API key), o sistema continua funcionando sem os insights.
4. **Insights são separados na UI:** aparecem em bloco identificado como "gerado por IA", nunca misturados com números do solver.
5. **Sem custo obrigatório:** camada LLM é opcional — MVP roda sem ela.

## Exemplo de uso

Após otimização do Eixo 4 + ACELLO 815:

> **Insight operacional (IA):**
> Esta carga está limitada por peso (99,94%). Sobra volume equivalente a ~2 pedidos leves. Considere adicionar itens de menor densidade (rejuntes, argamassas em sacos pequenos) se o próximo pedido for para Ipaporanga ou Ararendá.

## Provedor

A definir na implementação. Interface abstrata em `src/llm/client.py` permite trocar (OpenAI, Anthropic, local).

## Consequências

**Positivas:**
- Sistema demonstra "IA usada com propósito", não como enfeite.
- Coordenador ganha explicação em português sem depender de gráficos.

**Negativas:**
- Custo por chamada (se provedor pago).
- Latência adicional (~1–3s). Insights devem ser assíncronos ou opt-in.

## Ver também

- [[dominio/llm_insights]] — prompt e contrato
- [[api/endpoints]]#insight
