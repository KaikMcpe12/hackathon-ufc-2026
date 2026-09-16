# Camada LLM — Insights operacionais

Segunda etapa do motor híbrido. **Opcional, nunca crítica.** Ver [[arquitetura/adr/0007_motor_hibrido_llm]].

## O que faz

Recebe o resultado determinístico do solver e devolve 1–2 parágrafos em português explicando o perfil da carga e sugerindo próximos passos operacionais.

## O que NÃO faz

- Nunca altera peso, volume, ocupação, gargalo ou lista de pedidos.
- Nunca decide se a carga é válida.
- Nunca é obrigatória — se falhar, o resto do sistema continua.

## Contrato de entrada

```json
{
  "eixo": {
    "id": 4,
    "nome": "Ipaporanga → Poranga → Ararendá"
  },
  "veiculo": {
    "nome": "ACELLO 815",
    "capacidade_peso": 4800,
    "capacidade_volume": 2.4543
  },
  "resultado": {
    "peso_utilizado": 4797.335,
    "volume_utilizado": 2.4421,
    "ocupacao_peso": 0.9994,
    "ocupacao_volume": 0.9950,
    "gargalo": "PESO",
    "pedidos_selecionados": 7,
    "pedidos_rejeitados": 3,
    "valor_total": 16770.85
  },
  "rejeitados_top": [
    {"pedido": "L126010678", "motivo": "Excederia peso em 320 kg"}
  ]
}
```

## Contrato de saída

```json
{
  "resumo": "1–2 parágrafos em pt-BR",
  "modelo": "identificador do modelo usado",
  "duracao_ms": 1234
}
```

## Prompt (base)

Arquivo: `src/llm/prompt.py`

Sistema:

> Você é um assistente de logística especializado em otimização de cargas para transporte de materiais de construção. Você recebe um resultado determinístico de um solver e produz um comentário curto, prático e sem jargão para um coordenador de logística brasileiro.
>
> Regras:
> 1. Nunca altere os números — só os interprete.
> 2. Use no máximo 2 parágrafos curtos.
> 3. Português brasileiro, tom direto e cordial.
> 4. Se o gargalo é PESO, sugira itens de menor densidade para próximas cargas. Se é VOLUME, sugira itens mais compactos.
> 5. Se algum pedido foi rejeitado por pouco (< 5% da capacidade), sugira revisar.
> 6. Não invente dados que não estão na entrada.

Usuário: JSON de entrada.

## Fallback

Se o LLM falhar (rate limit, timeout, sem chave, provedor offline):

- API `POST /insight` retorna 503 com `{"erro": "LLM indisponível"}`.
- Frontend mostra bloco recolhido: "Insight de IA não disponível no momento."
- Nenhum outro fluxo é afetado.

## Segurança e privacidade

- Nunca enviar identificação de cliente para o LLM (a base já é anonimizada).
- Nunca enviar valores absolutos que permitam reidentificar (o resumo é agregado).
- Se provedor externo, garantir Zero Data Retention na configuração.

## UI

Bloco separado dentro de [[frontend/telas]]#planejamento, com label clara "Insight gerado por IA · nunca substitui os números do solver".

## Ver também

- [[arquitetura/adr/0007_motor_hibrido_llm]]
- [[api/endpoints]]#insight
