# PRD-03 — Cubagem

> **Status:** proposto. Depende de: [[prd/02-pipeline-etl]], [[prd/00-errata-decisoes]].
> Converte itens vendidos em **peso** e **volume** físicos e classifica cada pedido 🟢🟡🔴. Alvo: **46 completos / 81 utilizáveis**.

## Objetivo

Implementar as etapas 5–6 de [[dominio/pipeline_etl]] / [[dominio/cubagem]] como funções puras em `src/cubagem/`, preenchendo `peso_kg`, `volume_m3`, `qualidade_cubagem` e `itens` de `state.pedidos_processados`.

## Escopo

**Dentro:**
- **Parse** do `Itens_Resumo` por regex (`ITEM_RE` de [[dominio/cubagem]]) → `{codigo, descricao, qtd, un}`.
- **Cruzamento** por `codigo` com `state.ranking` (Top 85).
- **Conversão** (`conversor.py`): m²→caixas com `ceil(m2_solicitados / m2_por_caixa)`; `m2_por_caixa` extraído de `Unidade_Venda` por regex (L2); `peso_total=caixas·peso_caixa`, `volume_total=caixas·volume_caixa`. Produtos sem m² → cálculo direto por unidade.
- **Classificação** (`classificador.py`): selo por pior item — 🟢 todos oficiais / 🟡 algum estimado ou sintético / 🔴 algum sem cubagem. `pior_selo(🔴>🟡>🟢)`.
- **Sintéticos** (`sintetico.py`): carrega `etapa4b_referencias_sinteticas_prototipo.csv` (opcional), marca `fonte=sintetico:*` e força 🟡; gera `Correcao` com `acao=ESTIMADO` (E5).
- **Agregação** por pedido: soma `peso_total`/`volume_total`; monta `Item[]`.

**Fora:** flag `incluir_estimadas` no solver (PRD-04).

## Contratos / estruturas

`Item` (de [[api/contratos]] + L3): `unidade_venda` = unidade **do pedido** (UN/MT); `caixas` preenchido só quando houve conversão m²→caixas (senão `null`); `dado_estimado: bool`.

`Pedido.{peso_kg,volume_m3}`: `float | null` — **`null`/NaN** quando 🔴 (I4). **Nunca zero** (Charter §3.2).

`qualidade_cubagem`: `COMPLETA` (🟢) | `ESTIMADA` (🟡) | `AUSENTE` (🔴).

## Regras invioláveis (Charter)
- Peso/volume ausente **nunca** vira zero → 🔴 + fila de revisão.
- Nunca fração de caixa (`ceil`).
- Faixa de peso: usar o **valor maior** (segurança — melhor sobrar carga fictícia).
- Sintético sempre 🟡, nunca 🟢; marcado em `fonte`.

## Critérios de aceite
- [ ] `ceil(15,180 / 2,30) = 7 caixas` (exemplo PISO POINTER).
- [ ] Item sem código no Ranking → 🔴; pedido com item 🔴 → `AUSENTE` + `peso_kg=null`.
- [ ] **46** pedidos 🟢 (só dados oficiais); **81** utilizáveis (🟢+🟡 com sintéticos); **12** 🔴 (soma 93 — I7).
- [ ] Pedido com item estimado/sintético → 🟡 (nunca 🟢).
- [ ] `Item.caixas` só preenchido em conversão m²→caixas.

## Testes (de [[entrega/criterios_aceite]])
`test_parse_item_resumo`, `test_converte_m2_em_caixas_ceil`, `test_ausencia_nao_vira_zero`, `test_classifica_selo_pior_do_pedido`, `test_contagem_selos_46_35_12`.

## Riscos
- Regex de `Itens_Resumo` frágil a variações de formatação — cobrir casos reais.
- `m2_por_caixa` implícito em `Unidade_Venda` com formatos variados (`"Caixa 2,30 m²"`, `"CX 2,3m2"`) — regex tolerante + fallback.
- Estimativas sintéticas são necessárias para reproduzir os 7 do caso oficial (I5) — garantir carregamento.

## Ver também
[[dominio/cubagem]] · [[dados/dicionario]]#ranking · [[dominio/pipeline_etl]]
