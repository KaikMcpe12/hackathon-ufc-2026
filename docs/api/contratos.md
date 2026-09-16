# API — Contratos JSON

Schemas usados em request/response. Espelham Pydantic no backend e TypeScript no frontend.

## Entidades base

### `Eixo`

```json
{
  "id": 4,
  "nome": "Ipaporanga → Poranga → Ararendá",
  "cidades": ["IPAPORANGA", "PORANGA", "ARARENDA"]
}
```

### `Veiculo`

```json
{
  "nome": "ACELLO 815",
  "capacidade_peso": 4800,
  "capacidade_volume": 2.4543,
  "descricao": "Caminhão médio (ideal para eixos longos)"
}
```

### `Item`

```json
{
  "codigo": "14900",
  "descricao": "ARGAMASSA VARANDAS E QUINTAIS 15KG QUARTZOLIT",
  "quantidade": 7.0,
  "unidade_venda": "UN",
  "peso_kg_unit": 15.0,
  "volume_m3_unit": 0.009,
  "peso_total_kg": 105.0,
  "volume_total_m3": 0.063,
  "caixas": null,
  "dado_estimado": true
}
```

### `Pedido`

```json
{
  "pedido": "L12608740",
  "data": "2026-08-03",
  "cidade": "IPAPORANGA",
  "eixo_id": 4,
  "semana": 4,
  "valor": 1811.87,
  "vendedor": "LEONARDO",
  "situacao": "FATURADO",
  "logistica": "ENTREGA",
  "peso_kg": 1196.40,
  "volume_m3": 0.73440,
  "qualidade_cubagem": "COMPLETA",
  "elegivel": true,
  "motivo_exclusao": null,
  "itens": [ /* Item[] */ ]
}
```

- `qualidade_cubagem`: `"COMPLETA"` | `"ESTIMADA"` | `"AUSENTE"`
- `motivo_exclusao`: string ou null (ex.: `"Retirada no balcão"`, `"Cubagem ausente"`, `"Crateús"`)

### `Correcao`

```json
{
  "pedido": "L12608740",
  "campo": "data",
  "valor_original": "26/08/2014",
  "valor_novo": "2026-08-26",
  "regra": "ano_fora_do_lote",
  "criterio": "lote_agosto_2026",
  "aplicada_em": "2026-09-16T04:12:00Z"
}
```

## Requests

### `OtimizarRequest`

```json
{
  "eixo": 4,
  "veiculo": "ACELLO 815",
  "semana": 4,
  "data_carga": "2026-08-24",
  "incluir_estimadas": true
}
```

- `eixo`: int (1–5)
- `veiculo`: string (nome exato da frota)
- `semana`: int (1–4)
- `data_carga`: date (default = hoje se omitido)
- `incluir_estimadas`: bool (default true) — se falso, só 🟢 entra

### `CompararRequest`

```json
{
  "eixo": 4,
  "semana": 4,
  "veiculos": ["HR / BONGO", "ACELLO 815"],
  "data_carga": "2026-08-24"
}
```

### `RevisarCubagemRequest`

```json
{
  "itens": [
    { "codigo": "12185", "peso_kg": 45.0, "volume_m3": 0.18 }
  ]
}
```

## Responses

### `PlanoDeCarga`

```json
{
  "id": "plano_20260824_e4_acello",
  "eixo": { /* Eixo */ },
  "veiculo": { /* Veiculo */ },
  "semana": 4,
  "data_carga": "2026-08-24",
  "totais": {
    "peso_utilizado": 4797.335,
    "peso_capacidade": 4800.0,
    "ocupacao_peso": 0.9994,
    "volume_utilizado": 2.4421,
    "volume_capacidade": 2.4543,
    "ocupacao_volume": 0.9950,
    "valor_total": 16770.85,
    "quantidade_pedidos": 7
  },
  "gargalo": "PESO",
  "violacoes": 0,
  "pedidos_selecionados": [
    {
      "ordem": 1,
      "pedido": "L12608740",
      "cidade": "IPAPORANGA",
      "valor": 1811.87,
      "peso_kg": 1196.40,
      "volume_m3": 0.73440
    }
  ],
  "pedidos_rejeitados": [
    {
      "pedido": "L126010678",
      "cidade": "IPAPORANGA",
      "peso_kg": 530.00,
      "volume_m3": null,
      "motivo": "Cubagem incompleta"
    }
  ],
  "sequencia_descarga": [
    { "ordem": 1, "cidade": "IPAPORANGA", "qtd_pedidos": 2 },
    { "ordem": 2, "cidade": "PORANGA",    "qtd_pedidos": 0 },
    { "ordem": 3, "cidade": "ARARENDA",   "qtd_pedidos": 2 }
  ],
  "orientacao_carregamento": {
    "modo": "LIFO",
    "descricao": "Carregue primeiro os pedidos de Ararendá, depois Poranga, por fim Ipaporanga."
  },
  "gerado_em": "2026-09-16T04:15:00Z"
}
```

### `QualidadeResumo` (de `/qualidade/resumo`)

Ver [[api/endpoints]]#qualidade_resumo.

### `Insight` (de `/insight`)

```json
{
  "resumo": "Esta carga está no limite de peso (99,94%)...",
  "modelo": "anthropic:claude-sonnet-5",
  "duracao_ms": 1234
}
```

### `IngestResumo` (de `/etl/ingest`)

```json
{
  "semanas_atualizadas": [4],
  "resumo_qualidade": { /* QualidadeResumo */ }
}
```

## Tipos TypeScript (frontend)

Frontend mantém `src/api/types.ts` com os mesmos nomes de campo. Snake_case do backend → snake_case no TS (não converter).

Exemplo:
```ts
export interface PlanoDeCarga {
  id: string;
  eixo: Eixo;
  veiculo: Veiculo;
  semana: number;
  data_carga: string;      // ISO date
  totais: {
    peso_utilizado: number;
    peso_capacidade: number;
    ocupacao_peso: number;
    volume_utilizado: number;
    volume_capacidade: number;
    ocupacao_volume: number;
    valor_total: number;
    quantidade_pedidos: number;
  };
  gargalo: "PESO" | "VOLUME";
  violacoes: number;
  pedidos_selecionados: PedidoSelecionado[];
  pedidos_rejeitados: PedidoRejeitado[];
  sequencia_descarga: ParadaDescarga[];
  orientacao_carregamento: OrientacaoCarregamento;
  gerado_em: string;       // ISO datetime
}
```

## Ver também

- [[api/endpoints]] — rotas
- [[arquitetura/backend]] — Pydantic em `src/models/`
