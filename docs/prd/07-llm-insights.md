# PRD-07 — Camada LLM (Insights)

> **Status:** proposto (opcional no MVP). Depende de: [[prd/05-api]].
> Camada 2 do motor híbrido: interpreta o resultado do solver em linguagem natural, sem nunca alterar números. [[arquitetura/adr/0007_motor_hibrido_llm]].

## Objetivo

Implementar `src/llm/` e `POST /insight` conforme [[dominio/llm_insights]]: recebe um `PlanoDeCarga`, devolve 1–2 parágrafos em pt-BR com insights operacionais. Falha sempre de forma silenciosa.

## Escopo

**Dentro:**
- `client.py`: interface abstrata de provedor; implementação **Anthropic Claude** (default). Env: `ANTHROPIC_API_KEY`, `LLM_MODEL` (default `claude-haiku-4-5`), `LLM_TIMEOUT_S=8` (L5). Zero Data Retention configurado.
- `prompt.py`: monta o prompt determinístico a partir do `PlanoDeCarga` (ocupações, gargalo, rejeitados, folga). Regras: nunca alterar números, nunca decidir validade, sugerir revisão se pedido rejeitado por pouco (< 5% da capacidade na dimensão do gargalo).
- `POST /insight` (body `{ plano }`) → `{ resumo, modelo, duracao_ms }` | **503** (sem chave/timeout/provedor offline → fallback).
- Wiring de UI (E1): bloco "Insight de IA" na tela Planejamento e no Romaneio.

**Fora:** streaming; múltiplos provedores simultâneos.

## Regras invioláveis (ADR 0007 / Charter)
- LLM **nunca** altera números do solver; entrada = saída do solver + contexto; saída = texto.
- LLM **nunca** decide se a carga é válida.
- Fallback silencioso: falha do LLM não quebra o fluxo principal.
- Insight sempre rotulado como "gerado por IA", separado dos números.
- MVP roda **sem** LLM (opcional, sem custo obrigatório).

## Critérios de aceite
- [ ] Com `ANTHROPIC_API_KEY` válida: `/insight` retorna 1–2 parágrafos coerentes + `modelo` real + `duracao_ms`.
- [ ] Sem chave: `/insight` → 503; frontend colapsa o bloco ("Insight de IA não disponível no momento.").
- [ ] Timeout > `LLM_TIMEOUT_S` → 503 (não trava a request).
- [ ] O texto não contradiz os números do plano (não inventa ocupação/valor).

## Testes
`test_llm.py`: prompt contém os números do plano; `/insight` sem chave → 503; mock de provedor retorna texto; timeout simulado → 503.

## Riscos
- Custo/latência por chamada — opt-in e assíncrono no front.
- LLM "alucinar" números — prompt instrui a só interpretar; validação humana no bloco de IA.

## Ver também
[[dominio/llm_insights]] · [[arquitetura/adr/0007_motor_hibrido_llm]] · [[prd/00-errata-decisoes]]#l5
