# Preparação para a banca — FAQ e pontos em aberto

> Complemento do [[entrega/pitch]]. Respostas curtas para as perguntas prováveis + limitações assumidas.

## 1. Como explicar o modelo (30s)

**Otimização:** *Knapsack 2D* (mochila com peso **e** volume) resolvido por **MILP** (PuLP/CBC).
- Variável: `x_i ∈ {0,1}` — o pedido i entra na carga ou não (pedido é atômico, não se divide).
- Restrições rígidas: `Σ peso_i·x_i ≤ cap_peso` e `Σ vol_i·x_i ≤ cap_vol` → **nunca** viola.
- Objetivo: `0,5·ocup_peso + 0,5·ocup_volume + ε·valor` → melhor proporção peso×volume; valor só desempata.

**Cubagem/classificação:** cada item cruza com o Ranking Top 85 (peso/volume) ou uma estimativa sintética; o pedido recebe o **pior selo** dos seus itens: 🟢 todos oficiais · 🟡 algum estimado · 🔴 algum sem dado. Ausência **nunca vira zero**.

**Organização física:** zonas do caminhão **fundo→porta** pela rota (LIFO) + itens ordenados por densidade (densos na base).

## 2. Perguntas prováveis da banca

| Pergunta | Resposta curta |
|---|---|
| Como garante zero violações? | Peso/volume são **restrições rígidas** do MILP — soluções que estouram são matematicamente inviáveis. |
| Por que 0,5 / 0,5? | Otimizar só valor repete o "no olho"; só peso ignora volume. 50/50 empurra a usar as duas capacidades. Configurável. |
| E se um item não tem cubagem? | Vira 🔴, **não entra** no solver e cai na **fila de revisão** (o coordenador informa as dimensões — UC07). Nunca assume peso 0. |
| Os dados sintéticos não enganam? | São **marcados 🟡** e nunca apresentados como oficiais; o coordenador pode revisar. Em produção, viram fichas reais. |
| Por que "todas as semanas" e não só a 4? | O caso oficial otimiza todos os pedidos em aberto do eixo. `semana` é filtro opcional (ADR 0006 em revisão). |
| É determinístico? | Sim — mesma entrada → mesma saída (ordenação estável + `timeLimit` fixo + ε de desempate). |
| Escala para 4 caminhões × 5 eixos? | Hoje é 1 eixo/veículo por execução (MVP). Multi-eixo (MKP) está desenhado no [[prd/10-pos-mvp-melhorias]]. |
| Rastreabilidade dos dados? | Toda correção do ETL vira log clicável em **Dados & cubagem** (o quê, por quê, o que foi feito). |
| Como valida que está certo? | Gate automático: Eixo 4 + ACELLO reproduz **7 pedidos / 4.797,335 kg / 99,94% / 0 violações / R$ 16.770,85**. 36 testes. |

## 3. Números-âncora para a demo

- Pipeline: **688 → 93 → 81**; selos **🟢39 / 🟡42 / 🔴0**.
- Caso oficial: 7 pedidos · 99,94% peso · 99,50% volume · gargalo PESO · 0 violações · R$ 16.770,85.
- Tempo de resposta `/otimizar` < 3s; montagem manual 40–60 min → segundos.

## 4. Pontos em aberto / limitações (assumidas)

- **Multi-eixo** e **integração do CSV de Vendas_Faturamento** ficam para o pós-MVP ([[prd/10-pos-mvp-melhorias]]).
- **Persistência:** estado é in-memory; uploads são efêmeros (reinício volta ao seed). Banco é opcional ([[arquitetura/adr/0010_persistencia_opcional]]).
- **Frete mínimo:** não documentado pela empresa → implementado como **alerta de ocupação mínima** configurável (não bloqueia).
- **LLM (/insight):** opcional; sem chave, recolhe silenciosamente. Suporta Anthropic e NVIDIA NIM.
- Fila de revisão 🔴 está **vazia no seed** (os sintéticos cobrem tudo) — a UI do UC07 existe para dados reais sem cobertura.

## Ver também
[[entrega/pitch]] · [[entrega/criterios_aceite]] · [[dominio/otimizacao]] · [[dominio/cubagem]]
