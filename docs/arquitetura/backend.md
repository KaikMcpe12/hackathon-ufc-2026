# Arquitetura — Backend

## Estrutura de pastas

```
backend/
├── data/                                  # CSVs versionados
│   ├── pedidos_semana_1.csv
│   ├── pedidos_semana_2.csv
│   ├── pedidos_semana_3.csv
│   ├── pedidos_semana_4.csv
│   ├── ranking_top85.csv
│   └── rotas_coletas.csv
├── pyproject.toml                         # deps + config
├── src/
│   ├── __init__.py
│   ├── main.py                            # entrypoint FastAPI
│   ├── state.py                           # singleton in-memory
│   ├── models/                            # Pydantic
│   │   ├── pedido.py
│   │   ├── item.py
│   │   ├── veiculo.py
│   │   ├── eixo.py
│   │   ├── plano_carga.py
│   │   └── qualidade.py
│   ├── etl/                               # funções puras
│   │   ├── loader.py                      # lê CSVs
│   │   ├── normalizer.py                  # normaliza colunas
│   │   ├── filters.py                     # elegibilidade
│   │   ├── correcoes.py                   # datas, cidades
│   │   └── log.py                         # log rastreável
│   ├── cubagem/
│   │   ├── calculadora.py                 # peso/volume por item
│   │   ├── conversor.py                   # m² → caixas
│   │   ├── classificador.py               # 🟢🟡🔴
│   │   └── sintetico.py                   # estimativas marcadas
│   ├── optim/
│   │   ├── modelo.py                      # monta PuLP
│   │   ├── solver.py                      # resolve CBC
│   │   ├── gargalo.py                     # PESO vs VOLUME
│   │   └── explicabilidade.py             # motivos de rejeição
│   ├── romaneio/
│   │   ├── template.html                  # template WeasyPrint
│   │   └── gerador.py                     # renderiza PDF
│   ├── llm/                               # opcional
│   │   ├── client.py
│   │   └── prompt.py
│   └── api/
│       ├── deps.py
│       └── routes/
│           ├── eixos.py                   # GET /eixos
│           ├── veiculos.py                # GET /veiculos
│           ├── semanas.py                 # GET /semanas
│           ├── pedidos.py                 # GET /pedidos
│           ├── qualidade.py               # GET /qualidade/*
│           ├── otimizar.py                # POST /otimizar
│           ├── romaneio.py                # POST /romaneio/generate
│           ├── etl.py                     # POST /etl/ingest
│           └── llm.py                     # POST /insight
└── tests/
    ├── test_etl.py
    ├── test_cubagem.py
    ├── test_optim.py
    └── test_api.py
```

## Camadas

```
┌─────────────────────────────────────────┐
│  api/routes/         (thin, orquestra)  │
├─────────────────────────────────────────┤
│  models/             (Pydantic)         │
├─────────────────────────────────────────┤
│  optim/  romaneio/  llm/                │  ← funções puras
├─────────────────────────────────────────┤
│  cubagem/            (funções puras)    │
├─────────────────────────────────────────┤
│  etl/                (funções puras)    │
├─────────────────────────────────────────┤
│  state.py            (singleton)        │
├─────────────────────────────────────────┤
│  data/               (CSVs versionados) │
└─────────────────────────────────────────┘
```

## `state.py` — o singleton in-memory

Interface esperada:

```python
# src/state.py
import pandas as pd
from typing import NamedTuple

class AppState(NamedTuple):
    pedidos_raw: pd.DataFrame          # 4 semanas concatenadas + coluna semana
    pedidos_processados: pd.DataFrame  # pós-ETL + cubagem + classificação
    ranking: pd.DataFrame              # Top 85
    veiculos: pd.DataFrame             # HR/BONGO, ACELLO, MOTOS
    eixos: pd.DataFrame                # 1..5 com cidades ordenadas
    log_correcoes: list[dict]          # log rastreável

_state: AppState | None = None

def get_state() -> AppState:
    global _state
    if _state is None:
        raise RuntimeError("state não inicializado — chame bootstrap() no startup")
    return _state

def bootstrap(data_dir: str) -> None: ...
def reingest(files: dict[str, bytes]) -> AppState: ...
```

Rotas usam `Depends(get_state)`.

## Endpoints — thin rules

Cada rota segue:

```python
@router.post("/otimizar", response_model=PlanoDeCarga)
def otimizar_rota(
    req: OtimizarRequest,
    state: AppState = Depends(get_state),
) -> PlanoDeCarga:
    return otimizar(
        pedidos=state.pedidos_processados,
        eixo_id=req.eixo,
        veiculo=state.veiculos.loc[req.veiculo],
        semana=req.semana,
    )
```

Nenhuma regra de negócio dentro da rota. Se aparecer, refatorar.

## Testes por script

Todo módulo do domínio deve rodar sem FastAPI:

```bash
python -m src.etl.loader        # carrega e imprime shape
python -m src.cubagem.calculadora  # roda cubagem sobre 1 semana
python -m src.optim.solver      # otimiza eixo 4 + ACELLO 815 → bate caso oficial?
```

Isso é testável em CI sem subir servidor.

## Dependências principais

```toml
[project]
dependencies = [
  "fastapi>=0.110",
  "uvicorn[standard]>=0.27",
  "pandas>=2.2",
  "pulp>=2.8",              # solver
  "pydantic>=2.6",
  "weasyprint>=61",         # PDF
  "python-multipart",       # upload
  "jinja2",                 # template do PDF
]

[dependency-groups]
dev = ["pytest", "ruff", "mypy"]
llm = ["openai"]            # opcional, para camada de insights
```

## Configuração

- `.env` para chaves opcionais (LLM). Nunca comitar.
- `CORS_ORIGINS` liberado para `http://localhost:5173` (Vite) em dev.
- Nada de secrets no código.

## Ver também

- [[dominio/pipeline_etl]] — o que o `etl/` faz
- [[dominio/otimizacao]] — o que o `optim/` faz
- [[api/endpoints]] — rotas expostas
- [[api/contratos]] — schemas Pydantic
