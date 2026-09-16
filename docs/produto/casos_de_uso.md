# Casos de Uso

Ator principal: **Coordenador de Logística**. Ator secundário: **Sistema**.

## UC01 — Selecionar eixo

**Objetivo:** definir conjunto de pedidos considerado.
**Fluxo:** usuário abre sistema → sistema apresenta 5 eixos → usuário seleciona → sistema filtra pedidos elegíveis do eixo.
**Resultado:** pedidos do eixo disponíveis para o solver.

## UC02 — Selecionar veículo

**Objetivo:** definir capacidades máximas de kg e m³.
**Fluxo:** sistema apresenta veículos com capacidades → usuário seleciona → capacidades tornam-se restrições da otimização.

## UC03 — Selecionar semana

**Objetivo:** escolher o lote de pedidos a otimizar.
**Fluxo:** dropdown com semanas 1–4 → default = última semana → usuário confirma ou troca.
Ver [[arquitetura/adr/0006_semana_dropdown]].

## UC04 — Processar e validar pedidos

**Ator:** Sistema.
**Fluxo:** carrega CSVs → normaliza colunas → remove registros fora do escopo → detecta inconsistências → classifica qualidade da cubagem.
**Resultado:** base limpa pronta para otimização. Ver [[dominio/pipeline_etl]].

## UC05 — Calcular cubagem

**Ator:** Sistema.
**Fluxo:** lê itens do pedido → cruza códigos com Ranking Top 85 → converte unidades (m² → caixas) → calcula peso e volume por item → agrega por pedido.
**Resultado:** pedido com peso_total e volume_total. Ver [[dominio/cubagem]].

## UC06 — Identificar problemas de dados

**Fluxo:** sistema verifica peso/volume de cada item → classifica pedido em 🟢🟡🔴 → sinaliza incompletos → barra 🔴 da otimização automática.

## UC07 — Revisar pedidos com pendência de cubagem *(novo)*

**Ator:** Coordenador.
**Objetivo:** aprovar ou complementar cubagem de pedidos 🔴 na fila de revisão.
**Fluxo:** usuário abre tela de triagem → filtra por "cubagem incompleta" → informa peso/volume estimado por item → pedido passa a 🟡 e volta ao pool.
**Resultado:** pedido antes barrado volta para otimização com badge amarelo.
Ver [[frontend/telas]]#triagem.

## UC08 — Otimizar carga

**Pré-condições:** eixo, veículo e semana selecionados; pedidos válidos disponíveis.
**Fluxo:** usuário clica "Otimizar carga" → backend monta MILP → PuLP/CBC encontra combinação → sistema valida restrições → retorna resultado.
**Resultado:** carga válida, com 0 violações. Ver [[dominio/otimizacao]].

## UC09 — Visualizar desempenho

**Fluxo:** sistema apresenta kg utilizado/disponível/%, m³ utilizado/disponível/%, valor total, quantidade de pedidos, fator limitante.
Ver [[frontend/telas]]#planejamento.

## UC10 — Diagnosticar fator limitante

**Fluxo:** sistema compara `ocupacao_peso` e `ocupacao_volume` → identifica maior → destaca "Gargalo: PESO" ou "Gargalo: VOLUME".

## UC11 — Explicar pedidos não selecionados

**Fluxo:** para cada pedido rejeitado, sistema informa motivo:
- excederia o peso
- excederia o volume
- excederia peso e volume
- cubagem incompleta
- outra combinação aproveita melhor o caminhão

## UC12 — Organizar sequência de descarga

**Fluxo:** sistema identifica cidades presentes na carga → relaciona com ordem oficial do eixo → apresenta sequência de descarga → deriva ordem de carregamento LIFO (inversa).

## UC13 — Gerar plano de carga (PDF)

**Fluxo:** usuário clica "Gerar plano" → backend renderiza template WeasyPrint → PDF retorna com veículo, eixo, data, pedidos, cidades, peso, volume, ocupação, ordem de descarga e assinatura.
Ver [[dominio/romaneio]].

## UC14 — Consultar qualidade dos dados

**Fluxo:** usuário abre dashboard de qualidade → sistema mostra registros recebidos/removidos/corrigidos, pedidos incompletos, elegíveis, cobertura da cubagem.
Ver [[frontend/telas]]#qualidade_dados.

## UC15 — Comparar dois veículos

**Fluxo:** usuário ativa "Comparar veículos" → seleciona 2 veículos → sistema roda otimização para cada → apresenta lado a lado com destaque no "melhor equilíbrio operacional".
Ver [[frontend/telas]]#simulacao.

## UC16 — Reingerir CSVs

**Ator:** Coordenador.
**Fluxo:** usuário abre configurações avançadas → faz upload de CSV substituto → sistema valida colunas → recarrega estado in-memory → retorna relatório de ingestão.
Ver [[api/endpoints]]#etl_ingest.

## UC17 — Gerar insight em linguagem natural *(diferencial)*

**Ator:** Sistema (camada LLM).
**Fluxo:** após otimização, backend envia resumo determinístico ao LLM → LLM devolve 1–2 parágrafos comentando o resultado (perfil da carga, recomendações operacionais).
**Regra:** LLM nunca altera números do solver. Ver [[dominio/llm_insights]].
