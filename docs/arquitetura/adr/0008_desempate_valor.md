# ADR 0008 — Desempate por valor no solver (ε lexicográfico)

**Status:** Proposta
**Data:** 2026-09-16

## Contexto

A função objetivo do solver é `0,5·Op + 0,5·Ov` (ocupação de peso e volume). [[dominio/otimizacao]] diz que **valor financeiro é critério secundário de desempate**: "se duas soluções empataram em ocupação (diferença < ε), escolhe a de maior valor". Porém:

1. O código PuLP documentado **não implementa** esse desempate — só tem os dois termos de ocupação.
2. O CBC pode retornar **qualquer** solução ótima quando há empate de valor objetivo, o que **quebra o determinismo** exigido pelo caso oficial (Eixo 4 + ACELLO 815 tem números exatos a reproduzir).
3. `ε` nunca foi definido.

## Decisão

Adicionar um **terceiro termo de desempate** à função objetivo, com peso ε pequeno:

```
maximizar  0,5·(peso_util/cap_peso) + 0,5·(vol_util/cap_vol) + ε·(valor_total/valor_ref)
```

- `valor_ref` = soma do `valor` de todos os pedidos elegíveis do cenário (normaliza o termo de valor para [0, 1]).
- **ε = 1e-4.** Pequeno o bastante para que **nenhuma diferença de valor supere 1 ponto percentual de ocupação** (o termo de valor nunca "compra" ocupação); grande o bastante para desempatar de forma numericamente estável.
- Combinado com as regras de determinismo já existentes (ordenar pedidos por `pedido_id`, `timeLimit=30`, não depender de ordem de dict), garante saída reproduzível.

## Alternativas consideradas

- **Solve lexicográfico em 2 passes:** (1) maximiza ocupação; (2) fixa a ocupação ótima como restrição e re-otimiza maximizando valor. Matematicamente mais limpo (sem risco de ε "vazar" para a ocupação), porém dobra o tempo de solve e adiciona uma restrição de igualdade sensível a arredondamento. Fica registrado como **plano B** caso ε cause instabilidade numérica no caso oficial.
- **Sem desempate (só ocupação):** rejeitado — não é determinístico e ignora o critério de valor documentado.

## Consequências

**Positivas:**
- Determinismo do caso oficial preservado.
- Critério de valor implementado sem uma segunda chamada ao solver.

**Negativas:**
- ε mal calibrado poderia, em teoria, trocar uma solução por outra de ocupação marginalmente menor mas valor maior. Mitigação: teste que verifica que a ocupação ótima não regride ao ativar o termo de valor.

## Ver também

- [[dominio/otimizacao]] — função objetivo e determinismo
- [[prd/00-errata-decisoes]]#l1
- [[prd/04-otimizacao]]
- [[entrega/criterios_aceite]] — gate do caso oficial
