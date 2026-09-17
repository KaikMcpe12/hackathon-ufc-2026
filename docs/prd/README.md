# PRDs de Execução — NobreLOG Optimizer

> Cada passo de construção do MVP tem seu próprio PRD, para ser **validado/corrigido** antes de implementar.
> Comece por [[prd/00-errata-decisoes]] — ele resolve as inconsistências da documentação e é pré-requisito dos demais.

## Ordem e dependências

| PRD | Título | Depende de | Entrega |
|-----|--------|------------|---------|
| [[prd/00-errata-decisoes]] | Errata & Decisões | — | de-para das inconsistências (B/I/L/E) + ADRs 0008–0010 |
| [[prd/01-fundacao-deploy]] | Fundação & Deploy | 00 | scaffolding, seed, metadados, deploy stateful |
| [[prd/02-pipeline-etl]] | Pipeline ETL | 01 | 688→93, log rastreável, motivos |
| [[prd/03-cubagem]] | Cubagem | 02 | m²→caixas, selos 🟢🟡🔴, 46/81 |
| [[prd/04-otimizacao]] | Otimização MILP | 02, 03 | solver + **gate caso oficial** |
| [[prd/05-api]] | API de aplicação | 02, 03, 04 | rotas thin + contratos Pydantic |
| [[prd/06-romaneio]] | Romaneio (PDF) | 04, 05 | WeasyPrint, LIFO, 422 |
| [[prd/07-llm-insights]] | Camada LLM | 05 | /insight opcional, fallback |
| [[prd/08-frontend]] | Frontend (5 telas + Importar) | 01, 05 (06/07) | UI fiel aos mockups |
| [[prd/09-reingestao-testes]] | Re-ingestão, Testes & Aceite | 02–06 | upload + suíte pytest + gate |
| [[prd/10-pos-mvp-melhorias]] | Pós-MVP: Vendas_Faturamento + Multi-eixo + Render | 09 | integração dado bruto, MKP heurístico, deploy stateful |
| [[prd/11-melhorias-ux]] | Melhorias de UX/UI, A11y, PDF e Front-end | 08 | redesign shadcn/ui, hero, componentes ricos, PDF (P0 já feito) |
| [[prd/12-persistencia-banco]] | Persistência em banco (branch separada) | 10 | cadastro (form + CSV), histórico, upsert — futuro |

> **Deploy pronto (arquivos):** [`render.yaml`](../../render.yaml) · [`backend/Dockerfile`](../../backend/Dockerfile) · [`frontend/vercel.json`](../../frontend/vercel.json) · guia [`DEPLOY.md`](../../DEPLOY.md).

## Caminho crítico (do dado ao caminhão)
`01 → 02 → 03 → 04` já reproduz o caso oficial no backend. `05 → 06` entrega API + PDF. `08` dá a cara. `07` e `09` fecham insights e o upload/testes.

## Template de cada PRD
Objetivo · Escopo (in/out) · Dependências · Contratos/estruturas · Regras invioláveis (Charter) · Critérios de aceite (checklist + números) · Testes · Riscos.

## Convenções
- pt-BR, wikilinks relativos à raiz `docs/`.
- Números do solver citam a fonte ([[entrega/criterios_aceite]]).
- Decisão arquitetural nova → ADR em `arquitetura/adr/`.

## Ver também
[[AGENT_CHARTER]] · [[produto/prd]] · [[entrega/criterios_aceite]]
