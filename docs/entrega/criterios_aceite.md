# Critérios de Aceite

Checklist para o MVP ser considerado entregável.

## Checklist funcional

### ETL & Cubagem
- [ ] Carrega os 4 CSVs semanais + Ranking Top 85 + Rotas/Coletas
- [ ] Filtra cancelados, retiradas no balcão, Crateús e cidades fora dos eixos
- [ ] Data inconsistente é corrigida (não silenciosamente) e registrada em `qualidade/log`
- [ ] Valor `"R$ 1.811,87"` vira `1811.87`
- [ ] Cidade `"NOVA RUSSAS "` vira `"NOVA RUSSAS"`
- [ ] Parse do `Itens_Resumo` extrai código, quantidade e unidade
- [ ] Conversão m² → caixas usa `ceil(m2 / m2_por_caixa)`
- [ ] Peso ausente **nunca** vira zero — pedido cai em 🔴
- [ ] Cada pedido termina com selo `COMPLETA` / `ESTIMADA` / `AUSENTE`
- [ ] Pedidos 🟡 entram no solver com badge amarelo
- [ ] Pedidos 🔴 vão para fila de revisão, não entram no solver

### Solver
- [ ] Restrição de peso é respeitada (nenhuma solução acima da capacidade)
- [ ] Restrição de volume é respeitada
- [ ] Função objetivo é `0.5·Op + 0.5·Ov`
- [ ] Valor financeiro só desempata quando ocupação é equivalente
- [ ] Gargalo (PESO/VOLUME) é calculado corretamente
- [ ] Cada pedido rejeitado tem motivo em linguagem natural
- [ ] Mesma entrada → mesma saída (determinismo)

### API
- [ ] `GET /eixos`, `GET /veiculos`, `GET /semanas` retornam 200 com dados corretos
- [ ] `POST /otimizar` retorna `PlanoDeCarga` em < 3 segundos
- [ ] `POST /romaneio/generate` retorna PDF válido
- [ ] `POST /etl/ingest` aceita upload multipart e substitui state
- [ ] `GET /qualidade/resumo` alimenta dashboard corretamente

### Frontend
- [ ] Tela `/` (Planejamento) completa: selecionar eixo/veículo/semana → otimizar → ver resultado
- [ ] Tela `/romaneio` renderiza plano de carga e exporta PDF
- [ ] Tela `/simulacao` compara 2 veículos lado a lado
- [ ] Tela `/qualidade` mostra pipeline e KPIs
- [ ] Tela `/triagem` lista pedidos com filtros e permite revisar 🔴
- [ ] Barras de ocupação, badge de gargalo e contador de violações visíveis
- [ ] Ordem de descarga + orientação LIFO exibidas
- [ ] Design fiel aos mockups (preto/branco/amarelo)

## Caso oficial de aceite

**Cenário:** Eixo 4 (Ipaporanga → Poranga → Ararendá) + Veículo ACELLO 815 + Semana 4.

Após pipeline completo sobre os CSVs reais em `backend/data/`, o solver deve reproduzir:

| Indicador                | Valor esperado      |
|--------------------------|---------------------|
| Pedidos selecionados     | 7                   |
| Peso utilizado           | 4.797,335 kg        |
| Capacidade de peso       | 4.800 kg            |
| Ocupação de peso         | 99,94%              |
| Volume utilizado         | 2,4421 m³           |
| Capacidade de volume     | 2,4543 m³           |
| Ocupação de volume       | 99,50%              |
| Gargalo                  | **PESO**            |
| Violações                | 0                   |
| Valor total              | R$ 16.770,85        |

Tolerância: ±0,01 em kg/m³/R$ (arredondamento).

Se qualquer número divergir significativamente, o problema está em uma destas ordens de investigação:

1. **Filtros de elegibilidade** — mais ou menos pedidos que os 93 esperados?
2. **Cubagem** — algum item sendo tratado como zero? Caixas não sendo calculadas?
3. **Estimativas sintéticas** — foram carregadas (necessárias para os 7 pedidos)?
4. **Semana correta** — o solver rodou com `semana=4`?
5. **Solver** — CBC convergiu? `timeLimit` foi suficiente?

## Métricas quantitativas (do PRD)

| Indicador                       | Meta MVP                     | Como verificar             |
|---------------------------------|------------------------------|----------------------------|
| Tempo de montagem de carga      | < 5 minutos                  | Cronômetro na demo         |
| Violações de limite físico      | Zero                         | Testes unitários no solver |
| Ocupação média das cargas       | > 90% na dimensão do gargalo | Rodar todos os eixos       |
| Tempo de resposta do `/otimizar`| < 3 segundos                 | Logs do FastAPI            |

## Testes automatizados obrigatórios

- `test_etl.py`
  - `test_filtra_cancelados()`
  - `test_filtra_retiradas()`
  - `test_filtra_crateus()`
  - `test_normaliza_valor_brasileiro()`
  - `test_corrige_data_fora_lote()`
  - `test_log_correcoes_populado()`

- `test_cubagem.py`
  - `test_parse_item_resumo()`
  - `test_converte_m2_em_caixas_ceil()`
  - `test_ausencia_nao_vira_zero()`
  - `test_classifica_selo_pior_do_pedido()`

- `test_optim.py`
  - `test_nunca_viola_peso()`
  - `test_nunca_viola_volume()`
  - `test_caso_oficial_eixo4_acello()` **(bloqueia PR)**
  - `test_determinismo_com_seed()`
  - `test_motivos_rejeicao_gerados()`

## Ver também

- [[AGENT_CHARTER]]
- [[produto/prd]]#metricas
