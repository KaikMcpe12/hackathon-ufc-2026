# ADR 0010 — Persistência opcional em banco de dados (caso alternativo)

**Status:** Proposta (opcional / v2 — não faz parte do MVP)
**Data:** 2026-09-16

## Contexto

O MVP não usa banco de dados: estado em memória, seed em `backend/data/`, upload volátil ([[arquitetura/adr/0001_sem_banco_de_dados]], [[arquitetura/adr/0009_deploy_stateful]]). Esse modelo tem dois limites conhecidos que **podem** exigir persistência no futuro:

1. **RAM insuficiente:** se o volume de pedidos crescer muito (várias semanas/filiais), manter tudo em `pandas` na memória do processo pode estourar o host.
2. **Histórico:** o cliente (Grupo Nobre Lar) pode querer **salvar planos de carga anteriores**, auditar decisões passadas, comparar semanas, ou não reprocessar os CSVs a cada restart.

Este ADR descreve **como** introduzir persistência **sem** quebrar o MVP, para ser acionado só quando um desses gatilhos ocorrer.

## Gatilhos para acionar

- O host do backend fica sob pressão de memória (OOM) com o dataset real.
- Requisito de negócio: histórico de planos, re-emissão de romaneios antigos, ou dados que sobrevivem a restart.
- Necessidade de deploy serverless (então o estado precisa morar fora do processo).

## Decisão (quando acionado)

Introduzir uma **camada de persistência plugável** atrás da mesma interface de `src/state.py`, sem mudar as funções puras de domínio (etl/cubagem/optim permanecem stateless e testáveis por script). Opções, do mais leve ao mais robusto:

| Opção | Quando usar | O que persiste |
|-------|-------------|----------------|
| **SQLite** (arquivo local) | Persistência simples num único host stateful | uploads processados, planos gerados, log de correções |
| **DuckDB / Parquet** | Datasets grandes, analítica sobre pedidos sem sair de dataframes | tabelas colunares de pedidos processados |
| **PostgreSQL** | Multi-usuário, concorrência, deploy sério | tudo + histórico versionado |
| **KV/Blob** (Vercel KV, Redis, S3) | Necessário para deploy serverless | sessão de upload + planos serializados (JSON/PDF) |

O que passaria a ser persistido:
- **Uploads processados** (snapshot do `state` por data de ingestão) — evita reprocessar no restart.
- **Planos de carga gerados** (`PlanoDeCarga` + PDF) — histórico e re-emissão.
- **Log de correções** (`log_correcoes`) — auditoria permanente (hoje é volátil).

Estratégia de migração:
1. Extrair uma interface `StateRepository` (get/save state, save plano, list planos).
2. Implementação atual = `InMemoryRepository` (comportamento de hoje).
3. Adicionar `SqliteRepository` (ou outra) por trás da mesma interface, selecionável por env (`STATE_BACKEND=memory|sqlite|postgres`).
4. Nenhuma mudança nas rotas nem no domínio.

## Consequências

**Positivas:**
- Caminho claro para escala e histórico sem reescrever o núcleo.
- Mantém o MVP enxuto (memória) como default.

**Negativas:**
- Introduz migrations/esquema quando adotado (o que o ADR 0001 evitou de propósito).
- Requer decidir política de retenção/anonimização do histórico (respeitar Charter §3.5 — dados anonimizados, sem reidentificação).

## Ver também

- [[arquitetura/adr/0001_sem_banco_de_dados]] — decisão base que este ADR estende opcionalmente
- [[arquitetura/adr/0009_deploy_stateful]] — deploy do MVP
- [[prd/00-errata-decisoes]]
