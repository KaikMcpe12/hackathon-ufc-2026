# ADR 0003 — Solver: PuLP + CBC

**Status:** Aceita
**Data:** 2026-09-16

## Contexto

O problema é um Knapsack 2D (peso × volume) com < 500 pedidos por eixo/semana. Precisamos escolher entre PuLP, OR-Tools e `scipy.optimize.milp`.

## Decisão

**PuLP** com solver **CBC** (embutido no `pulp>=2.8`).

## Justificativa

| Critério                     | PuLP + CBC       | OR-Tools         | scipy.milp       |
|------------------------------|------------------|------------------|------------------|
| API para MILP                | Simples, LP-like | Verbosa          | Baixo nível      |
| Instalação                   | `pip install pulp` (CBC vem junto) | pesada (>100MB) | Vem com SciPy    |
| Performance no problema atual | < 1s             | < 1s             | Similar          |
| Curva de aprendizado         | Mínima           | Média            | Alta             |
| Docs pt-BR/comunidade        | Extensa          | Média            | Escassa          |

Para o tamanho do problema, **desempenho não é diferencial** — PuLP ganha pela ergonomia.

## Consequências

**Positivas:**
- Modelo lê como matemática (`lpSum`, `<=`, variáveis binárias).
- Trocar solver depois é 1 linha (CBC → GLPK → Gurobi).

**Negativas:**
- CBC é single-threaded. Para casos muito grandes (v2 multi-eixo) pode virar gargalo.

## Ver também

- [[dominio/otimizacao]]
- [[arquitetura/adr/0007_motor_hibrido_llm]] — o LLM é a **camada 2**, não substitui o solver
