# PRD-08 — Frontend (5 telas + Importar)

> **Status:** proposto. Depende de: [[prd/01-fundacao-deploy]], [[prd/05-api]] (e 06/07 para Romaneio/Insight).
> Interface React+TS fiel aos mockups (preto/branco/amarelo), consumindo a API.

## Objetivo

Implementar as 5 telas de [[frontend/telas]] + a tela **Importar** (E2), o design system de [[frontend/design_system]], os hooks React Query e o `api/client.ts` tipado.

## Escopo

**Telas (rotas):**
- `/` **Planejamento** — selects Eixo/Veículo/Semana + toggle `incluir_estimadas`; `POST /otimizar`; 4 KPIs (peso/volume/valor/pedidos de `totais`), gargalo, violações, sequência, tabela de selecionados; **bloco Insight de IA** (E1); botão → `/romaneio`.
- `/romaneio` **Romaneio** — preview do `PlanoDeCarga`; `POST /romaneio/generate` (Exportar PDF); assinaturas; bloco Insight.
- `/simulacao` **Simulação** — `POST /otimizar/comparar`; 2 cenários lado a lado; exibe `recomendado` **vindo do backend** (E6).
- `/qualidade` **Qualidade** — `GET /qualidade/resumo` + `/qualidade/log`; KPIs; stepper do pipeline; painel "Anomalias" agrupado por `Correcao.acao` (E5); donut de cobertura.
- `/triagem` **Triagem** — `GET /pedidos` com filtros incluindo **Qualidade da cubagem** (E4); `GET /qualidade/motivos-exclusao`; detalhe do pedido; `POST /pedidos/{id}/revisar` para 🔴.
- `/importar` **Importar** (E2) — drag-drop dos 6 CSVs → `POST /etl/ingest`; relatório de qualidade pós-ingestão.

**Design system:** cores (preto/branco/amarelo Nobre Lar), tipografia Inter, `tabular-nums`, formatação pt-BR (R$, kg, m³ até 5 casas, %). Componentes `KpiCard`, `OcupacaoBar`, `GargaloBadge`, `StatusBadge` (adicionar cor para "Retirada" — lacuna apontada), `TabelaPedidos`. Layout desktop 1280+.

**Estado:** React Query para GETs/mutations; sem Redux/Zustand; params via URL; resultado do `/otimizar` passa de `/` para `/romaneio` via router state.

**Fora:** lógica de negócio (fica no backend); MOTOS aparece desabilitado no dropdown (I3).

## Regras invioláveis
- Tipos em `types.ts` espelham snake_case do backend (não converter).
- Frontend **não recalcula** números do solver nem o `recomendado`.
- `peso_kg`/`volume_m3` `null` → render "—" (I4).

## Critérios de aceite (de [[entrega/criterios_aceite]])
- [ ] `/` completa: selecionar → otimizar → ver resultado.
- [ ] `/romaneio` renderiza e exporta PDF.
- [ ] `/simulacao` compara 2 veículos e destaca o recomendado do backend.
- [ ] `/qualidade` mostra pipeline + KPIs + anomalias por `acao`.
- [ ] `/triagem` lista com filtros (incl. qualidade) e revisa 🔴→🟡.
- [ ] `/importar` sobe CSVs e mostra relatório.
- [ ] Barras de ocupação, badge de gargalo, contador de violações, ordem de descarga + LIFO visíveis.
- [ ] Design fiel aos mockups; MOTOS desabilitado no seletor.
- [ ] Bloco Insight de IA com estados carregando/sucesso/indisponível.

## Testes
Testes de componente para KPI/OcupacaoBar/StatusBadge; testes de integração dos hooks contra a API (mock). (UI E2E fica opcional.)

## Riscos
- Fidelidade aos 5 mockups em `docs/inspiracao/` — revisar com o dono.
- Estados vazios/erro/carregando — cobrir skeletons e banners.

## Ver também
[[frontend/telas]] · [[frontend/design_system]] · [[arquitetura/frontend]] · [[api/contratos]]
