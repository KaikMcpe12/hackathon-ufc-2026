# PRD-02 — Pipeline ETL

> **Status:** proposto. Depende de: [[prd/01-fundacao-deploy]], [[prd/00-errata-decisoes]].
> Transforma os CSVs brutos em pedidos elegíveis e normalizados, com log rastreável. Alvo: **688 → 93**.

## Objetivo

Implementar as etapas 1–4 e 7 de [[dominio/pipeline_etl]] como **funções puras** em `src/etl/`, rodáveis por script, produzindo `state.pedidos_processados` (sem cubagem ainda) e `state.log_correcoes`.

## Escopo

**Dentro:**
- **Carregar** (`loader.py`): lê os 6 CSVs, detecção de separador (`;`/`,`), encoding UTF-8-BOM, concatena 4 semanas com coluna `semana`.
- **Normalizar** (`normalizer.py`): snake_case; `valor_pedido` BR→float; `data` multi-formato → `datetime`; `cidade` uppercase + sem acento (guarda original); `situacao`/`logistica` uppercase.
- **Filtrar** (`filters.py`): remover cancelados → retiradas balcão → Crateús → cidade fora de eixo, **nessa ordem**, com contagem por motivo (I6/I8).
- **Corrigir** (`correcoes.py`): data fora do lote → ano de referência (só se dia/mês plausíveis); cidades divergentes (`NOVA RUSSAS `, `IPAPORAGA`) via dicionário controlado; valor ausente em campo obrigatório → fila de exceção. Cada correção vira `Correcao` no log.
- **Log** (`log.py`): estrutura `Correcao` com `acao` (E5).
- **Publicar** (`state.py`): monta `pedidos_processados` (colunas de [[dominio/pipeline_etl]] §7, `peso_kg`/`volume_m3` ainda vazios até PRD-03).
- Endpoints: `GET /qualidade/log`, `GET /qualidade/motivos-exclusao`.

**Fora:** cubagem/selos (PRD-03), `/qualidade/resumo` completo (PRD-05 usa contagens desta fase + PRD-03).

## Contratos / estruturas

`Correcao` (de [[api/contratos]] + E5):
```
pedido, campo, valor_original (cru), valor_novo (ISO se data — I2),
regra, criterio, acao ∈ {CORRIGIDA,SINALIZADA,ESTIMADO,PADRONIZADA}, aplicada_em (ISO)
```

Mapa `regra → acao` (inicial): `ano_fora_do_lote→CORRIGIDA` · `cidade_trailing_space→PADRONIZADA` · `cidade_typo→PADRONIZADA` · `campo_obrigatorio_ausente→SINALIZADA` · (sintéticos `sintetico:*→ESTIMADO` entram no PRD-03).

`motivo_exclusao` enum canônico (I6): `CANCELADO`, `RETIRADA_BALCAO`, `CRATEUS`, `CIDADE_FORA_EIXO` (+ `CUBAGEM_AUSENTE`/`DATA_INCONSISTENTE` de outras etapas).

## Regras invioláveis (Charter)
- Nenhuma correção silenciosa — tudo em `log_correcoes` (§3.3).
- Valor ausente não é adivinhado; vai para fila de exceção.
- Ordem de filtros fixa; contagem separada por motivo.

## Critérios de aceite
- [ ] **688** registros carregados (soma das 4 semanas).
- [ ] Após filtros: **93** pedidos elegíveis (aproximado — ver [[entrega/criterios_aceite]]).
- [ ] `"R$ 1.811,87"` → `1811.87`; `"NOVA RUSSAS "` → `"NOVA RUSSAS"`.
- [ ] Data `26/08/2014` → `2026-08-26` **com** entrada no log (`acao=CORRIGIDA`, `valor_novo` ISO).
- [ ] `GET /qualidade/motivos-exclusao` soma = total de excluídos (≈595), 1 motivo por pedido na ordem canônica (I8).
- [ ] `GET /qualidade/log` retorna as correções aplicadas.

## Testes (de [[entrega/criterios_aceite]])
`test_filtra_cancelados`, `test_filtra_retiradas`, `test_filtra_crateus`, `test_normaliza_valor_brasileiro`, `test_corrige_data_fora_lote`, `test_log_correcoes_populado`, `test_motivos_exclusao_soma_total`.

## Riscos
- Parse de `data` multi-formato (`dd/mm/yy` vs `dd/mm/yyyy`) — usar `dayfirst=True` e validação de plausibilidade.
- Dicionário de cidades divergentes precisa cobrir os casos reais — construir a partir do CSV real e do glossário.

## Ver também
[[dominio/pipeline_etl]] · [[dados/dicionario]] · [[dados/glossario]]
