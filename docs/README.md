# NobreLOG Optimizer — Documentação

> Base de conhecimento do projeto. Todo agente ou pessoa que for tocar código começa lendo [[AGENT_CHARTER]].

## Mapa

### Produto
- [[produto/prd]] — visão, escopo, proposta de valor
- [[produto/requisitos]] — RF + RNF
- [[produto/casos_de_uso]] — UC01–UC15

### Arquitetura
- [[arquitetura/visao_geral]] — diagrama, stack, boot in-memory
- [[arquitetura/backend]] — módulos, camadas puras vs. rotas
- [[arquitetura/frontend]] — estrutura React+TS
- [[arquitetura/adr/0001_sem_banco_de_dados]]
- [[arquitetura/adr/0002_upload_ingestao]]
- [[arquitetura/adr/0003_solver_pulp]]
- [[arquitetura/adr/0004_pdf_backend]]
- [[arquitetura/adr/0005_mvp_mono_eixo]]
- [[arquitetura/adr/0006_semana_dropdown]]
- [[arquitetura/adr/0007_motor_hibrido_llm]]
- [[arquitetura/adr/0008_desempate_valor]]
- [[arquitetura/adr/0009_deploy_stateful]]
- [[arquitetura/adr/0010_persistencia_opcional]]

### Domínio (o núcleo)
- [[dominio/pipeline_etl]] — 688 → 93 → 81, filtros e rastreabilidade
- [[dominio/cubagem]] — m²→caixas, classificação 🟢🟡🔴
- [[dominio/otimizacao]] — MILP com PuLP, gargalo, explicabilidade
- [[dominio/romaneio]] — layout PDF, LIFO
- [[dominio/llm_insights]] — camada 2 (opcional)

### API
- [[api/endpoints]] — rotas e status codes
- [[api/contratos]] — schemas JSON

### Dados
- [[dados/dicionario]] — colunas por CSV
- [[dados/glossario]] — termos do domínio

### Frontend
- [[frontend/telas]] — 5 telas (planejamento, romaneio, simulação, qualidade, triagem)
- [[frontend/design_system]] — paleta, tipografia, tokens

### Entrega
- [[entrega/criterios_aceite]] — checklist MVP + caso oficial
- [[entrega/pitch]] — roteiro de 7 min

### PRDs de execução (passos de implementação)
- [[prd/README]] — índice, ordem e dependências
- [[prd/00-errata-decisoes]] — resolve as inconsistências da doc (ler primeiro)
- [[prd/01-fundacao-deploy]] … [[prd/09-reingestao-testes]] — um PRD por módulo

## Convenções

- Links internos usam `[[wikilink]]` com caminho relativo à raiz `docs/`.
- Números vindos de execução do solver citam a fonte ([[dados/dicionario]] ou execução datada).
- Toda decisão arquitetural nova vira ADR numerada em `arquitetura/adr/`.
- Português (pt-BR) no corpo. Nomes técnicos em inglês (endpoint, hard constraint, etc.).
