# PRD-12 — Persistência em Banco de Dados (passo otimista, branch separada)

> **Status:** proposto (futuro) · **Branch:** `feature/persistencia-db` (avaliada e depois mesclada à `main`)
> **Depende de:** MVP + PRD-10 concluídos · **Estende:** [[arquitetura/adr/0010_persistencia_opcional]]
> **Objetivo:** sair do estado in-memory efêmero para persistir os dados, viabilizando **cadastro** (individual ou em lote por CSV), **histórico** e sobrevivência a reinícios.

## 1. Contexto e motivação

Hoje o estado é in-memory (ADR 0001): o seed carrega no boot, o upload (`/etl/ingest`) é efêmero e o reinício zera tudo. Isso é ótimo para a demo, mas impede:
- reter uploads/histórico entre reinícios (hoje some no restart/spin-down do Render);
- **cadastrar** produtos/pedidos de forma incremental (um a um) sem reenviar todos os CSVs;
- consultar planos de carga anteriores.

Este PRD introduz um banco **atrás da mesma interface de `state.py`**, sem reescrever o domínio (etl/cubagem/optim continuam funções puras e testáveis).

## 2. Sua ideia + proposta refinada

**Sua ideia:** cadastrar 1 registro por **formulário** (dependendo do contexto) OU, se houver CSV pronto, **fazer upload** e o sistema captura os registros a cadastrar — respeitando restrições do banco (PK, regras de negócio).

**Proposta (mantém a sua e melhora):** um mesmo fluxo de **ingestão idempotente** serve os dois caminhos (form = 1 registro; CSV = N registros), com **upsert** e validação:

```
Formulário (1 registro) ─┐
                         ├─►  Validação (schema + regras) ─► UPSERT no banco ─► reprocessa pipeline ─► estado
Upload CSV (N registros)─┘        │ erros por linha
                                  └─► relatório: inseridos / atualizados / rejeitados (com motivo)
```

Por que isso é melhor que só "inserir":
- **Upsert (inserir OU atualizar)** pela chave natural evita erro de PK duplicada e permite reenvio/correção.
- **Validação por linha** com relatório (não falha o lote inteiro por 1 linha ruim) — cada rejeitada volta com o motivo.
- **Mesma regra de negócio** já existente (elegibilidade, cubagem) roda sobre os dados persistidos, mantendo o gate.

## 3. Entidades e chaves (modelo)

| Tabela | Chave natural (PK) | Origem hoje | Observações |
|--------|--------------------|-------------|-------------|
| `produto` | `codigo` | Ranking Top 85 + sintéticos | peso/volume/unidade; `fonte`, `dado_estimado` |
| `eixo` | `id` | Rotas | nome + cidades |
| `veiculo` | `nome` | Rotas | capacidades, `selecionavel` |
| `pedido` | `pedido` (ex.: L12608740) | Semanas | data, cidade, valor, semana, situação… |
| `pedido_item` | (`pedido`, `codigo`) | Itens_Resumo | quantidade, unidade |
| `entrega` (vendas) | `pedido` | Vendas_Faturamento | status faturamento/entrega |
| `plano_carga` | `id` (uuid) | gerado pelo solver | snapshot + PDF (histórico) |
| `log_correcao` | `id` | ETL | auditoria permanente |

Restrições: FK `pedido_item.codigo → produto.codigo` (ou permitir código órfão → vira 🔴/revisão), `pedido.eixo_id` derivado por cidade. `pedido_item` PK composta evita duplicar item no pedido.

## 4. Contexto de cadastro (o "dependendo de qual contexto")

O formulário/CSV muda conforme a **entidade**:

| Contexto | Formulário (1) | CSV (N) | Regra-chave |
|----------|----------------|---------|-------------|
| **Produto** | código, descrição, unidade, peso, volume | ranking_top85.csv | upsert por `codigo`; se já existe, atualiza |
| **Pedido** | pedido, data, cidade, valor, itens[] | pedidos_semana_N.csv | upsert por `pedido`; recalcula cubagem/elegibilidade |
| **Eixo/Veículo** | (form admin) | rotas_coletas.csv | substitui config |
| **Entrega** | — | vendas_faturamento.csv | enriquece pedido |

## 5. Arquitetura (mínima invasão)

- **`StateRepository`** (interface): `get_state()`, `save_pedido()`, `upsert_produtos(rows)`, `list_planos()`, `save_plano()`…
- Implementações selecionáveis por env `STATE_BACKEND=memory|sqlite|postgres`:
  - `InMemoryRepository` = comportamento atual (default) → nada muda para a demo.
  - `SqlRepository` (SQLAlchemy) → SQLite (1 host) ou Postgres (produção).
- **Reprocessamento:** após qualquer upsert, o pipeline (etl→cubagem→enriquecimento) roda sobre os dados do banco e republica o `AppState`. Domínio **inalterado**.
- **Migrations:** Alembic. Seed inicial = os CSVs atuais importados uma vez.

## 6. Telas novas / alteradas

**Novas:**
- **Cadastro / Catálogo** (rota `/cadastro`): abas Produtos · Pedidos. Cada aba com botão **"+ Novo"** (form) e **"Importar CSV"** (dropzone → relatório inseridos/atualizados/rejeitados). Reusa o padrão da tela **Importar** atual.
- **Histórico de planos** (rota `/historico`): lista de planos salvos (data, eixo, veículo, ocupação) com re-download do PDF.

**Alteradas:**
- **Importar** atual: passa a persistir (não mais efêmero) e mostra inseridos/atualizados/rejeitados.
- **Triagem / detalhe do pedido**: botões editar/excluir; a revisão de cubagem (UC07) passa a persistir.
- **Qualidade**: log de correções vira histórico permanente (consulta por data).
- **Header**: indicador de origem dos dados (banco vs seed/memória).

## 7. Fora do escopo (deste PRD)
- Autenticação/perfis (provável pré-requisito real de um cadastro — sinalizar como PRD seguinte).
- Sincronização com o ERP da empresa.
- Multiusuário concorrente com locks avançados.

## 8. Riscos e mitigações
| Risco | Mitigação |
|-------|-----------|
| Cadastro sem auth = qualquer um edita | Marcar auth como pré-requisito; começar restrito ao coordenador |
| Divergência de chave (pedido com/sem "L") | Normalizar a chave natural na entrada (já feito no cruzamento de vendas) |
| Lote grande trava a request | Processar em transação com limite; relatório assíncrono se necessário |
| Quebrar o gate | Pipeline roda igual sobre o banco; teste do caso oficial continua obrigatório |
| Migrations vs ADR 0001 | Persistência é **opt-in** por env; memory continua default |

## 9. Critérios de aceite
- [ ] `STATE_BACKEND=sqlite` sobe, importa o seed uma vez e reproduz **688→93→81** + gate.
- [ ] Cadastro de 1 produto por form → aparece no catálogo e no cruzamento de cubagem.
- [ ] Upload de CSV → relatório com inseridos/atualizados/rejeitados (por linha).
- [ ] Reenvio do mesmo registro **atualiza** (não duplica PK).
- [ ] Reinício do processo **mantém** os dados (diferente de hoje).
- [ ] `STATE_BACKEND=memory` = comportamento atual intacto (regressão zero).

## 10. Perguntas para você (antes de implementar)
1. **Banco:** SQLite (simples, 1 host) ou já Postgres (produção)? Recomendo começar SQLite e deixar o Postgres plugável.
2. **Auth:** entra junto (cadastro pede login) ou fica para um PRD depois? Recomendo pelo menos um login simples de coordenador.
3. **Escopo do cadastro no v1:** só **Produtos** (catálogo) ou **Produtos + Pedidos**? Recomendo Produtos primeiro (menor risco, alto valor para a cubagem).
4. **Histórico de planos:** guardar o PDF também ou só os números? 

## Ver também
[[arquitetura/adr/0010_persistencia_opcional]] · [[prd/09-reingestao-testes]] · [[prd/10-pos-mvp-melhorias]] · [[dominio/pipeline_etl]]
