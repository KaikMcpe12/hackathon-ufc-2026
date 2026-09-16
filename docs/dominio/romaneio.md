# Romaneio / Plano de Carga

Artefato final entregue à expedição. É o que a banca do hackathon avalia.

## Formato

- **PDF A4**, retrato, otimizado para impressão em preto-e-branco (sem perder legibilidade).
- Gerado via WeasyPrint no backend a partir de template HTML + Jinja2. Ver [[arquitetura/adr/0004_pdf_backend]].
- Template em `src/romaneio/template.html`.

## Estrutura (base: mockup Image 1)

### Cabeçalho

- Logo Nobre Lar + "NobreLOG · Inteligência Logística"
- Título: **"Plano de carga / Romaneio"**
- Subtítulo: "Documento operacional para expedição e conferência"

### Bloco de metadados

| Campo         | Fonte                                             |
|---------------|---------------------------------------------------|
| Veículo       | request                                           |
| Eixo          | ID + cidades ordenadas (ex.: "4 · Ipaporanga → Poranga → Ararendá") |
| Data da carga | request (default: hoje)                           |
| Coordenador   | request (default: "—")                            |
| Status        | "Carga válida" se violações = 0                   |

### KPIs

Quatro cards:
- Peso total utilizado (`X / Y kg` + barra de %)
- Volume total utilizado (`X / Y m³` + barra de %)
- Valor total da carga (R$)
- Pedidos na carga (`N de M disponíveis`)

### Sequência de descarga

Lista numerada de cidades na ordem oficial do eixo, com contagem de pedidos por cidade:

```
1  Ipaporanga    2 pedidos
2  Poranga       Nenhum pedido
3  Ararendá      2 pedidos
```

Se uma cidade do eixo não tem pedido, ainda aparece com "Nenhum pedido" (mantém a rota como referência).

### Orientação de carregamento (LIFO)

Bloco com ícone + texto claro:

> **Carregue na ordem inversa da entrega.** Para facilitar a descarga, posicione os pedidos de Ararendá por último, depois Poranga e por fim Ipaporanga (primeira entrega).

### Tabela de pedidos

| Ordem | Pedido     | Cidade      | Valor (R$) | Peso (kg) | Volume (m³) | Observação |
|-------|------------|-------------|------------|-----------|-------------|------------|
| 1     | L12608740  | Ipaporanga  | 1.811,87   | 1.196,40  | 0,73440     | —          |
| 2     | L8507237   | Poranga     | 176,00     |    86,00  | 0,05400     | —          |
| ...   |            |             |            |           |             |            |
| Total |            |             | 6.744,89   | 3.763,24  | 2,45103     | —          |

**Ordem = ordem de descarga.** A tabela é ordenada pela sequência do eixo.

### Rodapé — assinaturas

Três campos:
- Conferente (nome + assinatura)
- Motorista (nome + assinatura)
- Expedição (nome + assinatura)

## Regras de LIFO

**Ordem de carregamento é INVERSA à ordem de descarga.**

Exemplo (Eixo 4, cidades A → B → C):
- Descarga: A, B, C
- Carregamento: C (fundo do baú), B (meio), A (porta)

Assim a primeira entrega (A) fica acessível na porta e a última (C) no fundo.

Se uma cidade não tem pedido, ela é ignorada no cálculo de carregamento (mas mantida na rota como referência).

## API

`POST /romaneio/generate` recebe:

```json
{
  "plano": { "...saída do POST /otimizar..." },
  "coordenador": "João Silva",
  "data_carga": "2026-08-24"
}
```

Devolve `application/pdf` como binário ou URL para download.

## Regras invioláveis

1. **Números do PDF = números do solver.** Nunca recalcular no template.
2. **Se `violacoes > 0`, o PDF NÃO é gerado.** API retorna 422.
3. **Rodapé sempre inclui a versão do sistema** para rastreabilidade.

## Ver também

- [[arquitetura/adr/0004_pdf_backend]]
- [[frontend/telas]]#romaneio
- [[api/endpoints]]#romaneio_generate
