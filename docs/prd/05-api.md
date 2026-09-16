# PRD-05 — API de aplicação

> **Status:** proposto. Depende de: [[prd/02-pipeline-etl]], [[prd/03-cubagem]], [[prd/04-otimizacao]].
> Expõe o domínio via rotas FastAPI **thin** (só orquestram) e os contratos Pydantic de [[api/contratos]].

## Objetivo

Implementar as rotas de aplicação de [[api/endpoints]] (exceto `/romaneio/generate` → PRD-06, `/insight` → PRD-07, `/etl/ingest` → PRD-09) e os schemas Pydantic em `src/models/`, espelhando exatamente [[api/contratos]] (snake_case, sem conversão).

## Escopo

**Dentro:**
- `GET /pedidos` (filtros `eixo, semana, qualidade, cidade, status, q`) → `{ total, pedidos[] }`.
- `GET /pedidos/{id}` → `Pedido` | 404.
- `POST /pedidos/{id}/revisar` → aprova/edita cubagem de 🔴; passa a 🟡; retorna `Pedido` | 422.
- `GET /qualidade/resumo` → `QualidadeResumo` (números reais do pipeline; contrato I7: `completa+estimada+ausente == elegiveis`).
- `POST /otimizar` → `PlanoDeCarga` (< 3s) | 400 (input inválido, ex.: veículo não selecionável — I3) | 422 (sem pedidos elegíveis).
- `POST /otimizar/comparar` → `{ cenarios[], recomendado }` — **backend calcula `recomendado`** (E6).
- Modelos Pydantic: `Eixo, Veiculo, Item, Pedido, Correcao, PlanoDeCarga, QualidadeResumo, OtimizarRequest, CompararRequest, RevisarCubagemRequest`.
- Handler de erro padrão `{ code, message, details }`.

**Fora:** PDF (PRD-06), LLM (PRD-07), upload (PRD-09).

## Contratos (correções aplicadas do PRD-00)
- `Veiculo` ganha `selecionavel: bool` (I3).
- `peso_kg`/`volume_m3` → `Optional[float]` em `Pedido`/rejeitados/selecionados (I4).
- `Correcao` ganha `acao` (E5); `valor_novo` ISO (I2).
- `motivo_exclusao`/`motivo` usam o enum canônico (I6).
- `QualidadeResumo`: exemplos dos docs marcados como ilustrativos; valores reais em runtime (I7/I8).
- `RomaneioGenerateRequest` e resposta de `/otimizar/comparar` ganham schema explícito (lacunas apontadas na análise).

## Regras invioláveis (Charter)
- Rotas thin: validam, chamam função pura, formatam. Zero lógica de negócio na rota.
- `/otimizar` nunca devolve carga com violação.

## Critérios de aceite
- [ ] `POST /otimizar` (caso oficial) retorna `PlanoDeCarga` correto em **< 3s**.
- [ ] `POST /otimizar` com `veiculo="MOTOS"` → 400 (I3).
- [ ] `GET /pedidos?qualidade=AUSENTE` lista só 🔴; `?eixo=4&semana=4` filtra corretamente.
- [ ] `POST /pedidos/{id}/revisar` transforma 🔴→🟡 e o pedido passa a entrar no solver.
- [ ] `GET /qualidade/resumo`: `completa+estimada+ausente == elegiveis` (I7).
- [ ] `/otimizar/comparar` retorna `recomendado` calculado no backend (E6).
- [ ] Erros seguem `{code,message,details}`.

## Testes
`test_api.py`: metadados, `/pedidos` filtros, revisar 🔴→🟡, `/otimizar` caso oficial via HTTP, `/otimizar` 400 MOTOS, resumo fecha soma, comparar recomendado.

## Riscos
- Divergência snake_case entre back e front — types.ts espelha 1:1.
- Tempo < 3s com pool grande — solver já limitado por `timeLimit=30`, mas o caso real é pequeno.

## Ver também
[[api/endpoints]] · [[api/contratos]] · [[arquitetura/backend]]
