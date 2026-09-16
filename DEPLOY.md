# Deploy — NobreLOG Optimizer

Arquitetura de deploy (ver [`docs/arquitetura/adr/0009_deploy_stateful.md`](docs/arquitetura/adr/0009_deploy_stateful.md)):

- **Backend** → **Render** (Docker, host stateful — WeasyPrint precisa de libs nativas; serverless não serve).
- **Frontend** → **Vercel** (estático Vite).

Os dois se acoplam por 2 variáveis: o front aponta para a URL do backend (`VITE_API_URL`) e o backend libera o domínio do front no CORS (`CORS_ORIGINS`).

---

## 0. Variáveis de ambiente — valores a definir

### Render (backend)
| Variável | Valor a definir | Obrigatória? |
|----------|-----------------|:---:|
| `CORS_ORIGINS` | URL(s) do front na Vercel, ex.: `https://SEU-PROJETO.vercel.app` (várias separadas por vírgula) | **Sim** |
| `USE_SEED_DATA` | `true` usa os CSVs seed (mock/demo, já na imagem) · `false` inicia vazio e exige upload | Não |
| `LLM_PROVIDER` | `anthropic` (default) **ou** `nvidia` | Não |
| `LLM_MODEL` | Anthropic: `claude-haiku-4-5` · NVIDIA: id do catálogo (ex.: `nvidia/llama-3.1-nemotron-ultra-253b-v1`) | Não |
| `LLM_API_KEY` | A chave do LLM — Anthropic `sk-ant-…` **ou** NVIDIA `nvapi-…` | Só p/ ativar IA |
| `ANTHROPIC_API_KEY` | Alternativa à `LLM_API_KEY` (o código cai para ela) | Não |
| `LLM_BASE_URL` | Só p/ NVIDIA: `https://integrate.api.nvidia.com/v1` (já é o default) | Não |
| `OCUPACAO_MINIMA` | `0.6` (limiar do alerta de frete mínimo) | Não |
| `SOLVER_TIME_LIMIT` | `30` | Não |
| `LOTE_ANO` | `2026` | Não |
| `PYTHONUNBUFFERED` | `1` | Não |
| `PORT` / `DATA_DIR` | **NÃO definir** — `PORT` é injetado pelo Render; `DATA_DIR` já é `/app/data` | — |

### Dados: seed (mock) vs upload, e ciclo de vida
- Os **7 CSVs seed já vão na imagem** (`backend/data/`), então o Render **tem os dados** — o caso oficial roda no boot.
- `USE_SEED_DATA=true` (default): usa esse seed como mock/demo. `false`: começa vazio e o usuário importa em **Importar** (`/etl/ingest`).
- **Sobrescrita/acúmulo:** cada upload substitui **só os arquivos enviados** e **mantém os anteriores** (ex.: subir só `semana_4` preserva 1–3 e o ranking; um novo upload de `ranking` depois preserva a `semana_4` já enviada).
- **Efêmero (ADR 0001):** os uploads vivem só enquanto o processo roda. **Reinício** do serviço volta ao seed (ou vazio). No Render Free, o *spin-down* também reseta. Para reter uploads/histórico entre reinícios → banco de dados ([`docs/arquitetura/adr/0010_persistencia_opcional.md`](docs/arquitetura/adr/0010_persistencia_opcional.md)).

### Vercel (frontend)
| Variável | Valor a definir | Escopo |
|----------|-----------------|--------|
| `VITE_API_URL` | URL do backend no Render, ex.: `https://nobrelog-backend.onrender.com` (sem barra no fim) | Production (e Preview) |

> `VITE_API_URL` é **build-time** (o Vite embute no bundle) — após mudar, **redeploy**.

### Usar NVIDIA NIM (nemotron) em vez de Anthropic
O NVIDIA NIM é **compatível com a API da OpenAI**, não com a da Anthropic — por isso não basta trocar a chave. Configure:
```
LLM_PROVIDER=nvidia
LLM_API_KEY=nvapi-…                 # (ou coloque em ANTHROPIC_API_KEY — o código reusa)
LLM_BASE_URL=https://integrate.api.nvidia.com/v1
LLM_MODEL=<id do modelo no catálogo NVIDIA>   # confirme em https://build.nvidia.com
```
> ⚠️ Confirme o **id exato** do modelo em https://build.nvidia.com (ex.: `nvidia/llama-3.1-nemotron-ultra-253b-v1`). O nome que você citou (`nemotron-3-ultra-550b-a55b`) precisa ser validado no catálogo — use o slug exato que a NVIDIA lista lá.

---

## 1. Backend no Render (Docker)

Arquivos já prontos no repo: [`backend/Dockerfile`](backend/Dockerfile), [`backend/requirements.txt`](backend/requirements.txt), [`render.yaml`](render.yaml) (Blueprint).

### Opção A — Blueprint (recomendado)
1. No Render: **New → Blueprint** e conecte este repositório.
2. O Render lê o `render.yaml` e cria o serviço `nobrelog-backend` (Docker, plano free, health check em `/health`).
3. Em **Environment**, defina:
   - `CORS_ORIGINS` = URL do front na Vercel (ex.: `https://nobrelog.vercel.app`). Pode listar várias separadas por vírgula.
   - `ANTHROPIC_API_KEY` = (opcional) ativa `/insight`. Sem ela, `/insight` responde 503 (fallback).
4. Deploy. A URL final será algo como `https://nobrelog-backend.onrender.com`.

### Opção B — sem Blueprint
1. **New → Web Service** → conecte o repo.
2. **Runtime:** Docker · **Dockerfile Path:** `backend/Dockerfile` · **Docker Context:** `backend`.
3. **Health Check Path:** `/health`.
4. Adicione as env vars do passo 3 acima.

> O `$PORT` é injetado pelo Render; o container já faz `uvicorn --host 0.0.0.0 --port $PORT`.
> Os CSVs seed estão embutidos na imagem (`backend/data/`), então o caso oficial roda no boot.
> **Atenção (plano free):** o serviço "dorme" após inatividade e o estado in-memory (uploads via `/etl/ingest`) é perdido ao dormir/reiniciar, voltando ao seed. Para reter uploads/histórico, ver [`docs/arquitetura/adr/0010_persistencia_opcional.md`](docs/arquitetura/adr/0010_persistencia_opcional.md).

### Testar a imagem localmente (opcional)
```bash
docker build -t nobrelog-backend ./backend
docker run --rm -p 8000:8000 -e CORS_ORIGINS="http://localhost:5173" nobrelog-backend
curl localhost:8000/health
```

---

## 2. Frontend na Vercel (Vite)

Arquivo pronto: [`frontend/vercel.json`](frontend/vercel.json) (framework Vite + rewrites de SPA).

1. Na Vercel: **Add New → Project** → importe o repo.
2. **Root Directory:** `frontend` (importante — o projeto front está em subpasta).
3. Framework **Vite** é detectado; build `npm run build`, output `dist` (já no `vercel.json`).
4. **Environment Variables:**
   - `VITE_API_URL` = URL do backend no Render (ex.: `https://nobrelog-backend.onrender.com`).
   - ⚠️ É **build-time** (Vite embute no bundle) — após mudar, faça **redeploy**.
5. Deploy. A URL final (ex.: `https://nobrelog.vercel.app`) deve ser colocada no `CORS_ORIGINS` do backend (passo 1.3).

### `rewrites` (SPA)
O `vercel.json` já redireciona todas as rotas para `index.html`, para o roteamento client-side do React Router funcionar em refresh/deep-link.

---

## 3. Ordem de deploy (evita CORS quebrado)

1. Suba o **backend no Render** → anote a URL.
2. Suba o **frontend na Vercel** com `VITE_API_URL` = URL do backend → anote a URL.
3. Volte ao Render e ajuste `CORS_ORIGINS` = URL da Vercel → redeploy do backend.
4. Teste o fluxo: abrir o front, otimizar Eixo 4 + ACELLO, exportar o PDF.

---

## 4. Checklist de verificação pós-deploy
- [ ] `GET https://<backend>/health` → 200.
- [ ] Front carrega eixos/veículos (sem erro de CORS no console).
- [ ] `POST /otimizar` (Eixo 4 + ACELLO 815) reproduz 7 pedidos / 4.797,335 kg / PESO.
- [ ] Exportar PDF do romaneio funciona.
- [ ] (Se configurada a chave) bloco de IA gera insight; senão, recolhe silenciosamente.

## Notas
- Alternativas de host stateful além do Render: Railway, Fly.io, ou qualquer VPS com Docker — o `Dockerfile` é o mesmo.
- Não comitar `.env` (já no `.gitignore`). Use os `.env.example` como referência.
