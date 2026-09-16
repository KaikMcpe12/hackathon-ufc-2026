# Otimização

Núcleo determinístico do sistema. Escolhe a combinação de pedidos que **maximiza a ocupação física** de um veículo **sem violar** peso ou volume.

## Classificação técnica

Knapsack 2D (peso × volume) — caso particular do Multi-Dimensional Knapsack Problem (MDKP). Modelagem via MILP.

## Variáveis de decisão

Para cada pedido `i` elegível:

```
x_i ∈ {0, 1}   →   1 se pedido i entra na carga, 0 caso contrário
```

Escopo do MVP: um único veículo, um único eixo, por chamada. Ver [[arquitetura/adr/0005_mvp_mono_eixo]].

## Restrições (hard constraints)

```
Σ (peso_i × x_i)   ≤ capacidade_peso     (1)
Σ (volume_i × x_i) ≤ capacidade_volume   (2)
```

Nenhuma solução viola (1) ou (2). Isso é *hard constraint* — o solver rejeita e a API nunca devolve carga inválida.

## Função objetivo

```
maximizar   0,5 · (peso_utilizado / capacidade_peso)
          + 0,5 · (volume_utilizado / capacidade_volume)
```

**Por que 0,5/0,5?**
Otimizar só valor financeiro reproduz o comportamento manual que queremos substituir. Otimizar só peso (ou só volume) ignora a outra dimensão. Combinação linear balanceada empurra o solver a aproveitar as duas capacidades.

**Valor financeiro:** critério secundário. Se duas soluções empataram em ocupação (diferença < ε), escolhe a de maior valor.

## Diagnóstico do gargalo

Após resolver:

```python
if ocupacao_peso > ocupacao_volume:
    gargalo = "PESO"
else:
    gargalo = "VOLUME"
```

Aparece na UI ([[frontend/telas]]#planejamento) e no romaneio ([[dominio/romaneio]]).

## Explicabilidade — motivos de rejeição

Para cada pedido não selecionado, gerar mensagem:

| Regra                                                                        | Mensagem                                                        |
|------------------------------------------------------------------------------|-----------------------------------------------------------------|
| `peso_i` sozinho já excederia a capacidade                                   | *"Excederia a capacidade de peso em X kg."*                     |
| `volume_i` sozinho já excederia                                              | *"Excederia a capacidade de volume em Y m³."*                   |
| Ambos                                                                        | *"Excederia peso e volume."*                                    |
| Solver não selecionou por otimização (caberia individualmente)               | *"Outra combinação aproveita melhor o caminhão."*               |
| Pedido é 🔴                                                                   | *"Cubagem incompleta — pendente de revisão."*                   |
| Pedido não pertence ao eixo                                                  | *"Cidade fora do eixo selecionado."*                            |

Algoritmo para "excederia em X":

```python
delta_peso = (peso_selecionado + peso_i) - capacidade_peso
delta_vol  = (vol_selecionado  + vol_i)  - capacidade_volume
```

Se qualquer delta > 0, formata com valor exato (sempre positivo, arredondado para 2 casas). Se ambos <= 0, o motivo é "otimização".

## Implementação com PuLP

```python
import pulp

def otimizar(pedidos, capacidade_peso, capacidade_volume):
    p = pulp.LpProblem("nobrelog", pulp.LpMaximize)
    x = {i: pulp.LpVariable(f"x_{i}", cat="Binary") for i in pedidos.index}

    peso_norm = pulp.lpSum(pedidos.peso[i]   * x[i] for i in x) / capacidade_peso
    vol_norm  = pulp.lpSum(pedidos.volume[i] * x[i] for i in x) / capacidade_volume
    p += 0.5 * peso_norm + 0.5 * vol_norm

    p += pulp.lpSum(pedidos.peso[i]   * x[i] for i in x) <= capacidade_peso
    p += pulp.lpSum(pedidos.volume[i] * x[i] for i in x) <= capacidade_volume

    p.solve(pulp.PULP_CBC_CMD(msg=False, timeLimit=30))
    return {i: int(pulp.value(x[i])) for i in x}
```

Wrapper devolve `PlanoDeCarga` (Pydantic) com totais, gargalo, lista de selecionados e lista de rejeitados com motivos.

## Determinismo

CBC pode retornar soluções alternativas com valor objetivo idêntico. Para reproduzibilidade:

1. Ordenar pedidos por `pedido_id` antes de montar variáveis.
2. Fixar `timeLimit=30` para o CBC.
3. Nunca depender de ordem hash do dict.

## Caso oficial (Eixo 4 + ACELLO 815)

```
Capacidade: 4.800 kg, 2,4543 m³
Resultado esperado:
  7 pedidos selecionados
  Peso:   4.797,335 kg  (99,94%)
  Volume: 2,4421 m³     (99,50%)
  Gargalo: PESO
  Violações: 0
  Valor: R$ 16.770,85
```

Se o solver não bater esses números após ETL completo, algo está errado. Ver [[entrega/criterios_aceite]].

## Ver também

- [[arquitetura/adr/0003_solver_pulp]]
- [[dominio/pipeline_etl]] — o que alimenta o solver
- [[dominio/llm_insights]] — camada 2 que comenta o resultado
