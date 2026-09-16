# PRD-10 — Pós-MVP: Integração Vendas_Faturamento + Multi-eixo + Deploy Render

> **Status:** Proposto
> **Depende de:** [[prd/09-reingestao-testes]] (MVP completo validado)
> **Objetivo:** Evoluir o MVP para operação real na Nobre Lar — integrar dado bruto oficial, resolver o desafio bônus multi-eixo e configurar deploy no Render.

---

## 1. Contexto

O MVP atende 100% ao escopo obrigatório do hackathon (caso oficial: Eixo 4 + ACELLO 815 + Semana 4 → 99,94% peso, 99,50% vol, 0 violações). A Diretoria de Operações sinalizou implantação piloto. Três lacunas impedem uso diário real:

| Lacuna | Impacto | Prioridade |
|--------|---------|------------|
| **Vendas_Faturamento_Entregas.csv** não integrado | Não valida se pedido "Faturado" realmente saiu para entrega; não cruza status entrega (ENTREGUE/PENDENTE) com planejamento | Alta |
| **Multi-eixo** (bônus do desafio) | 4 caminhões para 5 eixos — hoje roda 1 eixo por vez; coordenador decide manualmente qual veículo vai a qual eixo | Alta |
| **Deploy Render** | Backend stateful precisa de host com processo contínuo + WeasyPrint; front na Vercel | Alta |

**Regra de negócio:** Persistência em banco de dados **fora do escopo** (ver [[arquitetura/adr/0010_persistencia_opcional]]). Estado continua in-memory com re-ingestão via upload.

---

## 2. Entregas (In Scope)

### 2.1 Integração `Vendas_Faturamento_Entregas.csv` (RF-Novo)

**Arquivo oficial:** `DADOS DE ENTREGAS  - Vendas_Faturamento_Entregas.csv` (~108k linhas, 3.236+ pedidos únicos)

**Colunas relevantes:**
| Coluna | Tipo | Uso |
|--------|------|-----|
| `Pedido` | string | Chave de join com `Pedidos_Filtrados_Semana_X` |
| `Situacao` | string | `FATURADO`, `CANCELADO`, etc. |
| `Situacao_CSV_Entrega` | string | `ENTREGUE`, `PENDENTE`, `EM ROTA`, `TRANSFERIDO` |
| `Data` | date | Data de emissão/faturamento |
| `Cidade` | string | Validação cruzada de rota |
| `Logistica` | string | Tipo de entrega (NORMAL, URGENTE, RETIRADA) |

**Regras de negócio:**
1. **Validação de elegibilidade real:** Só entra no solver pedidos com `Situacao = FATURADO` **E** `Situacao_CSV_Entrega IN (ENTREGUE, PENDENTE, EM ROTA)` — exclui `CANCELADO`, `RETIRADA`, `TRANSFERIDO` (já filtrado no ETL atual, mas agora com fonte primária).
2. **Deduplicação:** Mesmo `Pedido` pode aparecer múltiplas vezes (histórico de status). Usar **último status por data** (mais recente vence).
3. **Cruzamento com pedidos filtrados:** `Pedidos_Filtrados_Semana_X` já trazem itens + cidade. O join enriquece com status real de entrega/faturamento.
4. **Log de divergências:** Se `Pedidos_Filtrados` tem cidade X mas `Vendas_Faturamento` tem cidade Y → log em `qualidade/log` com código `CIDADE_DIVERGENTE`.

**Módulos afetados:**
- `src/etl/loader.py` → nova função `carregar_vendas_faturamento(data_dir)`
- `src/etl/normalizer.py` → normalização das colunas acima
- `src/etl/pipeline.py` → etapa extra pós-filtro: `enriquecer_com_vendas_faturamento(elegiveis, vendas_df)`
- `src/etl/filters.py` → filtro adicional `validar_status_entrega_faturamento`

**Contrato de saída (adiciona colunas em `pedidos_processados`):**
| Coluna | Tipo | Descrição |
|--------|------|-----------|
| `status_faturamento` | string | `FATURADO` / `CANCELADO` / etc. |
| `status_entrega` | string | `ENTREGUE` / `PENDENTE` / `EM ROTA` / `TRANSFERIDO` |
| `data_faturamento` | date | Data do faturamento |
| `divergencia_cidade` | bool | True se cidade difere entre fontes |

---

### 2.2 Otimização Multi-eixo (Desafio Bônus)

**Problema:** 5 eixos fixos, 4 veículos (HR/BONGO, ACELLO 815, 2× MÉDIO — Moto fora do escopo). Decidir **qual veículo vai a qual eixo** + **quais pedidos entram em cada veículo** para maximizar ocupação global.

**Modelo matemático:** **Multiple Knapsack Problem (MKP)** com restrições de eixo.
- 4 knapsacks (veículos), cada um com `(cap_peso, cap_vol)`
- Itens = pedidos, agrupados por eixo (um pedido pertence a exatamente 1 eixo)
- Variável de decisão: `x[i][v] ∈ {0,1}` = pedido i alocado no veículo v
- Restrição: se pedido i é do eixo E, só pode ir em veículo v **se** v for designado ao eixo E
- Cada veículo atende **no máximo 1 eixo** por dia (operação real)
- Objetivo: maximizar soma ponderada `Σ (0.5·Op_v + 0.5·Ov_v)` sobre os 4 veículos

**Abordagem em duas fases (pragmática para hackathon):**

#### Fase A — Designação Veículo → Eixo (heurística gulosa + busca local)
1. Para cada eixo, calcular **demanda total** (peso + volume dos pedidos elegíveis)
2. Para cada veículo, calcular **fit score** por eixo: `min(demanda_peso/cap_peso, demanda_vol/cap_vol)` — quanto da capacidade seria usada
3. Atribuição gulosa: parear eixo com melhor fit score, remover veículo e eixo, repetir
4. Busca local (2-opt): trocar designações de 2 veículos se melhora ocupação global

#### Fase B — Solver por eixo (reutiliza solver mono-eixo atual)
- Para cada par (eixo, veículo designado), rodar solver MILP existente (`src/optim/solver.py`)
- Retorna 4 planos de carga independentes

**Alternativa avançada (se tempo permitir):** MKP único com PuLP — variáveis `x[i][v]` + restrição `x[i][v] = 0 se eixo(i) != eixo(v)`. Mais elegante mas ~10x mais lento.

**Módulos novos:**
- `src/optim/multi_eixo.py` — orquestra Fase A + Fase B
- `src/optim/designacao.py` — heurística de designação veículo→eixo
- `src/api/routes/multi_otimizar.py` — endpoint `POST /otimizar/multi-eixo`

**Contrato de resposta (`MultiPlanoDeCarga`):**
```json
{
  "planos": [
    { "eixo_id": 1, "veiculo": "HR / BONGO", "plano": PlanoDeCarga },
    { "eixo_id": 2, "veiculo": "ACELLO 815", "plano": PlanoDeCarga },
    ...
  ],
  "resumo_global": {
    "ocupacao_media_peso": 0.87,
    "ocupacao_media_volume": 0.82,
    "veiculos_ociosos": 0,
    "eixos_nao_atendidos": 1
  },
  "designacao_usada": "GULOSA_2OPT",
  "gerado_em": "2026-09-16T10:30:00Z"
}
```

**Frontend:** Nova tela `/multi-planejamento` (ou aba em `/simulacao`) — mostra 4 cards lado a lado + resumo global.

---

### 2.3 Deploy no Render

**Configuração (conforme [[arquitetura/adr/0009_deploy_stateful]]):**

| Componente | Configuração |
|------------|--------------|
| **Backend** | Render **Web Service** (não Static Site) — processo contínuo |
| **Frontend** | Render **Static Site** (ou Vercel) — build Vite |
| **Dockerfile** | Python 3.11-slim + `apt-get install -y libpango-1.0-0 libharfbuzz0b libpangocairo-1.0-0` (WeasyPrint) |
| **Start Command** | `uvicorn src.main:app --host 0.0.0.0 --port $PORT` |
| **Env Vars** | `DATA_DIR=/app/backend/data`, `CORS_ORIGINS=https://nobrelog-frontend.onrender.com`, `LOTE_ANO=2026`, `SOLVER_TIME_LIMIT=30` |
| **Health Check** | `GET /health` (path `/health`) |
| **Auto-Deploy** | On push to `main` (após validação em `feature/*`) |

**Arquivos a criar/atualizar:**
- `render.yaml` (Infrastructure as Code) — define os 2 serviços
- `backend/Dockerfile` — otimizado para Render (multi-stage se necessário)
- `.renderignore` — excluir `.venv`, `__pycache__`, `tests/`, `docs/`
- `frontend/.env.production` → `VITE_API_URL=https://nobrelog-backend.onrender.com`

**Observação:** Render Free tier tem *spin-down* após 15 min inatividade → cold start ~30s. Para demo, usar plano **Starter ($7/mês)** ou manter *ping* externo.

---

## 3. Fora do Escopo (Out of Scope)

- [ ] **Persistência em banco** (PostgreSQL/SQLite) — ver [[arquitetura/adr/0010_persistencia_opcional]]
- [ ] **Autenticação / Multi-usuário**
- [ ] **Mapas / Rotas geográficas / GPS**
- [ ] **Histórico de planos anteriores** (requer banco)
- [ ] **Previsão de demanda com ML**
- [ ] **App mobile**

---

## 4. Estratégia Git — Commit Passado + Branch Futura + Merge

### 4.1 Estado Atual (MVP Concluído)
```bash
# Branch atual: main (ou mvp-final)
# Todos os PRDs 00-09 implementados e testados
# 27 testes passing
# Caso oficial validado
```

### 4.2 Passo 1 — Commit do Estado MVP (Tag de Release)
```bash
git add -A
git commit -m "release: MVP completo — caso oficial Eixo4+ACELLO815 validado

- ETL: 688→93→81, log rastreável, selos 🟢39/🟡42/🔴0
- Cubagem: m²→caixas (ceil), ranking Top85 + sintéticas
- Solver MILP: 0.5·Op+0.5·Ov, hard constraints, 0 violações
- API: /otimizar <3s, /romaneio PDF, /etl/ingest, /qualidade
- Frontend: 5 telas, design system preto/branco/amarelo
- Testes: 27 passing (gate test_caso_oficial_eixo4_acello)

Closes: MVP criteria [[entrega/criterios_aceite]]"
git tag -a v1.0.0-mvp -m "MVP Hackathon UFC 2026 — NobreLOG Optimizer"
git push origin main --tags
```

### 4.3 Passo 2 — Branch de Evolução (`feature/pos-mvp`)
```bash
git checkout -b feature/pos-mvp
# Desenvolvimento das 3 frentes:
#   feature/pos-mvp/vendas-faturamento
#   feature/pos-mvp/multi-eixo
#   feature/pos-mvp/deploy-render
# Cada sub-branch com PR próprio para code review
```

### 4.4 Passo 3 — PRs Independentes por Frente

| PR | Branch | Título | Revisores |
|----|--------|--------|-----------|
| #1 | `feature/pos-mvp/vendas-faturamento` | feat: integrar Vendas_Faturamento_Entregas.csv no ETL | @logistica @backend |
| #2 | `feature/pos-mvp/multi-eixo` | feat: otimização multi-eixo (4 veículos × 5 eixos) | @operacoes @backend |
| #3 | `feature/pos-mvp/deploy-render` | chore: deploy Render + Dockerfile otimizado | @devops @backend |

**Regra:** Cada PR **deve passar nos 27 testes existentes** + novos testes da feature. CI bloqueia merge se falhar.

### 4.5 Passo 4 — Merge para `feature/pos-mvp` (Integração)
```bash
# Após 3 PRs aprovados e merged em feature/pos-mvp:
git checkout feature/pos-mvp
git pull
# Rodar suite completa
pytest backend/tests/ -v
npm run build --prefix frontend
# Testes manuais: multi-eixo + Vendas_Faturamento + deploy local Docker
```

### 4.6 Passo 5 — Decisão em Equipe + Merge para `main`
```bash
# Reunião de revisão: demo multi-eixo, validação Vendas_Faturamento, deploy staging
# Se aprovado:
git checkout main
git merge feature/pos-mvp --no-ff -m "merge: pós-MVP — Vendas_Faturamento + Multi-eixo + Render
- Vendas_Faturamento integrado: validação status entrega/faturamento
- Multi-eixo: designação gulosa + 2-opt + 4 solvers paralelos
- Render: Web Service backend + Static Site frontend
- Testes: 27 existentes + 12 novos passing"
git tag -a v1.1.0-pos-mvp -m "Pós-MVP: multi-eixo + dado bruto + deploy"
git push origin main --tags
```

### 4.7 Rollback Rápido (se necessário)
```bash
# Volta ao MVP estável em segundos
git checkout main
git reset --hard v1.0.0-mvp
git push origin main --force-with-lease
# Redeploy no Render (auto-deploy da tag ou manual)
```

---

## 5. Critérios de Aceite (Checklist)

### 5.1 Vendas_Faturamento
- [ ] `carregar_vendas_faturamento()` lê CSV oficial sem erro
- [ ] Join com `Pedidos_Filtrados` por `Pedido` funciona (chave única após dedup último status)
- [ ] Filtro `status_faturamento=FATURADO` + `status_entrega IN (ENTREGUE,PENDENTE,EM_ROTA)` aplicado
- [ ] Log de `CIDADE_DIVERGENTE` populado em `GET /qualidade/log`
- [ ] Pipeline ainda reproduz 688→93→81 (ou números ajustados e documentados)
- [ ] Caso oficial Eixo 4 + ACELLO 815 **continua passando** (regressão zero)

### 5.2 Multi-eixo
- [ ] Endpoint `POST /otimizar/multi-eixo` retorna `MultiPlanoDeCarga` válido
- [ ] 4 veículos designados a 4 dos 5 eixos (1 eixo fica sem veículo — esperado)
- [ ] Cada plano individual respeita peso/volume (0 violações)
- [ ] Ocupação média global > 80% na dimensão do gargalo
- [ ] Tempo de resposta < 10s (4 solvers sequenciais)
- [ ] Determinismo: mesma entrada → mesma designação + mesmos planos
- [ ] Frontend mostra 4 cards + resumo global

### 5.3 Deploy Render
- [ ] `render.yaml` válido — `render validate` passa
- [ ] Backend sobe no Render Free/Starter, `GET /health` = 200
- [ ] Frontend builda no Render Static Site (ou Vercel) e consome API
- [ ] WeasyPrint gera PDF no container (testar `POST /romaneio/generate`)
- [ ] CORS configurado para domínio do front
- [ ] Variáveis de ambiente documentadas no `README.md` seção Deploy

---

## 6. Testes Novos (Adicionar à Suite)

| Teste | Arquivo | Descrição |
|-------|---------|-----------|
| `test_vendas_faturamento_join()` | `test_etl.py` | Join por Pedido, dedup último status |
| `test_vendas_faturamento_filtro_status()` | `test_etl.py` | Só FATURADO + (ENTREGUE\|PENDENTE\|EM_ROTA) passa |
| `test_vendas_faturamento_divergencia_cidade()` | `test_etl.py` | Log `CIDADE_DIVERGENTE` gerado |
| `test_multi_eixo_designacao_gulosa()` | `test_optim.py` | 4 veículos → 4 eixos, 1 ocioso |
| `test_multi_eixo_zero_violacoes()` | `test_optim.py` | Todos os 4 planos respeitam capacidade |
| `test_multi_eixo_determinismo()` | `test_optim.py` | Mesma entrada → mesma saída |
| `test_multi_eixo_endpoint()` | `test_api.py` | `POST /otimizar/multi-eixo` 200 + schema válido |
| `test_render_dockerfile_build()` | `test_docker.py` (novo) | Dockerfile builda sem erro |
| `test_weasyprint_no_container()` | `test_romaneio.py` | PDF gerado no container Docker |

---

## 7. Riscos e Mitigações

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| `Vendas_Faturamento` tem chaves duplicadas não-resolvíveis | Média | Alto | Dedup por `Pedido + max(Data)` + log de conflitos |
| MKP único (PuLP) explode combinatoriamente | Alta | Médio | Usar heurística 2-fases (designação + solver por eixo) |
| Render Free tier spin-down quebra demo | Alta | Baixo | Plano Starter $7 ou ping externo (cron-job.org) |
| WeasyPrint falha no container Render | Média | Alto | Dockerfile testado localmente + `render.yaml` com `dockerCommand` customizado |
| Mudança de escopo da diretoria durante desenvolvimento | Média | Médio | PRs pequenos, revisão semanal, tag MVP imutável |

---

## 8. Referências e Wikilinks

- [[prd/09-reingestao-testes]] — MVP baseline (testes, gate, upload)
- [[entrega/criterios_aceite]] — Caso oficial Eixo 4 + ACELLO 815
- [[arquitetura/adr/0009_deploy_stateful]] — Decisão deploy stateful
- [[arquitetura/adr/0010_persistencia_opcional]] — Por que não banco agora
- [[dominio/pipeline_etl]] — Etapa 5 nova: enriquecimento Vendas_Faturamento
- [[dominio/otimizacao]] — Extensão para multi-eixo (MKP)
- [[dados/dicionario]] — Dicionário de dados (atualizar com Vendas_Faturamento)
- [[produto/requisitos]] — RF-Novo: RF31, RF32, RF33 (multi-eixo, Vendas_Faturamento, deploy)

---

## 9. Próximos Passos Imediatos

1. **Aprovação deste PRD** pela equipe (async ou sync)
2. **Criar branch `feature/pos-mvp`** e sub-branches
3. **PR #1 (Vendas_Faturamento)** — menor risco, valida dado bruto
4. **PR #3 (Deploy Render)** — pode ser paralelo, desbloqueia staging
5. **PR #2 (Multi-eixo)** — maior complexidade, faz por último
6. **Demo integrada** em `feature/pos-mvp` → decisão → merge `main`

---

## 10. Decisões Pendentes (Perguntas para a Equipe)

1. **Vendas_Faturamento**: Usar **último status por data** como regra de dedup, ou há regra de negócio específica (ex.: primeiro faturamento vence)?
2. **Multi-eixo**: Aceitar que 1 eixo ficará sem veículo (4 veículos × 5 eixos), ou permitir que um veículo faça 2 eixos em dias alternados (fora do escopo diário)?
3. **Render**: Confirmar plano **Starter ($7/mês)** para evitar spin-down, ou Free tier com ping externo é aceitável?
4. **Frontend multi-eixo**: Nova rota `/multi-planejamento` ou aba dentro de `/simulacao`?
5. **Nomenclatura tag**: `v1.1.0-pos-mvp` ou `v2.0.0` (breaking change semântica)?

---

*Documento versão 1.0 — 2026-09-16 — Para revisão da equipe antes de iniciar implementação.*