# PRD-04 — Otimização MILP

> **Status:** proposto. Depende de: [[prd/02-pipeline-etl]], [[prd/03-cubagem]], [[prd/00-errata-decisoes]].
> Núcleo determinístico. **Gate central do projeto:** reproduzir o caso oficial Eixo 4 + ACELLO 815.

## Objetivo

Implementar o solver de [[dominio/otimizacao]] como funções puras em `src/optim/`, resolvendo o Knapsack 2D (peso × volume) para 1 eixo + 1 veículo + 1 semana, com explicabilidade e determinismo.

## Escopo

**Dentro:**
- **Modelo** (`modelo.py`): variáveis binárias `x_i`; restrições hard `Σpeso·x ≤ cap_peso`, `Σvol·x ≤ cap_vol`; objetivo `0,5·Op + 0,5·Ov + ε·(valor/valor_ref)` com **ε=1e-4** ([[arquitetura/adr/0008_desempate_valor]]).
- **Pool de pedidos:** filtra por `eixo` + `semana`; aplica `incluir_estimadas` (I5: false→só 🟢; true→🟢+🟡; 🔴 sempre fora).
- **Solver** (`solver.py`): `PULP_CBC_CMD(msg=False, timeLimit=30)`; ordena por `pedido_id`; devolve seleção.
- **Gargalo** (`gargalo.py`): `PESO` se `ocup_peso > ocup_vol` senão `VOLUME`.
- **Explicabilidade** (`explicabilidade.py`): motivo por pedido rejeitado (tabela de [[dominio/otimizacao]]); `delta` arredondado a 2 casas, sempre positivo.
- **Wrapper** → monta `PlanoDeCarga` (Pydantic): `totais`, `gargalo`, `violacoes`, `pedidos_selecionados[]` (com `ordem`), `pedidos_rejeitados[]` (com `motivo`).

**Fora:** rota HTTP (PRD-05), sequência de descarga/LIFO e PDF (PRD-06).

## Regras invioláveis (Charter)
- **Zero violações** é hard constraint — API nunca devolve carga inválida.
- Função objetivo é ocupação (peso+volume); **valor é só desempate**, nunca o objetivo principal.
- Todo rejeitado tem **motivo explicável**.
- Determinismo: mesma entrada → mesma saída.

## Critérios de aceite — caso oficial (bloqueia PR)
Eixo 4 + ACELLO 815 + Semana 4, `incluir_estimadas=true`, tolerância ±0,01:

| Indicador | Esperado |
|-----------|----------|
| Pedidos selecionados | **7** |
| Peso utilizado | 4.797,335 / 4.800 kg (99,94%) |
| Volume utilizado | 2,4421 / 2,4543 m³ (99,50%) |
| Gargalo | **PESO** |
| Violações | **0** |
| Valor total | R$ 16.770,85 |

Outros:
- [ ] Nenhuma solução excede peso ou volume (qualquer cenário).
- [ ] Reexecução N vezes → saída idêntica (L4).
- [ ] Motivos de rejeição em linguagem natural, com `X kg`/`Y m³` quando aplicável.

## Testes (de [[entrega/criterios_aceite]])
`test_nunca_viola_peso`, `test_nunca_viola_volume`, `test_caso_oficial_eixo4_acello` **(bloqueia PR)**, `test_determinismo_reexecucao` (renomeado de `_com_seed` — L4), `test_motivos_rejeicao_gerados`, `test_epsilon_nao_regride_ocupacao` (ADR-0008).

## Riscos
- ε mal calibrado poderia trocar ocupação por valor — teste `test_epsilon_nao_regride_ocupacao` cobre.
- Se o caso oficial não bater, seguir a ordem de investigação de [[entrega/criterios_aceite]] (filtros→cubagem→sintéticos→semana→solver).

## Ver também
[[dominio/otimizacao]] · [[arquitetura/adr/0003_solver_pulp]] · [[arquitetura/adr/0008_desempate_valor]] · [[arquitetura/adr/0005_mvp_mono_eixo]]
