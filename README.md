# NobreLOG Optimizer

Sistema de otimização de carga de caminhões para o Grupo Nobre Lar (Crateús-CE).
Recebe eixo + veículo e devolve o **plano de carga** que maximiza a ocupação física
**sem** violar peso ou volume, com romaneio em PDF e explicabilidade.

> Documentação completa em [`docs/`](docs/README.md). Comece por [`docs/AGENT_CHARTER.md`](docs/AGENT_CHARTER.md)
> e pelos PRDs de execução em [`docs/prd/`](docs/prd/README.md).

## Arquitetura

- **Backend:** Python · FastAPI · Pandas · PuLP (CBC) · WeasyPrint. Estado in-memory (sem banco).
- **Frontend:** React + TypeScript · Vite · Tailwind.
- **Deploy:** backend em host stateful + frontend na Vercel (ver `docs/arquitetura/adr/0009_deploy_stateful.md`).

## Como rodar

### Backend (porta 8000)
```bash
cd backend
python -m venv .venv && . .venv/bin/activate
pip install fastapi "uvicorn[standard]" pandas pulp pydantic python-multipart jinja2 weasyprint
uvicorn src.main:app --reload --port 8000
```

### Frontend (porta 5173)
```bash
cd frontend
npm install
npm run dev
```
Abra http://localhost:5173.

### Testes (inclui o gate que bloqueia PR)
```bash
cd backend && . .venv/bin/activate && pytest
```

## Caso oficial de aceite (gate)

`Eixo 4 (Ipaporanga → Poranga → Ararendá) + ACELLO 815`, sobre os CSVs reais em `backend/data/`:

| Indicador | Esperado | Status |
|-----------|----------|:------:|
| Pedidos selecionados | 7 | ✅ |
| Peso | 4.797,335 / 4.800 kg (99,94%) | ✅ |
| Volume | 2,4421 / 2,4543 m³ (99,50%) | ✅ |
| Gargalo | PESO | ✅ |
| Violações | 0 | ✅ |
| Valor | R$ 16.770,85 | ✅ |

Pipeline validado contra o protótipo: **688 → 93 (pós-situação) → 81 (pool)**; selos 🟢39 / 🟡42 / 🔴0.

## Endpoints (base `/api/v1`)

`GET /eixos · /veiculos · /semanas · /pedidos · /qualidade/{resumo,log,motivos-exclusao}`
`POST /otimizar · /otimizar/comparar · /romaneio/generate (PDF) · /insight · /etl/ingest`
