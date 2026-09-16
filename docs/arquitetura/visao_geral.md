# Arquitetura — Visão Geral

## Diagrama de contexto

```
┌──────────────────────┐            HTTP/JSON            ┌────────────────────────┐
│  Frontend            │◄────────────────────────────────►│  Backend               │
│  React + TypeScript  │                                  │  FastAPI (Python 3.11) │
│  Vite + Tailwind     │                                  │                        │
└──────────────────────┘                                  │  In-memory state       │
                                                          │  (Pandas DataFrames)   │
                                                          └───────────┬────────────┘
                                                                      │ boot
                                                          ┌───────────▼────────────┐
                                                          │  backend/data/*.csv    │
                                                          │  (versionados no repo) │
                                                          └────────────────────────┘

                        Componentes internos do backend
                        ────────────────────────────────
                        etl → cubagem → optim (PuLP/CBC)
                                        ↓
                                    romaneio (WeasyPrint)
                                        ↓
                                    llm (opcional)
```

## Stack

| Camada         | Tecnologia                    | Justificativa curta                                      |
|----------------|-------------------------------|----------------------------------------------------------|
| Frontend       | React 18 + TypeScript + Vite  | Rápido para prototipar, tipagem forte, DX no hackathon   |
| Estilo         | Tailwind CSS                  | Utility-first, sem lock-in de UI kit                     |
| Componentes    | shadcn/ui (opcional)          | Boa base acessível, quando necessário                    |
| Backend        | FastAPI                       | Docs OpenAPI grátis, tipagem Pydantic, hot reload        |
| Processamento  | Pandas                        | Padrão do ecossistema para ETL tabular                   |
| Solver         | PuLP + CBC                    | Ver [[arquitetura/adr/0003_solver_pulp]]                 |
| PDF            | WeasyPrint                    | Ver [[arquitetura/adr/0004_pdf_backend]]                 |
| LLM (opcional) | Provedor a definir            | Ver [[arquitetura/adr/0007_motor_hibrido_llm]]           |

## Boot in-memory

Ver [[arquitetura/adr/0001_sem_banco_de_dados]]. Fluxo:

1. FastAPI `startup` event lê 4 CSVs semanais + Ranking Top 85 + Rotas/Coletas.
2. ETL normaliza tudo em `pandas.DataFrame` na variável de módulo `src/state.py`.
3. Cubagem é calculada uma vez e mantida em memória.
4. Rotas leem do estado, nunca do disco (exceto no upload de re-ingestão).

Reingestão (via upload) substitui o estado em memória. Não persiste em disco entre reinícios.

## Fluxo de request típico

```
POST /otimizar { eixo, veiculo, semana }
    ↓
api/routes/otimizar.py           # rota thin
    ↓
optim/solver.py::otimizar(...)   # função pura
    ↓                            #  ├─ lê state.pedidos_processados
    ↓                            #  ├─ monta modelo PuLP
    ↓                            #  ├─ resolve CBC
    ↓                            #  └─ retorna PlanoDeCarga (Pydantic)
    ↓
response JSON
```

## Princípios arquiteturais

1. **Funções puras primeiro.** Todo módulo de domínio (`etl/`, `cubagem/`, `optim/`) roda sozinho por script, sem FastAPI.
2. **Rotas thin.** `api/routes/*.py` só orquestra: valida input Pydantic, chama função pura, formata resposta.
3. **State como singleton.** `src/state.py` carrega uma vez, expõe DataFrames imutáveis (ou snapshots).
4. **Sem side-effect no domínio.** Domínio não escreve em disco, não faz HTTP, não lê env. Isso vive nas bordas.
5. **Logs de qualidade rastreáveis.** Toda transformação vira uma entrada estruturada em `state.log_correcoes`.

## Diagramas relacionados

- [[arquitetura/backend]] — estrutura de pacotes
- [[arquitetura/frontend]] — estrutura React
- [[dominio/pipeline_etl]] — o que roda no ETL
- [[dominio/otimizacao]] — o que roda no solver
