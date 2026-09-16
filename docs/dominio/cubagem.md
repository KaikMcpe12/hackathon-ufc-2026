# Cubagem

Converte itens vendidos (unidade comercial) em **peso** e **volume** físicos.

## Fluxo

```
pedido.itens[] → parse do resumo → cruzar por código → converter unidade → calcular kg/m³ → agregar por pedido → classificar
```

## Parse do resumo de itens

`Itens_Resumo` na semana vem como string separada por `;` (ou similar):

```
14900 - ARGAMASSA VARANDAS E QUINTAIS 15KG QUARTZOLIT (7,00 UN);
15624 - REJ QUARTZOLIT CZ PLATINA - 1KG (2,00 UN)
```

Extração por regex:

```python
import re
ITEM_RE = re.compile(r"(?P<codigo>\d+)\s*-\s*(?P<descricao>.+?)\s*\((?P<qtd>[\d,\.]+)\s*(?P<un>\w+)\)")
```

Resulta em:

```python
{"codigo": "14900", "descricao": "ARGAMASSA VARANDAS E QUINTAIS 15KG QUARTZOLIT", "qtd": 7.0, "un": "UN"}
```

## Cruzamento com Ranking Top 85

Chave: `codigo` (string). `ranking_top85.csv` tem:

- `codigo`
- `produto`
- `unidade_venda` (ex.: `Saco (papel/plástico) 15 kg`, `Caixa 2,30 m²`)
- `peso_kg` (por unidade)
- `volume_m3` (por unidade)
- `dado_estimado` (`SIM`/`NAO`)
- `fonte`

Se código do pedido não está no Ranking → item cai em `AUSENTE`.

## Conversão m² → caixas

Alguns produtos são vendidos em m² (`MT` no CSV do pedido) mas transportados em caixas. Regra:

```python
import math
caixas = math.ceil(m2_solicitados / m2_por_caixa)
peso_total = caixas * peso_por_caixa
volume_total = caixas * volume_por_caixa
```

`m2_por_caixa` vem da tabela de cubagem (implícito na `unidade_venda`).

Exemplo:

- Pedido: `15,180 MT` de PISO POINTER
- Caixa cobre `2,30 m²`
- Caixas = `ceil(15,180 / 2,30)` = **7 caixas**
- Peso = `7 × peso_da_caixa`

Nunca fração de caixa.

## Faixas de peso conservadoras

Quando o Ranking indica faixa (ex.: `peso ≈ 24,5 kg`), usar o **valor maior** para evitar subestimar. Isso é regra de segurança: **melhor sobrar carga fictícia do que estourar caminhão real**.

## Classificação da cubagem

Cada pedido termina em uma classe:

| Selo | Nome        | Regra                                                                    | Uso no solver         |
|------|-------------|--------------------------------------------------------------------------|-----------------------|
| 🟢   | COMPLETA    | Todos os itens têm cubagem no Ranking com `dado_estimado=NAO`            | Entra automaticamente |
| 🟡   | ESTIMADA    | Ao menos um item tem `dado_estimado=SIM` ou usou estimativa sintética    | Entra com badge amarelo |
| 🔴   | AUSENTE     | Ao menos um item sem cubagem nenhuma                                     | **Barrado.** Vai para fila de revisão (UC07) |

Regra crítica: **peso ou volume ausente NUNCA vira zero.** É `NaN` e o pedido cai em 🔴.

## Estimativas sintéticas (protótipo)

Para produtos fora do Top 85, o time criou estimativas sintéticas baseadas em produtos similares. Elas estão em `etapa4b_referencias_sinteticas_prototipo.csv` (opcional — não é fonte oficial da empresa).

Regras:

1. Estimativas sintéticas são marcadas explicitamente na coluna `fonte` (ex.: `sintetico:aproximacao_por_similaridade`).
2. Pedido que usou estimativa sintética é sempre 🟡, nunca 🟢.
3. UI mostra o badge amarelo e permite ao coordenador editar/aprovar (UC07).
4. Em produção real, essas estimativas seriam substituídas pelas fichas oficiais da empresa.

## Agregação por pedido

```python
pedido.peso_kg = sum(item.peso_total for item in pedido.itens)
pedido.volume_m3 = sum(item.volume_total for item in pedido.itens)
pedido.qualidade_cubagem = pior_selo(item.selo for item in pedido.itens)
# 🔴 > 🟡 > 🟢 na prioridade da pior
```

## Módulos

- `src/cubagem/calculadora.py` — orquestra parse + cruzamento + soma
- `src/cubagem/conversor.py` — m² → caixas
- `src/cubagem/classificador.py` — atribui selo
- `src/cubagem/sintetico.py` — carrega estimativas sintéticas do protótipo (opcional)

## Ver também

- [[dominio/pipeline_etl]]
- [[dominio/otimizacao]]
- [[dados/dicionario]]#ranking
