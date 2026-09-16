# Dicionário de Dados

Documenta os 6 CSVs de entrada tal como chegam da empresa (com sujeira). Cada tabela mostra a coluna original, o tipo esperado, o tipo real observado e a regra de normalização/transformação.

## 1. `Pedidos_Filtrados_Semana_N_Anonimizado.csv` (4 arquivos, N = 1..4)

Separador: `;` · Encoding: UTF-8 com BOM · ~150–200 linhas cada.

| Coluna original          | Tipo esperado | Realidade                                | Regra                                                  |
|--------------------------|---------------|------------------------------------------|--------------------------------------------------------|
| `Pedido`                 | str           | `L12608278`                              | Chave. Manter.                                         |
| `Data`                   | date          | `01/08/2026` (dd/mm/yyyy)                | Parse com `dayfirst=True`.                             |
| `Vendedor`               | str           | `LEONARDO`, `CAMILA`                     | Manter.                                                |
| `Situacao`               | str           | `Faturado`, `Cancelado`, `Separacao`     | Uppercase.                                             |
| `Cidade`                 | str           | `CRATEUS`, `IPAPORANGA`, `NOVA RUSSAS`   | Uppercase, remover acentos e trailing spaces.          |
| `Logistica`              | str           | `ENTREGUE`, `ENTREGA`                    | Uppercase.                                             |
| `Situacao_CSV_Entrega`   | str           | `RETIRADA`, vazio, outros                | Uppercase. `RETIRADA` filtra.                          |
| `Valor_Pedido`           | float         | `"R$ 1.811,87"` (string BR)              | Remove `R$`, ponto de milhar, troca `,` por `.`.       |
| `Qtd_Itens`              | int           | `1`, `24`                                | Parse int.                                             |
| `Itens_Resumo`           | str livre     | `"14900 - ARGAMASSA... (7,00 UN);..."`    | Parse por regex. Ver [[dominio/cubagem]]#parse.        |

## 2. `Ranking_Top85_Materiais.csv`

Separador: `;` · Encoding: UTF-8 com BOM · 85 linhas.

| Coluna original      | Tipo esperado | Realidade                               | Regra                                                |
|----------------------|---------------|------------------------------------------|------------------------------------------------------|
| `Rank`               | int           | 1–85                                     | Ignorar.                                             |
| `Codigo`             | str           | `14900`                                  | Chave de cruzamento com pedidos.                     |
| `Produto`            | str           | Descrição comercial                      | Manter para exibição.                                |
| `Pedidos`            | int           | Contador histórico                       | Ignorar no MVP.                                      |
| `Qtd_Entregue`       | str livre     | `"1.447,00 UN"`                          | Ignorar no MVP.                                      |
| `Unidade_Venda`      | str           | `Saco 15 kg`, `Caixa 2,30 m²`            | Parse para extrair m²/caixa quando aplicável.        |
| `Peso_kg`            | float         | `15,0`, `1,0`                            | Parse BR (troca `,` por `.`).                        |
| `Volume_m3`          | str livre     | `0,00092`, `≈0,009 (estimado)`           | Parse tolerante. Se contém "estimado" → `estimado=True`. |
| `Dado_Estimado`      | str           | `SIM` / `NAO`                            | Bool.                                                |
| `Fonte`              | str livre     | Vários                                   | Manter para auditoria.                               |

## 3. `DADOS_DE_ENTREGAS__xlsx_-_ROTAS_E_COLETAS.csv`

Separador: `,` · Formato semi-estruturado (planilha exportada com linhas em branco).

Contém dois blocos úteis:

### Bloco 1 — Rotas (linhas ~11–17)

Colunas de cabeçalho na linha 11: `ROTA`, `VALOR TOTAL (R$)`, `PREVISÃO`, `CARGA`, e 6 colunas de valor por eixo (uma por eixo + Crateús).

Extração: usar `pandas.read_csv(skiprows=..., nrows=...)` ou parse manual por índice. Extrair somente:
- Nome do eixo
- Cidades (aparecem na linha 12 como cabeçalho das 6 colunas)

### Bloco 2 — Capacidades (linhas ~26–28)

| Linha | Coluna A         | HR/BONGO      | ACELLO 815    | MOTOS         |
|-------|------------------|---------------|---------------|---------------|
| 26    | Capacidade utilizada | (header)   | (header)      | (header)      |
| 27    | Peso             | `1.700 kg`    | `4.800 kg`    | `300 kg`      |
| 28    | capacidade em m³ | `2,1793`      | `2,4543`      | `0,3833`      |

Parse: remover `kg`, converter BR.

## 4. `DADOS_DE_ENTREGAS__-_Vendas_Faturamento_Entregas.csv` (a.k.a. `Vendas_Faturamento_Entregas.csv`)

Separador: `,` · ~3.236+ pedidos únicos · 24 colunas (planilha operacional completa).
**MVP (atual):** não usado como fonte primária — `Pedidos_Filtrados_Semana_N.csv` já vêm sanitizados.
**Pós-MVP ([[prd/10-pos-mvp-melhorias]]#21-integracao-vendas_faturamentoentregascsv-rf-novo):** integração obrigatória para validação real de status entrega/faturamento.

| Coluna original         | Tipo real observado         | Regra pós-MVP                                                   |
|-------------------------|-----------------------------|-----------------------------------------------------------------|
| `Pedido`                | `3236`, `L12608278`         | Chave de join com semanas (normalizar: remover prefixo `L` se houver). |
| `Situacao`              | `FATURADO`, `CANCELADO`     | Uppercase. Filtro: só `FATURADO` entra no solver.               |
| `Situacao_CSV_Entrega`  | `ENTREGUE`, `PENDENTE`, `EM ROTA`, `TRANSFERIDO`, `RETIRADA` | Uppercase. Filtro: `IN (ENTREGUE, PENDENTE, EM ROTA)` entra. `RETIRADA`/`TRANSFERIDO` excluem. |
| `Data`                  | `01/08/26` (dd/mm/yy)       | Parse `dayfirst=True`, ano 2 dígitos → 2000+.                   |
| `Cidade`                | `CRATEUS`, `IPAPORANGA`     | Uppercase, strip, remover acentos. Cruzar com `Pedidos_Filtrados.Cidade` → log `CIDADE_DIVERGENTE` se divergir. |
| `Logistica`             | `NORMAL`, `URGENTE`, `RETIRADA` | Uppercase. Informativo.                                         |
| `Valor_Pedido`          | `"R$ 412,00"` (string BR)   | Auditoria: conferir com `Pedidos_Filtrados.Valor_Pedido`.       |
| `Veiculo`               | `HR / BONGO`, `ACELLO 815`  | Histórico de qual veículo fez a entrega (não é ficha técnica).  |

**Deduplicação:** Mesmo `Pedido` pode aparecer múltiplas vezes (histórico de status). Regra: **último status por `Data`** (mais recente vence). Log de conflitos se status final divergir entre linhas.

**Inconsistências conhecidas (adicionais ao MVP):**
- `Data` com ano 2 dígitos ambíguo → assumir 2000+ (lote 2026)
- `Situacao_CSV_Entrega` vazio em alguns registros → tratar como `PENDENTE` com warning no log
- Colunas extras vazias (~10) → ignorar

## Inconsistências conhecidas

Do protótipo, documentadas para o ETL tratar:

1. **Data fora do lote:** ao menos um registro com `26/08/2014` em lote de agosto/2026 → corrigir para `2026-08-26` com log.
2. **Cidade com espaço extra:** `"NOVA RUSSAS "` → strip.
3. **Cidade fora dos eixos:** alguns pedidos com cidade não mapeada → excluir com motivo `"Cidade não mapeada em eixo"`.
4. **Cubagem ausente:** ~113 dos 330 itens dos 93 pedidos elegíveis não têm cubagem no Top 85 → pedido vira 🔴.
5. **`Situacao_CSV_Entrega` divergente:** alguns pedidos aparecem como `RETIRADA` mesmo com `Logistica=ENTREGA` → confiar em `Situacao_CSV_Entrega`.

## Ver também

- [[dominio/pipeline_etl]] — como o pipeline consome cada CSV
- [[dominio/cubagem]] — como o Ranking é usado
