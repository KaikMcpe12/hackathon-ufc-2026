# PRD-01 — Fundação & Deploy

> **Status:** proposto. Depende de: [[prd/00-errata-decisoes]].
> Base para todos os demais PRDs. Cria o esqueleto do backend e do frontend, o estado in-memory, o seed dos CSVs reais e os endpoints de metadados.

## Objetivo

Ter um backend FastAPI que sobe, carrega os 6 CSVs de `backend/data/` em memória no startup, e serve `GET /eixos|/veiculos|/semanas`; e um frontend Vite/React/TS que builda e conversa com esse backend. Deploy: backend em host stateful, front na Vercel ([[arquitetura/adr/0009_deploy_stateful]]).

## Escopo

**Dentro:**
- Estrutura de pastas de [[arquitetura/backend]] e [[arquitetura/frontend]].
- `src/state.py` com `AppState`, `get_state()`, `bootstrap(data_dir)`, `reingest(files)`.
- Seed: 6 CSVs reais versionados em `backend/data/` (ver B1). Boot in-memory no `startup` do FastAPI.
- `state.eixos` **derivado** do CSV de rotas (B2) e `state.veiculos` com campo `selecionavel` (I3).
- Endpoints de metadados: `GET /eixos`, `GET /veiculos`, `GET /semanas`.
- `main.py` (FastAPI app, CORS para o domínio do front), healthcheck `GET /health`.
- `frontend/` scaffold: Vite + React + TS + Tailwind, `api/client.ts`, `api/types.ts` (espelha [[api/contratos]]), roteador das 5 telas + `/importar` (stubs).
- `pyproject.toml` e `package.json` com as dependências de [[arquitetura/backend]]/[[arquitetura/frontend]].
- Dockerfile (Python 3.11 + libs nativas do WeasyPrint) e instruções de deploy.

**Fora:** ETL real (PRD-02), cubagem (PRD-03), solver (PRD-04), telas ricas (PRD-08).

## Módulos / arquivos

```
backend/
├── data/                         # 6 CSVs reais (seed)
├── pyproject.toml
├── Dockerfile
└── src/
    ├── main.py                   # FastAPI, CORS, startup->bootstrap, /health
    ├── state.py                  # AppState + get_state/bootstrap/reingest
    ├── config.py                 # env: DATA_DIR, CORS_ORIGINS, LLM_*, STATE_BACKEND
    ├── models/{veiculo,eixo}.py  # Pydantic (parcial nesta fase)
    └── api/routes/{eixos,veiculos,semanas}.py
frontend/
├── package.json, vite.config.ts, tailwind.config.ts
└── src/{main.tsx,App.tsx,router.tsx,api/{client,types,endpoints}.ts}
```

## Estruturas

`AppState` (NamedTuple, ver [[arquitetura/backend]]): `pedidos_raw`, `pedidos_processados`, `ranking`, `veiculos`, `eixos`, `log_correcoes`.

Contratos desta fase (de [[api/contratos]]):
- `Eixo`: `{ id, nome, cidades[] }` — 5 eixos derivados de rotas.
- `Veiculo`: `{ nome, capacidade_peso, capacidade_volume, descricao, selecionavel }` — 3 veículos; `MOTOS.selecionavel=false` (I3).
- `GET /semanas` → `{ semanas: [1,2,3,4], padrao: 4 }` (default última — [[arquitetura/adr/0006_semana_dropdown]]).

## Regras invioláveis (Charter)
- Sem banco de dados; estado em memória ([[arquitetura/adr/0001_sem_banco_de_dados]]).
- Sem auth no MVP.
- Domínio sem side-effects; rotas thin.

## Critérios de aceite
- [ ] `uvicorn` sobe; `GET /health` = 200.
- [ ] No startup, os 6 CSVs são carregados; `get_state()` retorna DataFrames não vazios.
- [ ] `GET /eixos` retorna **5 eixos** com cidades ordenadas (Eixo 4 = Ipaporanga → Poranga → Ararendá).
- [ ] `GET /veiculos` retorna **3 veículos**; `MOTOS.selecionavel=false`; nome canônico `"HR / BONGO"` (I1).
- [ ] `GET /semanas` retorna `{ semanas:[1,2,3,4], padrao:4 }`.
- [ ] `frontend` builda (`vite build`) e `client.ts` consome os 3 endpoints em dev (`VITE_API_URL`).
- [ ] Dockerfile builda com WeasyPrint funcional (valida no PRD-06).

## Testes
- `test_state_bootstrap()` — carrega seed, valida shapes e nomes canônicos.
- `test_metadados_endpoints()` — 5 eixos / 3 veículos / semanas.

## Riscos
- CSV de rotas semi-estruturado (parse por índice frágil) — mitigar com testes sobre o arquivo real e tolerância a linhas em branco.
- Libs nativas do WeasyPrint no Docker — fixar base image que já traz Cairo/Pango.

## Ver também
[[arquitetura/visao_geral]] · [[arquitetura/backend]] · [[arquitetura/frontend]] · [[dados/dicionario]]
