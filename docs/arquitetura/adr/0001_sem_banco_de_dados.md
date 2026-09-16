# ADR 0001 — Sem banco de dados

**Status:** Aceita
**Data:** 2026-09-16
**Decisor:** Kaik + equipe

## Contexto

O sistema opera sobre 4 CSVs semanais + Ranking Top 85 + Rotas/Coletas — todos arquivos estáticos entregues pelo desafio. Não há multiusuário, não há histórico entre sessões, não há concorrência.

## Decisão

Não usar banco de dados. Estado da aplicação vive **em memória** (`pandas.DataFrame` em `src/state.py`), carregado no `startup` do FastAPI a partir de `backend/data/*.csv`.

## Consequências

**Positivas:**
- Setup zero (sem migrations, sem docker-compose de Postgres).
- Queries são operações Pandas — rápidas, familiares ao time.
- Deploy simples: qualquer host com Python roda.

**Negativas:**
- Reinício do servidor perde qualquer re-ingestão que não foi comitada nos CSVs.
- Escalar horizontalmente exige que cada instância recarregue os arquivos.
- Não serve para produção real; é MVP consciente.

## Alternativas descartadas

- **SQLite:** overhead sem ganho — as queries são sobre datasets pequenos.
- **Postgres:** overkill para o hackathon.
- **Parquet/DuckDB:** ganho marginal em performance, custo de complexidade não vale.

## Ver também

- [[arquitetura/adr/0002_upload_ingestao]] — como o upload preserva a decisão in-memory
