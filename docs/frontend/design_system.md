# Design System

Baseado nos mockups (Image 1–5). Identidade visual: preto/branco/amarelo Nobre Lar.

## Paleta

### Neutros

| Token         | Hex        | Uso                                       |
|---------------|------------|-------------------------------------------|
| `neutral-50`  | `#F9FAFB`  | Background da página                      |
| `neutral-100` | `#F3F4F6`  | Background de cards secundários           |
| `neutral-200` | `#E5E7EB`  | Bordas, divisores                         |
| `neutral-400` | `#9CA3AF`  | Texto de rótulos secundários              |
| `neutral-600` | `#4B5563`  | Texto de corpo                            |
| `neutral-900` | `#111827`  | Títulos, headers hero                     |
| `black`       | `#000000`  | Botões primários                          |

### Marca

| Token         | Hex        | Uso                                       |
|---------------|------------|-------------------------------------------|
| `yellow-400`  | `#F5C518`  | Accent principal (barras de ocupação, links) |
| `yellow-500`  | `#EAB308`  | Botões primários coloridos ("Otimizar")   |
| `yellow-100`  | `#FEF3C7`  | Backgrounds de alerta amarelo             |

### Semânticos

| Token         | Hex        | Uso                                       |
|---------------|------------|-------------------------------------------|
| `success`     | `#10B981`  | Status "Carga válida", "Elegível"         |
| `warning`     | `#F59E0B`  | Alertas amarelos, cubagem estimada        |
| `danger`      | `#EF4444`  | Violações, cubagem ausente                |
| `info`        | `#3B82F6`  | Badges informativas ("Separacao")         |

## Tipografia

Fonte: **Inter** (Google Fonts) ou similar sans-serif geométrica.

| Estilo         | Tamanho | Peso | Uso                              |
|----------------|---------|------|----------------------------------|
| Display XL     | 40px    | 700  | Header hero das telas            |
| Display L      | 28px    | 700  | Títulos de seção                 |
| Title M        | 20px    | 600  | Títulos de card, "Configurar carga" |
| Body           | 14px    | 400  | Texto de corpo                   |
| Label          | 12px    | 500  | Rótulos de campo, sublabels      |
| Numeric XL     | 32px    | 700  | KPIs principais (peso, volume)   |
| Numeric M      | 24px    | 700  | KPIs secundários                 |

Números tabulares (`font-variant-numeric: tabular-nums`) em toda a UI.

## Formatação de valores

- **Moeda:** `R$ 6.744,89` — `pt-BR`, sempre 2 casas.
- **Peso:** `3.763,24 kg` — separador de milhar `.`, decimal `,`, 2 casas.
- **Volume:** `2,45103 m³` — até 5 casas para preservar precisão do solver.
- **Porcentagem:** `99,9%` — 1 casa decimal na UI, sem espaço antes do `%`.

Helper em `src/lib/format.ts`.

## Componentes-chave

### `<KpiCard>`

Card branco com bordas suaves, contendo:
- Ícone (esquerda superior)
- Label (12px, neutral-400)
- Valor grande (Numeric XL, neutral-900)
- Subtítulo com valor de capacidade (`X / Y kg`)
- Barra de progresso (amarela) + % à direita

### `<OcupacaoBar>`

Barra horizontal com altura ~8px, `bg-neutral-200` como trilha, `bg-yellow-400` como preenchimento. `% > 95` transita para tom mais forte (`yellow-500`).

### `<GargaloBadge>`

Chip com texto uppercase `PESO` ou `VOLUME`, fundo `bg-yellow-100`, borda `border-warning`.

### `<StatusBadge>`

- Verde: `Carga válida`, `Elegível`
- Amarelo: `Cubagem estimada`, `Cubagem incompleta`
- Vermelho: `Cancelado`, `Violação`
- Azul: `Faturado`, `Separacao`

### `<TabelaPedidos>`

Tabela zebrada suave (`odd:bg-neutral-50`), linhas hover (`hover:bg-neutral-100`). Última linha "Total" em `font-semibold` com borda superior grossa.

## Layout

- Largura máxima do conteúdo: `max-w-[1440px]` centralizado.
- Grid principal: 8 colunas de conteúdo + 4 colunas de painel lateral direito.
- Gaps: `gap-6` (24px) entre cards principais, `gap-4` (16px) entre KPIs.
- Header fixo no topo com altura 64px.

## Ícones

Lucide Icons (`lucide-react`). Tamanhos: 16px em botões/labels, 20px em cards, 24px em headers.

## Estados

- **Loading:** skeletons cinza com pulse (`animate-pulse`) para KPIs e tabelas.
- **Vazio:** ilustração + texto amigável ("Nenhum pedido para os filtros atuais.").
- **Erro:** banner vermelho no topo do bloco afetado.

## Responsividade

Foco em desktop (1280+). Para larguras < 1024px:
- Painel lateral vira modal.
- KPIs empilham em 2 colunas.
- Tabelas com scroll horizontal.

Mobile é secundário no MVP.

## Ver também

- [[frontend/telas]] — como os componentes se combinam em cada tela
