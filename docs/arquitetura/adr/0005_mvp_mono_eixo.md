# ADR 0005 — MVP mono-eixo / mono-veículo

**Status:** Aceita
**Data:** 2026-09-16

## Contexto

O edital descreve multi-eixo (5 eixos, 4 caminhões) como **bônus, não eliminatório**. O Documento Mestre trata multi-eixo como fase posterior. O PRD havia modelado `x_{i,j}` e `y_{j,k}` (multi).

## Decisão

O MVP resolve `1 eixo + 1 veículo` por execução (Knapsack 2D). Multi-eixo simultâneo fica em **v2**.

## Justificativa

- Cronograma de 13h.
- Complexidade de UI cresce (roteamento de frota) sem melhorar o pitch — o "momento UAU" já cabe em mono.
- Comparação lado a lado de 2 veículos ([[frontend/telas]]#simulacao) já demonstra "e se eu escolhesse outro caminhão" sem virar problema multi.

## Consequências

**Positivas:**
- Modelo matemático trivial: 1 conjunto de restrições, 1 função objetivo.
- Explicabilidade fica clara ("neste veículo, este pedido não coube").

**Negativas:**
- Não resolve o problema estratégico do coordenador de "com 4 caminhões e 5 eixos, qual eixo fica sem caminhão hoje?".

## Ver também

- [[dominio/otimizacao]]
