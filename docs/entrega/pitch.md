# Pitch — Roteiro de 7 minutos

Limite: 7 min. Meta interna: **terminar em 6:20** para folga.

## 0:00 — 0:40 · Problema

**Objetivo:** trazer a banca para a dor real.

**Fala-âncora:**
> "No Grupo Nobre Lar, 40 a 60 minutos por dia são gastos por um coordenador de logística montando cargas no olho e no caderno. O resultado é imprevisível: caminhão que sai com espaço sobrando, pedido que fica para depois sem critério, e nenhuma medida de ocupação."

**Visual:** foto/mockup do processo manual (opcional).

## 0:40 — 1:20 · Solução

**Objetivo:** apresentar o produto em uma frase.

**Fala-âncora:**
> "O NobreLOG Optimizer transforma pedidos e restrições físicas em um plano de carga executável, explicável e otimizado. O coordenador escolhe eixo e veículo; o sistema faz o resto."

**Visual:** logo + slogan "Do pedido ao caminhão em poucos segundos."

## 1:20 — 3:30 · Demonstração ao vivo

**Objetivo:** momento UAU.

**Roteiro:**

1. Abrir tela `/` (Planejamento).
2. Selecionar **Eixo 4 · Ipaporanga → Poranga → Ararendá**.
3. Selecionar **Veículo ACELLO 815**.
4. Semana 4 (default).
5. Clicar **"Otimizar carga"**.
6. Apontar KPIs:
   - Peso: **99,94%**
   - Volume: **99,50%**
   - Gargalo: **PESO**
   - Violações: **0**
   - 7 pedidos selecionados de 93 disponíveis
   - R$ 16.770,85
7. Ir para `/qualidade` — mostrar rapidamente: "esses números vieram de um pipeline rastreável, 688 → 93 pedidos, com correções logadas."
8. Voltar e clicar **"Gerar plano de carga"** → mostrar PDF do romaneio.

**Fala-âncora ao ver o resultado:**
> "Em menos de dois segundos, o sistema achou uma combinação que aproveita 99,94% do peso e 99,5% do volume do caminhão, sem violar limite algum, e transformou isso em um plano de carga que a expedição pode assinar hoje."

## 3:30 — 4:30 · Diferencial

**Objetivo:** mostrar por que não é só "algoritmo + tela".

**Blocos:**

1. **Explicabilidade** — abrir a tabela de rejeitados: "esse pedido excederia o peso em 320 kg; esse outro tem cubagem incompleta e está aguardando revisão." Ir para `/triagem` e mostrar a fila de revisão.
2. **Diagnóstico peso × volume** — "identificamos que esse eixo é limitado por peso, não por volume. O coordenador pode compor cargas futuras com mais itens leves."
3. **Comparação de veículos** — `/simulacao` lado a lado (HR/BONGO vs ACELLO 815) — mostrar como o gargalo muda.

**Fala-âncora:**
> "Não construímos uma caixa-preta. Cada decisão é rastreável, e cada rejeição tem motivo. Isso transforma um algoritmo matemático em uma ferramenta que o coordenador confia."

## 4:30 — 5:20 · Tecnologia

**Objetivo:** provar que é sólido.

**Slides ou fala:**

- Backend: FastAPI + Pandas + PuLP/CBC
- Solver MILP com hard constraints — **zero violações é matematicamente garantido**
- ETL rastreável: nenhuma correção é silenciosa
- Frontend: React + TypeScript
- Motor híbrido: solver determinístico + camada LLM opcional para insights
- **Regra de ouro:** peso ou volume ausente **nunca** vira zero. Ele barra o pedido — segurança primeiro.

## 5:20 — 6:00 · Impacto e escalabilidade

**Fala-âncora:**
> "Isso substitui 40–60 minutos diários de um coordenador por menos de 5 minutos. Escala imediatamente para os 5 eixos e os 4 caminhões da Nobre Lar. E como toda regra de negócio vive em módulos separados, adicionar novos veículos ou eixos é subir um CSV — não escrever código."

## 6:00 — 6:20 · Fechamento

**Fala-âncora:**
> "O Grupo Nobre Lar tem 38 anos entregando materiais de construção no Sertão Central e Inhamuns. O NobreLOG Optimizer é a ferramenta que um coordenador pode abrir amanhã: recebe pedidos, respeita restrições físicas, explica cada decisão e entrega um plano de carga pronto para expedição."

**Encerrar com:** logo + slogan.

## Checklist de ensaio

- [ ] Demo funciona offline (não depende de internet ao vivo).
- [ ] Caso oficial (Eixo 4 + ACELLO 815) reproduz os números do pitch.
- [ ] Backup do PDF do romaneio pronto para exibir se algo travar.
- [ ] Cronometrar 3× — meta 6:20.
- [ ] Slide de fechamento pronto para congelar tela.

## Ver também

- [[entrega/criterios_aceite]]#caso_oficial
- [[frontend/telas]]
