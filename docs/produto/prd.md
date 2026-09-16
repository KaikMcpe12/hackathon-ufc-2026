# PRD — NobreLOG Optimizer

## 1. Contexto de negócio

**Empresa:** Grupo Nobre Lar (Home Center, 38 anos, Crateús-CE) — materiais de construção para Sertão Central e Inhamuns.

**Operação atual:**
- 4 caminhões atendem 5 eixos rodoviários fixos (moto atende só Crateús urbano — fora do escopo).
- 35–40% das entregas são pisos, porcelanatos e argamassas (pesado e volumoso).
- Montagem de carga é manual, feita "no olho" ou pelo valor do pedido.
- Coordenador gasta 40–60 min/dia decidindo o que entra em cada caminhão.

**Frota conhecida (do CSV oficial):**

| Veículo    | Peso (kg) | Volume (m³) |
|------------|----------:|------------:|
| HR / BONGO |     1.700 |      2,1793 |
| ACELLO 815 |     4.800 |      2,4543 |
| MOTOS      |       300 |      0,3833 |

**Eixos:**
1. Buriti dos Montes
2. Sucesso, Tamboril, Nova Russas, Fazenda
3. Independência
4. Ipaporanga, Poranga, Ararendá
5. Novo Oriente, Realejo, Santana, Monte Nebo, Santo André, Quiterianópolis

## 2. Problema central

> Como selecionar automaticamente a melhor combinação de pedidos para um veículo e eixo de entrega, maximizando o aproveitamento físico do caminhão sem ultrapassar seus limites de peso e volume, e transformar essa decisão em um plano de carga operacionalmente utilizável?

## 3. Matriz de problemas específicos

| ID   | Problema                                                | Consequência                                         | Resposta                                                 |
|------|---------------------------------------------------------|------------------------------------------------------|----------------------------------------------------------|
| P01  | Dados operacionais inconsistentes                       | Planejamento incorreto                               | Limpeza + validação automática ([[dominio/pipeline_etl]]) |
| P02  | Peso e volume estão distribuídos nos itens              | Cálculo manual                                       | Cubagem automática por pedido ([[dominio/cubagem]])       |
| P03  | Produtos vendidos em m² transportados em caixas         | Quantidade comercial ≠ carga física                  | Conversão m² → caixas                                    |
| P04  | Peso e volume são restrições simultâneas                | Carga pode desperdiçar dimensão ou exceder outra     | Otimização multidimensional ([[dominio/otimizacao]])      |
| P05  | Muitas combinações possíveis                            | Escolha manual limitada                              | Solver MILP (PuLP/CBC)                                   |
| P06  | Pedidos pertencem a eixos diferentes                    | Mistura indevida                                     | Filtragem por eixo antes da otimização                   |
| P07  | Ordem de entrega influencia carregamento                | Movimentação extra na descarga                       | Sequenciamento LIFO                                      |
| P08  | Resultado precisa ser usado pela expedição              | Dashboard não resolve                                | Geração de plano de carga (PDF)                          |
| P09  | Algoritmo pode parecer caixa-preta                      | Usuário não confia                                   | Explicabilidade por pedido                               |
| P10  | Dados incompletos contaminam otimização                 | Carga calculada incorretamente                       | Bloqueio de registros sem cubagem + fila de revisão      |

## 4. Proposta de valor

> **Transformar a lista de pedidos em um plano de carga otimizado, explicável e pronto para execução.**

**Slogan de trabalho:** *Do pedido ao caminhão: a melhor combinação de carga em poucos segundos.*

## 5. Escopo

### 5.1 Dentro do MVP

- Pipeline ETL sobre os 4 CSVs semanais + Ranking Top 85 + Rotas/Coletas
- Cubagem por código de produto + conversão m² → caixas
- Classificação de qualidade da cubagem 🟢🟡🔴
- Fila de revisão para pedidos 🔴
- Otimização MILP mono-eixo/mono-veículo com PuLP/CBC
- Diagnóstico de gargalo (PESO vs VOLUME)
- Explicabilidade dos pedidos rejeitados
- Frontend React+TS com 5 telas (ver [[frontend/telas]])
- Geração de PDF do romaneio (WeasyPrint no backend)
- Upload de CSV para re-ingestão em runtime
- Camada LLM opcional para insights ([[dominio/llm_insights]])
- Simulação/comparação entre 2 veículos para mesmo eixo

### 5.2 Fora do MVP (v2)

- Otimização multi-eixo simultânea (distribuir 4 veículos entre 5 eixos)
- Persistência em banco de dados
- Autenticação/multi-usuário
- Mapas com rotas geográficas
- Rastreamento GPS
- Previsão de demanda com ML
- App mobile
- Histórico de planos anteriores

## 6. Métricas de sucesso do MVP

| Indicador                       | Cenário atual         | Meta MVP                              |
|--------------------------------|-----------------------|---------------------------------------|
| Tempo de montagem de carga     | 40–60 min/dia         | < 5 minutos, automatizado             |
| Taxa de ocupação (kg e m³)     | Não medida            | Maior possível, apurada na demo       |
| Violação de limite físico      | Ocorre sem registro   | **Zero** cargas acima de kg ou m³     |
| Rastreabilidade da limpeza     | Manual, sem registro  | Cada correção explicada, com critério |
| Qualidade do plano de carga    | Manual                | Utilizável pela expedição sem retrabalho |

## 7. Restrições

- **Anonimização:** dados fornecidos são anonimizados. Proibida reidentificação ou enriquecimento externo.
- **Dados sintéticos:** produtos sem cubagem oficial ganham estimativa sintética *marcada explicitamente* — nunca apresentada como dado real.
- **Prazo:** hackathon de 13h. Todo esforço deve caber no cronograma.

## 8. Referências

- Documento Mestre do projeto (materiais de origem)
- Desafio NobreLOG IA (edital oficial)
- README do protótipo (Etapa 4b) — solver validado
- Ver [[entrega/criterios_aceite]] para o caso oficial de aceite
