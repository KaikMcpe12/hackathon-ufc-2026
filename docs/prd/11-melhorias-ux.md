# PRD-11 — Mapa de Melhorias de UX/UI, Acessibilidade, PDF e Front-end

> **Nota:** boa parte do P0 já foi implementada (shadcn/ui, hero, nav pills, cards/métricas/tabelas/comboboxes, donut, pipeline stepper, PDF redesenhado). Este doc segue como mapa do que resta (a11y fina, responsividade mobile, micro-animações extras, painel de detalhe da triagem).

> **Status:** proposto. Mapa completo dos pontos de melhoria do front-end (6 telas), do PDF do romaneio,
> do design system, acessibilidade, responsividade e micro-interações — comparando o que está implementado
> (`frontend/`) com o design de referência [[inspiracao/NobreLOG_HTML_CSS]] e os mockups de [[inspiracao]].
> Legenda de prioridade: **P0** essencial · **P1** alto impacto · **P2** refinamento. Esforço: S/M/G.

## 0. Diagnóstico resumido

O backend está sólido; o front-end atual é **funcional mas visualmente cru** e diverge do design de referência:
não tem **hero**, usa amarelo errado (`#F5C518` em vez de `#ffc400`), cards planos sem sombra/ícone,
sem ilustração de caminhão, sem stepper de rota/pipeline, sem donut, selects não pesquisáveis, tabelas sem
container arredondado/sticky, zero micro-animações, acessibilidade mínima e responsividade só via grid solto.
O **PDF** usa um layout próprio, mais pobre que a web, com KPIs vazios e metade da página em branco.

---

## 1. Biblioteca de design & stack visual (P0)

| Item | Decisão proposta | Esforço |
|---|---|---|
| **shadcn/ui** (Radix + Tailwind + CVA) | Adotar como base de componentes acessíveis (Dialog, Select, Command, Tabs, Tooltip, Toast, Skeleton). Dá acessibilidade "de graça" (foco, ARIA, teclado). | G |
| **lucide-react** | Ícones consistentes (16/20/24) nos chips de card, nav, botões (hoje uso emoji/nada). | S |
| **framer-motion** | Micro-animações declarativas (entrada de cards, contagem de KPIs, transição de página). | M |
| **cmdk** (via shadcn `Command`) | Seletores pesquisáveis de eixo/veículo/cidade (⌘K e comboboxes). | M |
| **@tanstack/react-table** | Tabelas com ordenação, densidade e colunas configuráveis. | M |
| **sonner** | Toasts de sucesso/erro (otimização feita, PDF exportado, upload). | S |
| **tailwind-merge + clsx/cva** | Variantes de componente sem `className` frágil. | S |
| Tokens do Tailwind | Alinhar ao CSS de referência: `--y:#ffc400`, `--ink:#11141a`, `--muted:#667085`, `--line:#e4e7ec`, `--bg:#f3f5f7`, `--green:#18b96b`, `--red:#e5484d`, radius **18px**, sombra `0 10px 28px rgba(18,24,33,.06)`. | S |
| Fonte Inter | Carregar via `@fontsource/inter` (hoje depende do sistema). | S |

> Alternativa ao shadcn/ui: **Radix puro + CVA** (mais leve) ou **Park UI/Mantine**. Recomendo shadcn/ui pela aderência ao Tailwind já usado.

---

## 2. Layout global & navegação (P0)

- **Hero por tela** (falta 100%): faixa escura com gradiente, marca-d'água "NL", título 40–46px com destaque amarelo + subtítulo. É a assinatura visual do produto.
- **Top bar** (76px): logo `N` + `L` amarelo (letter-spacing negativo), "NobreLOG · Inteligência Logística", **chip de usuário** com avatar à direita.
- **Nav em pills** arredondadas (`border-radius:999px`), ativa = escura; hoje uso retângulos.
- **Larguras/espaçamento**: `max-w-[1660px]`, `padding` 18–22px, `gap` 16px entre cards (hoje `1440px`/`gap-6`). Escala de espaçamento consistente (4/8/12/16/24).
- **Grid "two"**: conteúdo (2fr) + painel lateral (0.9fr, min 340px). Alinhar todas as telas a esse padrão.
- **Sticky header** com leve sombra ao rolar.

---

## 3. Componentes (P0/P1)

| Componente | Melhoria | Prioridade |
|---|---|---|
| **Card** | Sombra suave, radius 18, `.title` com **chip de ícone** (38px, bg cinza) + título + subtítulo. | P0/S |
| **MetricCard** | Rótulo, número 24px, barra de progresso animada, % à direita, subtítulo ("de 93 candidatos"). Padronizar altura (hoje "Valor/Pedidos" ficam vazios). | P0/S |
| **OcupacaoBar** | Altura 10px, trilha `#edf0f4`, animar preenchimento; cor vira `#eab308` acima de 95%. | P1/S |
| **Ilustração de caminhão** (CSS art) | Presente na referência (Planejamento/Simulação/Romaneio) — hoje ausente. Recriar como componente SVG/CSS. | P1/M |
| **RouteStepper** | Dots numerados + linhas tracejadas + destaque de paradas com pedido; `notice` quando cidade sem pedido. Hoje é lista simples. | P1/M |
| **PipelineStepper** (Qualidade) | 5 estágios em círculos (Importação→Situação→Eixo→Cubagem→Validação) com número e %. | P1/M |
| **Donut de cobertura** (Qualidade) | `conic-gradient` 🟢/🟡/🔴 com total ao centro. Hoje inexistente. | P1/M |
| **ScenarioCard** (Simulação) | Card com foto do veículo, KPIs e **borda dourada** no recomendado; badges "Limite de peso/volume/Melhor equilíbrio". | P1/M |
| **Tabela** | Container arredondado com borda, `thead` fundo `#f2f4f7` **sticky**, hover de linha, `tfoot` de total destacado, `tabular-nums`, densidade compacta, scroll-x no mobile. | P0/M |
| **Formulário** | `field` com label 12px/700, inputs 46px, foco com anel amarelo, `Select` pesquisável (combobox), toggle estilizado para "incluir estimadas", link "Configurações avançadas". | P0/M |
| **Badges** | Paleta completa: green/red/warn/blue/gray/purple + **selo de retirada** (faltava no design system). Mapear status→cor num único lugar. | P1/S |
| **Notice/Soft box** | Caixas amarelas de aviso e caixas "soft" de destaque (fator limitante, orientação). | P1/S |
| **Botões** | 46px, variantes `yellow`/`dark`/`light`, ícone à esquerda, estado `:active`/loading com spinner. | P1/S |

---

## 4. Micro-animações (P1/P2)

- **Contagem animada** dos KPIs (0 → valor) ao otimizar.
- **Preenchimento animado** das barras de ocupação (width transition + ease).
- **Entrada de cards** (fade+slide) com `framer-motion` (stagger).
- **Hover lift** nos cards (translateY -2px + sombra).
- **Transição de página** entre rotas.
- **Skeletons** com shimmer no lugar de "carregando…".
- **Respeitar `prefers-reduced-motion`** (desligar animações).

---

## 5. Acessibilidade (P0)

- **HTML semântico**: `header/nav/main/aside/section`, `<table>` com `<caption>`/`scope`.
- **Foco visível**: anel `focus-visible` em todos os interativos (hoje ausente).
- **ARIA**: `aria-label` nos ícones-só, `aria-live="polite"` no bloco de resultado da otimização, `aria-busy` durante carregamento, `role="alert"` nos banners de erro.
- **Contraste**: revisar amarelo sobre branco (texto sobre `#ffc400` deve ser `#11141a`); `muted #667085` ok em branco.
- **Teclado**: navegação por Tab, `Esc` fecha modais, comboboxes navegáveis (shadcn cobre).
- **Labels**: todo input com `<label htmlFor>`; selects com nome acessível.
- **Alvo de toque** ≥ 44px no mobile.
- **`lang="pt-BR"`** (ok) e títulos de página por rota (`document.title`).

---

## 6. Responsividade (P0/P1)

- Breakpoints do design: **1100px** (2col→1col, métricas 4→2, form 4→2, stages 5→3) e **720px** (tudo 1col, hero menor, stages 2col, nav compacta).
- **Nav mobile**: pills com scroll horizontal ou menu "hambúrguer".
- **Painel lateral** vira bloco empilhado (hoje quebra sem ordem clara).
- **Tabelas**: container com scroll-x + min-width; considerar "cards" por linha no mobile.
- **Hero**: reduzir tipografia e padding no mobile.
- Testar 360/768/1024/1440.

---

## 7. Estados & feedback (P1)

- **Loading**: skeletons por bloco (KPIs, tabela) em vez de texto.
- **Vazio**: ilustração + texto amigável ("Otimize uma carga para ver o resultado").
- **Erro**: banner `role="alert"` no topo do bloco + toast.
- **Sucesso**: toast ("Plano gerado", "PDF exportado", "Dados reingeridos").
- **Bloco de IA**: estados carregando/sucesso/indisponível já previstos — refinar visual (chip "IA", colapsável).

---

## 8. PDF do Romaneio (P0) — problemas atuais e plano

**Problemas observados no PDF atual (print gerado):**
1. Layout **diferente da web** e do romaneio de referência (Image 1).
2. KPI cards **"Valor" e "Pedidos" vazios** (sem barra/subtítulo) → desalinhados.
3. **Metade inferior da página em branco** (conteúdo não preenche o A4).
4. Assinaturas soltas, muito distantes da tabela.
5. Amarelo `#F5C518` em vez do `#ffc400` da marca.
6. Sem bloco lateral de **sequência/orientação** que a web tem.

**Plano (alinhar ao `romaneio.html` de referência):**
- **Hero** escuro compacto com título e status "Carga válida".
- **romhead**: faixa de 5 metadados (Veículo · Eixo · Data · Coordenador · Status).
- **Métricas**: 4 cards com barra de progresso (padronizar Valor/Pedidos com subtítulo "de N candidatos").
- **2 colunas**: tabela (esq.) + **sequência de descarga (stepper)** e **orientação LIFO (soft box)** + notice (dir.).
- **Assinaturas** logo após, com espaçamento correto.
- **Rodapé** fixo com versão/geração.
- Cor `#ffc400`, tipografia e sombras iguais à web → **paridade visual web↔PDF**.
- Garantir bom preenchimento do A4 e quebra de página elegante para cargas grandes.

---

## 9. Por tela (resumo do gap vs referência)

- **Planejamento** (Image 5): + hero, form com combobox e "Configurações avançadas", métricas com barras, aside "Resumo da carga" com **caminhão + rota (stepper) + ações**, bloco de IA. 
- **Romaneio** (Image 1): paridade com a web + export PDF idêntico (ver §8).
- **Simulação** (Image 2): 2 `ScenarioCard` com foto do veículo, badges e **card dourado recomendado**, tabela comparativa com coluna destacada, aside "rota selecionada".
- **Qualidade** (Image 3): KPIs, **pipeline stepper (5)**, **donut de cobertura**, painel "conversão de pisos", tabela de anomalias com badges por ação, top materiais.
- **Triagem** (Image 4): filtros (incluindo **qualidade**), KPIs, **motivos de exclusão com barras**, tabela com badges, **painel de detalhe do pedido** (abre ao clicar; alerta + editar cubagem para 🔴).
- **Importar**: drag-and-drop com área destacada, preview do arquivo, relatório de qualidade em cards.

---

## 10. Qualidade de código / boas práticas React (P1/P2)

- **Code-splitting por rota** (`React.lazy` + `Suspense`) e prefetch de queries no hover da nav.
- **Componentização**: extrair `PageHero`, `Metric`, `SectionCard`, `DataTable`, `RouteStepper`, `Truck`, `StatusBadge` para `components/`.
- **Tipos compartilhados** já ok (`api/types.ts`); adicionar hooks (`useEixos`, `useOtimizar`…) em `hooks/` (Charter previa isso).
- **React Query**: `staleTime` para metadados, `select` para derivar, estados `isPending/isError` padronizados.
- **A11y lint**: `eslint-plugin-jsx-a11y`.
- **Testes de UI**: Vitest + Testing Library para componentes-chave.
- **Performance**: memoizar tabelas grandes, `content-visibility` em listas longas.

---

## Ordem de execução sugerida
1. **P0 base** (§1 tokens + shadcn/ui + §2 layout/hero + §3 Card/Metric/Table/Form) — muda a cara de todas as telas.
2. **PDF** (§8) — paridade web↔PDF.
3. **Telas** uma a uma (§9), com componentes ricos (§3) e micro-animações (§4).
4. **A11y + responsividade** transversais (§5/§6) validadas por tela.
5. **Estados/feedback** (§7) e **boas práticas** (§10).

## Ver também
[[inspiracao/NobreLOG_HTML_CSS]] · [[frontend/design_system]] · [[frontend/telas]] · [[prd/08-frontend]] · [[prd/06-romaneio]]
