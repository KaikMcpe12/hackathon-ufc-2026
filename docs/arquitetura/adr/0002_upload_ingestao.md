# ADR 0002 — Upload de re-ingestão de CSVs

**Status:** Aceita
**Data:** 2026-09-16

## Contexto

Os CSVs em `backend/data/` são a fonte de verdade padrão. Mas durante a demonstração (e em piloto) o coordenador pode querer subir novos CSVs sem recompilar/reimplantar.

## Decisão

Existe o endpoint `POST /etl/ingest` que aceita upload multipart dos CSVs (semanas 1–4, Ranking, Rotas). O handler:

1. Valida colunas esperadas.
2. Roda o pipeline ETL completo em memória.
3. Substitui o `state` singleton.
4. **Não** grava arquivos em disco.

Comportamento:
- Reinício do servidor volta aos CSVs versionados em `backend/data/`.
- Upload parcial (só uma semana) mantém as outras semanas do estado atual.

## Consequências

**Positivas:**
- Demo pode simular semana nova.
- Piloto pode ajustar dados sem envolver time técnico.

**Negativas:**
- Nenhuma auditoria de quem subiu o quê (aceitável no MVP).
- Sem autenticação — qualquer um com URL pode reingerir. Aceito para o hackathon.

## Alternativas descartadas

- **Persistir upload em disco:** confundiria a fonte de verdade (data/ vs. upload).
- **Só CLI:** perde o valor demonstrativo.

## Ver também

- [[api/endpoints]]#etl_ingest
- [[dominio/pipeline_etl]]
