# PRD-09 — Re-ingestão, Testes & Aceite

> **Status:** proposto. Depende de: [[prd/02-pipeline-etl]] … [[prd/06-romaneio]].
> Fecha o ciclo: upload em runtime + suíte de testes que valida o MVP e trava PRs.

## Objetivo

Implementar `POST /etl/ingest` (backend do fluxo de upload de E2) e a suíte automatizada de [[entrega/criterios_aceite]], com o gate do caso oficial travando PR.

## Escopo

**Dentro:**
- `POST /etl/ingest` (multipart: `semana_1..4`, `ranking`, `rotas`, todos opcionais):
  1. valida colunas esperadas (400 se ausentes);
  2. roda o pipeline (PRD-02/03) sobre os arquivos enviados;
  3. substitui o singleton `state` (só os arquivos enviados; demais mantêm o estado atual — [[arquitetura/adr/0002_upload_ingestao]]);
  4. retorna `IngestResumo` (`{ semanas_atualizadas, resumo_qualidade }`).
- `state.reingest(files)` — reprocessa em memória, sem gravar em disco.
- **Suíte pytest** completa: `test_etl.py`, `test_cubagem.py`, `test_optim.py`, `test_api.py`, `test_romaneio.py`, `test_llm.py`.
- **Gate:** `test_caso_oficial_eixo4_acello()` bloqueia PR.
- Verificação de métricas RNF (tempo `/otimizar` < 3s; zero violações).
- CI simples (rodar pytest + ruff + mypy).

**Fora:** UI de importação (PRD-08).

## Regras invioláveis (Charter §7)
- Antes de qualquer PR: testes do módulo passam; caso oficial reproduz; nenhum `TODO` sem ADR/issue; `qualidade/log` continua registrando.

## Critérios de aceite
- [ ] `POST /etl/ingest` com só `semana_4` substitui a semana 4 e mantém 1–3; retorna `IngestResumo`.
- [ ] Colunas ausentes → 400.
- [ ] Após reingest, `/otimizar` usa os novos dados (validado em host stateful — não serverless, [[arquitetura/adr/0009_deploy_stateful]]).
- [ ] `pytest` verde; `test_caso_oficial_eixo4_acello` reproduz 7 / 4.797,335 / 2,4421 / PESO / 0 / 16.770,85 (±0,01).
- [ ] `/otimizar` do caso oficial < 3s (log FastAPI).
- [ ] Restart do backend volta ao seed de `backend/data/`.

## Testes
Todos os de [[entrega/criterios_aceite]] §"Testes automatizados obrigatórios" + `test_ingest_parcial()`, `test_ingest_colunas_invalidas()`, `test_ingest_substitui_estado()`.

## Riscos
- Upload parcial e consistência de eixos/ranking entre semanas — validar cruzamentos após reingest.
- Gate frágil se os dados reais mudarem — manter tolerância ±0,01 e ordem de investigação documentada.

## Ver também
[[entrega/criterios_aceite]] · [[arquitetura/adr/0002_upload_ingestao]] · [[arquitetura/adr/0009_deploy_stateful]]
