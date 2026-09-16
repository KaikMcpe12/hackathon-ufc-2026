# ADR 0006 — Seleção de semana via dropdown

**Status:** Aceita
**Data:** 2026-09-16

## Contexto

Temos 4 CSVs semanais (`Pedidos_Filtrados_Semana_1..4_Anonimizado.csv`). Precisamos decidir se o coordenador escolhe qual semana otimizar ou se consolidamos tudo.

## Decisão

Dropdown com 4 opções (Semanas 1, 2, 3, 4). **Default = última semana disponível** (Semana 4).

## Justificativa

- Semana é o "lote de pedidos em aberto" — realidade operacional.
- Consolidar as 4 semanas geraria pedidos "vencidos" na fila.
- Dropdown deixa a demo mais concreta ("hoje estamos planejando a semana 4") e permite trocar para testar cenários.

## Consequências

- `GET /semanas` retorna semanas disponíveis.
- `POST /otimizar` recebe `semana` como parâmetro obrigatório.
- Frontend: `<SeletorSemana>` como terceiro campo do formulário (Eixo, Veículo, Semana).

## Ver também

- [[frontend/telas]]#planejamento
- [[api/contratos]]#otimizar_request
