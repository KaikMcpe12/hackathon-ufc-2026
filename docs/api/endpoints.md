# API — Endpoints

Base: `/api/v1`. Todos os endpoints retornam JSON (exceto `/romaneio/generate` que retorna PDF).

## Metadados

### GET `/eixos`

Lista os 5 eixos com cidades ordenadas.

- **200** `{ eixos: Eixo[] }`

### GET `/veiculos`

Lista os 3 veículos com capacidades (HR/BONGO, ACELLO 815, MOTOS).

- **200** `{ veiculos: Veiculo[] }`

### GET `/semanas`

Semanas disponíveis no estado atual.

- **200** `{ semanas: [1,2,3,4], padrao: 4 }`

## Pedidos

### GET `/pedidos`

Lista pedidos com filtros.

Query params:
- `eixo` (opcional): 1–5
- `semana` (opcional): 1–4
- `qualidade` (opcional): `COMPLETA`, `ESTIMADA`, `AUSENTE`
- `cidade` (opcional)
- `status` (opcional)
- `q` (opcional): busca livre em pedido, cliente, observação

- **200** `{ total: int, pedidos: Pedido[] }`

### GET `/pedidos/{pedido_id}`

Detalhe do pedido, incluindo itens e motivo de exclusão (se houver).

- **200** `Pedido`
- **404** se não existe

### POST `/pedidos/{pedido_id}/revisar`

Coordenador aprova/edita cubagem manual de um pedido 🔴. Ao aprovar, pedido passa a 🟡.

Body:
```json
{
  "itens": [
    { "codigo": "12185", "peso_kg": 45.0, "volume_m3": 0.18 }
  ]
}
```

- **200** `Pedido` (atualizado, agora 🟡)
- **422** se dados inválidos

## Qualidade

### GET `/qualidade/resumo`

KPIs para dashboard [[frontend/telas]]#qualidade_dados.

- **200**
```json
{
  "registros_processados": 688,
  "inconsistencias_detectadas": 1,
  "materiais_ranking": 85,
  "pedidos_completa": 46,
  "pedidos_estimada": 12,
  "pedidos_ausente": 6,
  "pipeline_stages": [
    { "nome": "Importacao", "registros": 688, "percentual": 100.0 },
    { "nome": "Limpeza",    "registros": 687, "percentual": 99.9 },
    { "nome": "Conversao",  "registros": 687, "percentual": 99.9 },
    { "nome": "Cubagem",    "registros": 649, "percentual": 94.3 },
    { "nome": "Validacao",  "registros": 646, "percentual": 93.9 }
  ]
}
```

### GET `/qualidade/log`

Log rastreável de correções aplicadas no ETL.

- **200** `{ correcoes: Correcao[] }`

### GET `/qualidade/motivos-exclusao`

Contagem de pedidos excluídos por motivo (para painel lateral da tela de triagem).

- **200**
```json
{
  "motivos": [
    { "motivo": "Retirada no balcão", "total": 18, "percentual": 38.3 },
    { "motivo": "Crateús",            "total": 11, "percentual": 23.4 },
    { "motivo": "Cancelado",          "total":  8, "percentual": 17.0 },
    { "motivo": "Cubagem ausente",    "total":  7, "percentual": 14.9 },
    { "motivo": "Data inconsistente", "total":  3, "percentual":  6.4 }
  ]
}
```

## Otimização

### POST `/otimizar`

Executa MILP para 1 eixo + 1 veículo + 1 semana.

Body:
```json
{
  "eixo": 4,
  "veiculo": "ACELLO 815",
  "semana": 4,
  "data_carga": "2026-08-24",
  "incluir_estimadas": true
}
```

- **200** `PlanoDeCarga`
- **400** se input inválido
- **422** se não há pedidos elegíveis para o cenário

### POST `/otimizar/comparar` <a id="comparar"></a>

Executa otimização para 2 veículos no mesmo eixo/semana.

Body:
```json
{
  "eixo": 4,
  "semana": 4,
  "veiculos": ["HR / BONGO", "ACELLO 815"],
  "data_carga": "2026-08-24"
}
```

- **200**
```json
{
  "cenarios": [
    { "veiculo": "HR / BONGO", "resultado": PlanoDeCarga },
    { "veiculo": "ACELLO 815", "resultado": PlanoDeCarga }
  ],
  "recomendado": "ACELLO 815"
}
```

## Romaneio

### POST `/romaneio/generate` <a id="romaneio_generate"></a>

Gera PDF do plano de carga.

Body: `{ plano: PlanoDeCarga, coordenador: str, data_carga: date }`

- **200** `application/pdf` (binário)
- **422** se plano tem violações > 0

## Insight (LLM)

### POST `/insight`

Gera resumo em linguagem natural do plano de carga.

Body: `{ plano: PlanoDeCarga }`

- **200** `{ resumo: str, modelo: str, duracao_ms: int }`
- **503** se LLM indisponível (fallback silencioso no frontend)

## ETL

### POST `/etl/ingest` <a id="etl_ingest"></a>

Substitui o estado in-memory a partir de CSVs subidos. Multipart form-data:

- `semana_1` (opcional): CSV
- `semana_2` (opcional): CSV
- `semana_3` (opcional): CSV
- `semana_4` (opcional): CSV
- `ranking` (opcional): CSV
- `rotas` (opcional): CSV

Só os arquivos enviados são substituídos.

- **200** `{ semanas_atualizadas: [int], resumo_qualidade: QualidadeResumo }`
- **400** se colunas esperadas ausentes

## Convenções de erro

Toda resposta de erro segue:

```json
{
  "code": "PEDIDO_NAO_ENCONTRADO",
  "message": "Pedido L99999999 não existe no estado atual.",
  "details": { "pedido": "L99999999" }
}
```

## Ver também

- [[api/contratos]] — schemas Pydantic
- [[dominio/otimizacao]] — o que roda em `/otimizar`
