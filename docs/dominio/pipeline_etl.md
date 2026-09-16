# Pipeline ETL

Fluxo do dado bruto até "pedido pronto para o solver":

```
CSVs brutos → Carregar → Normalizar → Filtrar → Corrigir → Cruzar cubagem → Classificar → Estado in-memory
                                                                                                 ↓
                                                                                        Solver ([[dominio/otimizacao]])
```

## Números de referência (do protótipo validado)

Sobre a base real:

- **688** registros recebidos (todas as semanas)
- **93** pedidos elegíveis após filtros
- **46** com cubagem completa apenas com dados oficiais
- **81** utilizáveis após estimativas sintéticas (marcadas)

Se o pipeline não reproduzir esses números aproximadamente, revisar filtros. Ver [[entrega/criterios_aceite]].

## Etapa 1 — Carregar

Módulo: `src/etl/loader.py`

- Lê os 6 CSVs de `backend/data/` com `pandas.read_csv`.
- Detecção de separador: os arquivos usam `;` ou `,` — normalizar na leitura.
- Encoding: UTF-8 com BOM (arquivos vêm com `\ufeff`).
- Concatena as 4 semanas em uma DataFrame com coluna extra `semana` (1–4).

## Etapa 2 — Normalizar

Módulo: `src/etl/normalizer.py`

- Snake_case em todos os nomes de coluna (`VALOR DO PEDIDO` → `valor_pedido`).
- `valor_pedido`: string `"R$ 1.811,87"` → float `1811.87`. Remove `R$`, ponto de milhar, troca vírgula por ponto.
- `data`: aceita `01/08/26`, `01/08/2026`, `2026-08-01`. Normaliza para `datetime`.
- `cidade`: uppercase, remove acentos para comparação (mas guarda original para exibição).
- `situacao`, `logistica`: uppercase.

## Etapa 3 — Filtrar (elegibilidade)

Módulo: `src/etl/filters.py`

Regras (todas registradas no log com contagem):

| Filtro                          | Coluna base            | Regra                                          |
|--------------------------------|------------------------|------------------------------------------------|
| Remover cancelados              | `situacao`             | Excluir se contém `CANCELADO`                  |
| Remover retiradas no balcão     | `situacao_csv_entrega` | Excluir se `RETIRADA`                          |
| Remover entregas em Crateús     | `cidade` (normalizada) | Excluir se `CRATEUS`/`CRATEÚS`                 |
| Remover cidades fora dos eixos  | cruzar com `eixos.csv` | Excluir se cidade não mapeia para nenhum eixo  |

Ordem: cancelados → retiradas → Crateús → sem eixo. Log conta cada exclusão separadamente.

## Etapa 4 — Corrigir

Módulo: `src/etl/correcoes.py`

Correções documentadas (cada uma vira uma entrada em `state.log_correcoes`):

- **Datas inconsistentes** (ex.: `26/08/2014` em lote de agosto/2026): corrigir para o ano de referência (2026) apenas se o dia e mês forem plausíveis para o lote. Nunca "adivinhar" data completa.
- **Cidades divergentes:** casos como `NOVA RUSSAS ` (trailing space), `IPAPORAGA` (typo comum) — mapear via dicionário controlado.
- **Valores ausentes em campo obrigatório:** pedido vai para fila de exceção (não é excluído — o coordenador decide).

Correções silenciosas são proibidas. Toda mudança registra:

```json
{
  "pedido": "L12608740",
  "campo": "data",
  "valor_original": "26/08/2014",
  "valor_novo": "26/08/2026",
  "regra": "ano_fora_do_lote",
  "criterio": "lote_agosto_2026"
}
```

## Etapa 5 — Cruzar com Ranking Top 85

Módulo entra em [[dominio/cubagem]]. Parseia `Itens_Resumo` do pedido (ex.: `"14900 - ARGAMASSA VARANDAS E QUINTAIS 15KG QUARTZOLIT (7,00 UN)"`) em código + quantidade + unidade. Cruza `codigo` com `ranking_top85`.

## Etapa 6 — Classificar

Ver [[dominio/cubagem]]#classificacao. Cada pedido termina com um selo 🟢🟡🔴.

## Etapa 7 — Publicar estado

Módulo: `src/state.py`

Ao final, `state.pedidos_processados` fica com colunas:

| Coluna                | Tipo    | Fonte                             |
|-----------------------|---------|-----------------------------------|
| `pedido`              | str     | CSV semanal                       |
| `data`                | date    | normalizada                       |
| `cidade`              | str     | normalizada                       |
| `eixo_id`             | int     | derivado de `eixos.csv`           |
| `valor`               | float   | normalizado                       |
| `peso_kg`             | float   | cubagem (ou NaN se 🔴)            |
| `volume_m3`           | float   | cubagem (ou NaN se 🔴)            |
| `qualidade_cubagem`   | str     | `COMPLETA` / `ESTIMADA` / `AUSENTE` |
| `semana`              | int     | 1–4                               |
| `itens`               | list    | parse do `Itens_Resumo`           |

Pedidos com `AUSENTE` vão para a fila de revisão (UC07), não entram no solver automaticamente.

## Log de qualidade

Exposto por `GET /qualidade/log`. Consumido pelo dashboard [[frontend/telas]]#qualidade_dados.

## Ver também

- [[dominio/cubagem]] — o que acontece dentro do cruzamento com Ranking
- [[dados/dicionario]] — colunas reais de cada CSV
