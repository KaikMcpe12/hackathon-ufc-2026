# Requisitos — Funcionais e Não Funcionais

## Requisitos Funcionais (RF)

| ID    | Requisito                                                            | Prioridade   | Referência                        |
|-------|----------------------------------------------------------------------|--------------|-----------------------------------|
| RF01  | Permitir selecionar um eixo de entrega                               | Obrigatório  | [[frontend/telas]]#planejamento   |
| RF02  | Permitir selecionar um veículo                                       | Obrigatório  | [[frontend/telas]]#planejamento   |
| RF03  | Permitir selecionar a semana de pedidos (dropdown, default = última) | Obrigatório  | [[arquitetura/adr/0006_semana_dropdown]] |
| RF04  | Carregar e processar pedidos disponíveis a partir dos CSVs           | Obrigatório  | [[dominio/pipeline_etl]]          |
| RF05  | Filtrar retiradas no balcão, cancelados e entregas em Crateús        | Obrigatório  | [[dominio/pipeline_etl]]#filtros  |
| RF06  | Calcular peso total de cada pedido                                   | Obrigatório  | [[dominio/cubagem]]               |
| RF07  | Calcular volume total de cada pedido                                 | Obrigatório  | [[dominio/cubagem]]               |
| RF08  | Converter m² para caixas quando necessário                           | Obrigatório  | [[dominio/cubagem]]#conversao     |
| RF09  | Identificar dados incompletos/inconsistentes (classificação 🟢🟡🔴)   | Obrigatório  | [[dominio/cubagem]]#classificacao |
| RF10  | Impedir uso automático de pedidos 🔴 (sem cubagem)                   | Obrigatório  | [[dominio/cubagem]]               |
| RF11  | Pedidos 🟡 (estimados) entram sempre com badge amarelo               | Obrigatório  | [[frontend/telas]]#triagem        |
| RF12  | Executar otimização automática                                       | Obrigatório  | [[dominio/otimizacao]]            |
| RF13  | Respeitar limite de peso (hard constraint)                           | Obrigatório  | [[dominio/otimizacao]]#restricoes |
| RF14  | Respeitar limite de volume (hard constraint)                         | Obrigatório  | [[dominio/otimizacao]]#restricoes |
| RF15  | Maximizar aproveitamento físico (0,5·Op + 0,5·Ov)                    | Obrigatório  | [[dominio/otimizacao]]#objetivo   |
| RF16  | Mostrar ocupação em peso                                             | Obrigatório  | [[frontend/telas]]                |
| RF17  | Mostrar ocupação em volume                                           | Obrigatório  | [[frontend/telas]]                |
| RF18  | Identificar fator limitante (PESO vs VOLUME)                         | Obrigatório  | [[dominio/otimizacao]]#gargalo    |
| RF19  | Listar pedidos selecionados com id, cidade, peso, volume e valor     | Obrigatório  | [[frontend/telas]]#planejamento   |
| RF20  | Listar pedidos não selecionados com motivo                           | Diferencial  | [[dominio/otimizacao]]#explicabilidade |
| RF21  | Organizar pedidos segundo sequência de cidades do eixo               | Obrigatório  | [[dominio/romaneio]]              |
| RF22  | Mostrar ordem de descarga                                            | Obrigatório  | [[frontend/telas]]#romaneio       |
| RF23  | Mostrar ordem de carregamento (LIFO — inversa à descarga)            | Obrigatório  | [[dominio/romaneio]]#lifo         |
| RF24  | Gerar plano de carga/romaneio em PDF                                 | Obrigatório  | [[dominio/romaneio]]              |
| RF25  | Permitir upload de novos CSVs para re-ingestão                       | Obrigatório  | [[api/endpoints]]#etl_ingest      |
| RF26  | Mostrar resumo da qualidade dos dados (dashboard)                    | Diferencial  | [[frontend/telas]]#qualidade_dados |
| RF27  | Fila de revisão para pedidos 🔴                                       | Obrigatório  | [[frontend/telas]]#triagem        |
| RF28  | Comparar dois veículos lado a lado para o mesmo eixo                 | Diferencial  | [[frontend/telas]]#simulacao      |
| RF29  | Gerar insight em linguagem natural sobre a carga (LLM)               | Diferencial  | [[dominio/llm_insights]]          |
| RF30  | Permitir nova otimização sem reiniciar aplicação                     | Obrigatório  | —                                 |

## Requisitos Não Funcionais (RNF)

| ID     | Requisito                                                                                | Como medir                              |
|--------|------------------------------------------------------------------------------------------|------------------------------------------|
| RNF01  | Usabilidade: coordenador sem conhecimento técnico completa fluxo em < 5 min              | Teste com coordenador na demo            |
| RNF02  | Clareza visual: peso, volume, capacidade restante e fator limitante visíveis na tela     | Inspeção de UI                           |
| RNF03  | Responsividade: funciona em notebook/desktop (mobile é secundário)                       | Manual, larguras 1280+                   |
| RNF04  | Desempenho: otimização retorna em < 3s para o dataset do hackathon                       | Cronômetro                               |
| RNF05  | Confiabilidade: nunca apresentar carga com peso ou volume acima da capacidade            | Testes unitários no solver               |
| RNF06  | Integridade de dados: ausência de peso/volume nunca vira zero                            | Testes unitários no ETL                  |
| RNF07  | Rastreabilidade: todas as correções expostas em `/qualidade/log`                        | Inspeção do endpoint                     |
| RNF08  | Explicabilidade: cada pedido rejeitado tem motivo em linguagem natural                   | Inspeção da resposta                     |
| RNF09  | Segurança: apenas dados anonimizados; sem tentativa de reidentificação                   | Code review                              |
| RNF10  | Manutenibilidade: ETL, cubagem, otimização e API em módulos separados                    | Estrutura de pastas ([[AGENT_CHARTER]])  |
| RNF11  | Modularidade: novos veículos e eixos entram por CSV, sem alterar código                  | Teste de re-ingestão                     |
| RNF12  | Escalabilidade: arquitetura não depende de regras de uma semana ou veículo específico    | Code review                              |
| RNF13  | Persistência da análise na sessão: resultado permanece até nova execução                 | Manual                                   |
| RNF14  | Tratamento de erros: erros técnicos viram mensagens compreensíveis                       | Inspeção de UI                           |
| RNF15  | Determinismo: mesma entrada → mesma saída do solver                                      | Testes unitários com seed                |

## Convenções de prioridade

- **Obrigatório:** MVP não é entregável sem isso.
- **Recomendado:** MVP entregável, mas com qualidade reduzida.
- **Diferencial:** ganho de pontuação no hackathon; entra depois do MVP funcional.
