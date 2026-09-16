# Glossário

Termos do domínio, ordenados alfabeticamente.

**Cubagem** — Peso e volume físicos de um item ou pedido. Base para calcular ocupação do caminhão. Ver [[dominio/cubagem]].

**Eixo** — Rota rodoviária fixa que agrupa cidades atendidas em uma mesma viagem. Nobre Lar tem 5 eixos. Ver [[produto/prd]]#contexto.

**Elegibilidade** — Conjunto de filtros aplicados a um pedido antes da otimização: não pode estar cancelado, ser retirada no balcão, ter destino em Crateús, nem estar fora de qualquer eixo mapeado.

**Fila de revisão** — Lista de pedidos 🔴 (sem cubagem) que aguardam decisão do coordenador para entrar ou não na otimização.

**Gargalo** — Recurso limitante da carga: `PESO` se `ocupacao_peso > ocupacao_volume`, senão `VOLUME`. Ver [[dominio/otimizacao]]#gargalo.

**Hard constraint** — Restrição rígida que nunca pode ser violada. No NobreLOG: peso e volume ≤ capacidade do veículo.

**LIFO (Last In, First Out)** — Ordem de carregamento inversa à ordem de descarga. O último pedido carregado é o primeiro descarregado. Ver [[dominio/romaneio]]#lifo.

**MILP** — Mixed-Integer Linear Programming. Classe de problemas de otimização com variáveis inteiras e restrições lineares. Solver do NobreLOG usa MILP. Ver [[dominio/otimizacao]].

**Motor híbrido** — Arquitetura em 2 etapas: solver matemático (determinístico) + LLM (interpretativo). Ver [[arquitetura/adr/0007_motor_hibrido_llm]].

**Ocupação** — Percentual da capacidade utilizada. Duas dimensões: `ocupacao_peso = peso_usado / capacidade_peso` e `ocupacao_volume = volume_usado / capacidade_volume`.

**Pedido elegível** — Pedido que passou por todos os filtros de elegibilidade e tem eixo definido.

**Ranking Top 85** — Tabela dos 85 materiais mais entregues, com código, peso e volume unitários. Fonte de cubagem oficial. Ver [[dados/dicionario]]#ranking.

**Romaneio** — Documento operacional entregue à expedição com a lista de pedidos, ordem de descarga e assinaturas. No NobreLOG, o romaneio é o PDF gerado pelo backend. Ver [[dominio/romaneio]].

**Selo 🟢🟡🔴** — Classificação da qualidade da cubagem de um pedido. 🟢 = todos os dados oficiais; 🟡 = ao menos um estimado; 🔴 = ao menos um ausente (barrado da otimização automática).

**Semana** — Lote semanal de pedidos. NobreLOG opera com 4 semanas nos CSVs de entrada. Ver [[arquitetura/adr/0006_semana_dropdown]].

**Sequência de descarga** — Ordem oficial das cidades do eixo em que a expedição entrega. Definida no `Rotas e Coletas`.

**Sintético** — Estimativa de cubagem inventada pelo protótipo para produtos fora do Top 85. Marcada explicitamente. Em produção real seria substituída por ficha técnica oficial. Ver [[dominio/cubagem]]#sinteticas.

**Solver** — Programa que resolve o problema de otimização automaticamente. NobreLOG usa PuLP + CBC. Ver [[arquitetura/adr/0003_solver_pulp]].

**Violação** — Solução que ultrapassa peso ou volume. Nunca pode ser gerada pelo sistema (hard constraint).
