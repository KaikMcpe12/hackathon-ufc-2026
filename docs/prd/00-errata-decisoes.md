# PRD-00 — Errata & Decisões Pendentes

> **Status:** proposto (aguardando validação do dono do produto).
> Este PRD é o **de-para** que resolve as inconsistências e lacunas encontradas na documentação antes de começar a implementar. Todos os demais PRDs (01–09) dependem das decisões aqui.
> Cada item traz: **Problema → Decisão proposta → Impacto**. Onde marcado ⚠️, é uma decisão que precisa do seu "ok" ou correção.

## Como ler

- **B#** = bloqueadores. **I#** = inconsistências de contrato. **L#** = lacunas técnicas. **E#** = lacunas de escopo (frontend/produto).
- Decisões que criam arquitetura nova viram ADR: [[arquitetura/adr/0008_desempate_valor]], [[arquitetura/adr/0009_deploy_stateful]], [[arquitetura/adr/0010_persistencia_opcional]].
- Regras invioláveis do [[AGENT_CHARTER]] têm precedência sobre qualquer decisão aqui.

---

## B — Bloqueadores

### B1 — Sem dados nem código no repositório
**Problema:** o repo só tem `docs/`. Não existe `backend/`, `frontend/`, nem os CSVs. Os números "do protótipo validado" (688→93→46→81; caso Eixo 4 + ACELLO 815) não são reproduzíveis, e o gate `test_caso_oficial_eixo4_acello()` não roda.

**Decisão (validada):** modelo **Seed + Upload**.
- Os 6 CSVs reais são versionados em `backend/data/` e carregados no boot (`state.bootstrap`). O caso oficial roda no boot/teste.
- O usuário pode **subir CSVs em runtime** por `POST /etl/ingest` (sobrepõe o estado em memória, não grava em disco). Ver [[arquitetura/adr/0002_upload_ingestao]].

**Impacto:** PRD-01 (seed + boot), PRD-09 (upload + gate).

### B2 — `eixos.csv` não existe como insumo
**Problema:** [[dominio/pipeline_etl]] e [[arquitetura/backend]] citam `eixos.csv`, mas [[dados/dicionario]] só descreve o CSV **ROTAS E COLETAS** (semi-estruturado), do qual os eixos são **derivados**.

**Decisão:** não existe arquivo `eixos.csv` de entrada. `state.eixos` é **derivado** do bloco "Rotas" de `DADOS_DE_ENTREGAS__xlsx_-_ROTAS_E_COLETAS.csv`. Onde a documentação disser "cruzar com `eixos.csv`", leia-se "cruzar com `state.eixos` (derivado de rotas)".

**Impacto:** PRD-01 (parser de rotas → `state.eixos`), PRD-02 (filtro "sem eixo").

---

## I — Inconsistências de contrato

### I1 — Nome canônico do veículo ⚠️
**Problema:** aparece `"HR / BONGO"` (PRD, contratos, `/otimizar/comparar`) e `"HR/BONGO"` (comentário em [[arquitetura/backend]]). É chave de match exato em `/otimizar`.

**Decisão proposta:** forma canônica **`"HR / BONGO"`** (com espaços), como em [[api/contratos]] e [[api/endpoints]]. O ETL normaliza o valor lido do CSV de rotas para essa forma. IDs internos usam slug (`hr_bongo`, `acello_815`, `motos`) para lookup, mas o campo `nome` exposto na API é o canônico.

**Impacto:** PRD-01 (`state.veiculos.nome`), PRD-05 (validação de `/otimizar`).

### I2 — Formato de data no log de correção
**Problema:** [[dominio/pipeline_etl]] mostra `valor_novo: "26/08/2026"` (dd/mm/yyyy); [[api/contratos]] mostra `"2026-08-26"` (ISO).

**Decisão:** **ISO 8601** (`YYYY-MM-DD`) em todo JSON de API, incluindo `Correcao.valor_novo`. `valor_original` mantém o texto **cru** como veio do CSV (ex.: `"26/08/2014"`), pois é auditoria do dado original.

**Impacto:** PRD-02 (`etl/correcoes.py`, modelo `Correcao`).

### I3 — `MOTOS` é selecionável no otimizador? ⚠️
**Problema:** o PRD diz que a moto "atende só Crateús urbano — fora do escopo", mas `MOTOS` aparece na frota, em `state.veiculos` e em `GET /veiculos`. Como Crateús é sempre filtrado no ETL, um otimizador de `MOTOS` não teria pedidos.

**Decisão proposta:** `MOTOS` **aparece** em `GET /veiculos` (transparência da frota) mas é **marcado `selecionavel: false`** e **bloqueado** em `/otimizar` e `/otimizar/comparar` (retorna 400 com motivo "veículo fora do escopo do MVP"). Adicionar campo `selecionavel: bool` ao schema `Veiculo`.

**Impacto:** PRD-01 (`Veiculo.selecionavel`), PRD-05 (validação), PRD-08 (dropdown desabilita MOTOS).

### I4 — `volume_m3`/`peso_kg` nullable coerente
**Problema:** `Pedido.volume_m3` aparece como número obrigatório, mas em `PlanoDeCarga.pedidos_rejeitados[]` aparece `null` (pedido 🔴).

**Decisão:** `peso_kg` e `volume_m3` são **`float | null`** em `Pedido`, `pedidos_rejeitados[]` e `pedidos_selecionados[]`. `null` (⇔ `NaN` interno) representa cubagem ausente (🔴). Regra do Charter mantida: **ausência nunca vira zero**. No frontend, tipo `number | null` e render "—" quando `null`.

**Impacto:** PRD-03 (NaN), PRD-05 (Pydantic `Optional[float]`), PRD-08 (types.ts).

### I5 — Semântica de `incluir_estimadas`
**Problema:** ambíguo se `incluir_estimadas=false` remove 🟡 (ESTIMADA) ou também mexe em 🔴.

**Decisão:** o flag controla **apenas os 🟡**.
- 🔴 (AUSENTE) **sempre** fora do solver (Charter §3.2), independente do flag.
- `incluir_estimadas=true` (default): pool do solver = 🟢 + 🟡.
- `incluir_estimadas=false`: pool = só 🟢.
- **Atenção ao caso oficial:** os 7 pedidos do Eixo 4 podem depender de estimativas sintéticas (🟡). O gate roda com `incluir_estimadas=true`. Ver [[entrega/criterios_aceite]] item 3.

**Impacto:** PRD-04 (montagem do pool), PRD-05 (contrato), PRD-09 (gate).

### I6 — Enum canônico de `motivo_exclusao` ⚠️
**Problema:** strings livres espalhadas ("Retirada no balcão", "Crateús", "Cancelado", "Cubagem ausente", "Data inconsistente", "Cidade não mapeada em eixo").

**Decisão proposta:** enum canônico único, usado por ETL, `GET /qualidade/motivos-exclusao` e badges do frontend:

| Código interno            | Rótulo exibido            | Origem                                  |
|---------------------------|---------------------------|-----------------------------------------|
| `CANCELADO`               | Cancelado                 | filtro elegibilidade                    |
| `RETIRADA_BALCAO`         | Retirada no balcão        | filtro elegibilidade                    |
| `CRATEUS`                 | Crateús                   | filtro elegibilidade                    |
| `CIDADE_FORA_EIXO`        | Cidade fora dos eixos     | filtro elegibilidade                    |
| `CUBAGEM_AUSENTE`         | Cubagem ausente           | classificação 🔴 (não é exclusão de elegibilidade; é barra do solver) |
| `DATA_INCONSISTENTE`      | Data inconsistente        | correção/fila de exceção                |

Nota: **"Cubagem ausente" (🔴) não é o mesmo que "inelegível"** — o pedido é elegível mas fica na fila de revisão. A UI distingue "excluído da base" de "elegível mas barrado".

**Impacto:** PRD-02 (filtros), PRD-03 (🔴), PRD-05 (`/qualidade/motivos-exclusao`), PRD-08 (badges).

### I7 — Números do `/qualidade/resumo` — CORRIGIDO com dados reais ✅
**Problema original:** o exemplo em [[api/endpoints]] traz `46/12/6` (soma 64) que não fecha.

**Achado empírico (implementação validada contra os CSVs reais + protótipo etapa4b):** o pipeline verdadeiro é **688 → 93 (pós-situação) → 81 (pós-eixo)**, exatamente o `688 → 93 → 81` do pitch. Detalhamento:
- 688 registros − 0 cancelados − 184 retiradas − 411 Crateús = **93** (checkpoint "pós-situação").
- 93 − **12 cidade-fora-eixo** (IBIAPABA, SÃO GONÇALO, VILA GRAÇA, etc. — genuinamente fora dos 5 eixos) = **81** (pool do solver).
- **Os "12" NÃO são 🔴 cubagem-ausente** (como eu supus antes) — são cidade-fora-eixo.
- Selos entre os 81: **🟢 39 / 🟡 42 / 🔴 0** (bate 100% com `Status_Cubagem_Prototipo`). No seed, a fila de revisão 🔴 fica **vazia** (os sintéticos cobrem tudo).
- **Meus 81 pedidos elegíveis são idênticos (conjunto) aos 81 do protótipo.**

**Decisão:** `/qualidade/resumo` reporta números de runtime; contrato garante `completa+estimada+ausente == elegiveis (81)`. Valores de referência: **39 / 42 / 0**. A definição de selo é **referência-real vs sintético** (não o flag `Dado_Estimado` do ranking): 🟢 = todos os itens no Ranking Top 85; 🟡 = algum item sintético; 🔴 = algum item sem cubagem.

**Impacto:** já implementado em `etl/filters.py` (checkpoints) e `cubagem/*`; PRD-02/03/05 alinhados.

### I9 — Semana filtra o pool do solver? CONFLITO com o gate ⚠️
**Problema (achado na implementação):** o caso oficial "Eixo 4 + ACELLO 815 + **Semana 4**" só reproduz os 4.797,335 kg se o solver usar **todos os 27 pedidos do Eixo 4 (todas as semanas 1–4)**. Os 7 pedidos vencedores vêm das semanas **2, 3 e 4** — não só da 4. O protótipo (etapa5 cenarios) otimizou por eixo ignorando a semana. Isso **conflita** com [[arquitetura/adr/0006_semana_dropdown]] (que trata semana como o lote a otimizar).

**Decisão proposta:** `semana` é filtro **opcional**. `semana=None` (default do solver e do gate) = todos os pedidos do eixo (comportamento do protótipo, reproduz o gate). Passar uma semana específica restringe o pool àquela semana (feature de UI). O `GET /semanas` continua com `padrao=4` para o dropdown, mas a otimização "oficial" roda com todas. **Precisa do seu ok** — alternativa: honrar o ADR 0006 (semana filtra) e aceitar que o gate seja "todas as semanas do eixo", ajustando o rótulo do caso oficial.

**Impacto:** `optim/planejador.py` (implementado com `semana` opcional), PRD-04/05, revisão do ADR 0006.

### I8 — Totais de `/qualidade/motivos-exclusao` são ilustrativos
**Problema:** o exemplo soma 47 exclusões (18+11+8+7+3), mas 688−93 = **595** registros foram excluídos. Os percentuais também são "% do subconjunto", não de 688.

**Decisão:** `total` = contagem real por motivo (deve somar os excluídos reais, na ordem 688→93); `percentual` = sobre o total de **excluídos**. O exemplo do doc é ilustrativo. Um pedido pode casar com mais de um motivo → contabiliza-se pelo **primeiro** motivo na ordem canônica (cancelado → retirada → Crateús → sem eixo), coerente com a ordem de filtros de [[dominio/pipeline_etl]].

**Impacto:** PRD-02 (contagem por motivo na ordem), PRD-05 (contrato).

---

## L — Lacunas técnicas

### L1 — Desempate por valor (ε) não definido nem implementado ⚠️ → ADR-0008
**Problema:** a função objetivo é `0,5·Op + 0,5·Ov`; o "valor como critério secundário" está no texto mas **não** no código PuLP. Sem isso, o CBC pode devolver qualquer ótimo empatado — o que **quebra o determinismo do caso oficial**.

**Decisão proposta (ADR-0008):** objetivo com **terceiro termo de desempate lexicográfico-aproximado**:

```
maximizar  0,5·Op + 0,5·Ov + ε · (valor_total / valor_ref)
```

- `valor_ref` = soma do valor de todos os pedidos elegíveis do cenário (normaliza o termo p/ [0,1]).
- `ε = 1e-4` (pequeno o suficiente para nunca superar 1 ponto de ocupação, grande o suficiente para desempatar de forma estável).
- Alternativa considerada: solve lexicográfico em 2 passes (fixa ocupação ótima, re-otimiza valor). Mais correto, mais lento. Fica registrada no ADR como plano B se ε causar instabilidade numérica.

**Impacto:** PRD-04 (`optim/modelo.py`), gate do caso oficial.

### L2 — Parse de `m2_por_caixa`
**Problema:** [[dominio/cubagem]] diz que `m2_por_caixa` vem "implícito na `unidade_venda`" (ex.: `"Caixa 2,30 m²"`) mas não dá o parser.

**Decisão:** extrair de `Ranking.Unidade_Venda` por regex tolerante:
```python
UNIDADE_M2_RE = re.compile(r"(?P<n>[\d]+[.,]?[\d]*)\s*m²", re.IGNORECASE)
# "Caixa 2,30 m²" -> 2.30 ; se não casar, m2_por_caixa = None (produto não é vendido por m²)
```
Produtos sem `m²` na `unidade_venda` são tratados por unidade direta (`peso_kg`, `volume_m3` do Ranking × quantidade), sem conversão de caixas.

**Impacto:** PRD-03 (`cubagem/conversor.py`).

### L3 — O que `Item.unidade_venda` guarda
**Problema:** o parse do `Itens_Resumo` extrai `un` do pedido (`UN`, `MT`); o Ranking traz `"Caixa 2,30 m²"`. Qual vai para `Item.unidade_venda`?

**Decisão:** `Item.unidade_venda` guarda a **unidade comercial do pedido** (`UN`, `MT`, …), que é o que o operador vê. A unidade do Ranking é insumo de cálculo (`m2_por_caixa`, `peso_por_caixa`) e **não** é exposta em `Item`. `Item.caixas` é preenchido só quando houve conversão m²→caixas (senão `null`).

**Impacto:** PRD-03 (montagem de `Item`), PRD-05 (schema `Item`).

### L4 — Determinismo x "seed"
**Problema:** o teste `test_determinismo_com_seed()` cita seed, mas o CBC do PuLP é determinístico por **ordenação estável + `timeLimit` fixo**, não por seed.

**Decisão:** manter as 3 regras de [[dominio/otimizacao]] (ordenar por `pedido_id`, `timeLimit=30`, nunca depender de ordem de dict). O teste é renomeado para `test_determinismo_reexecucao()` (roda o solver N vezes e compara a saída idêntica). Se a versão do CBC expuser `randomSeed`/`randomCbcSeed`, fixá-lo como reforço — mas o determinismo **não depende** disso.

**Impacto:** PRD-04 (solver), PRD-09 (teste renomeado).

### L5 — Provedor, timeout e fallback do LLM
**Problema:** `/insight` não define timeout; provedor "a definir" mas [[api/contratos]] exemplifica `"anthropic:claude-sonnet-5"`.

**Decisão proposta:**
- Provedor default: **Anthropic Claude** (modelo configurável via env `LLM_MODEL`, default `claude-haiku-4-5` — rápido/barato para 1–2 parágrafos; usar Sonnet se houver orçamento). Interface abstrata `src/llm/client.py` permite trocar (ver [[arquitetura/adr/0007_motor_hibrido_llm]]).
- `LLM_TIMEOUT_S = 8` (dentro do aceitável para bloco opcional).
- Sem chave (`ANTHROPIC_API_KEY` ausente) → `/insight` retorna **503** e o front colapsa o bloco silenciosamente. Nunca quebra o fluxo principal.
- Zero Data Retention configurado no cliente.
- O `modelo` retornado reflete o env real (não hardcode).

**Impacto:** PRD-07 (`llm/client.py`, `/insight`).

---

## E — Lacunas de escopo (frontend/produto)

### E1 — `/insight` sem tela que o consuma
**Problema:** LLM está no domínio e em ADR 0007, mas nenhuma das 5 telas o exibe.

**Decisão:** bloco **"Insight de IA"** recolhível na tela **Planejamento** (abaixo dos KPIs) e replicado no **Romaneio**. Chama `POST /insight` com o `PlanoDeCarga` após a otimização. Estados: carregando (skeleton) · sucesso (1–2 parágrafos) · indisponível (503 → "Insight de IA não disponível no momento.", recolhido). Ver [[dominio/llm_insights]].

**Impacto:** PRD-07, PRD-08.

### E2 — Upload (`/etl/ingest`) agora é fluxo primário do usuário
**Problema:** upload existia só na API; nenhuma tela o expunha. Com a decisão **Seed + Upload**, o upload passa a ser um fluxo de primeira classe.

**Decisão:** criar tela/rota **`/importar`** (ou modal acessível do Header) com drag-drop dos 6 CSVs (nomes livres, mapeados por campo: semana_1..4, ranking, rotas), botão "Processar", e **relatório de qualidade** pós-ingestão (reusa `QualidadeResumo`). Seed permanece como fallback quando nada foi enviado. Sem auth no MVP (ADR 0002).

**Impacto:** PRD-08 (tela importar), PRD-09 (`/etl/ingest`).

### E3 — Reclassificar "Dashboard de qualidade" para Obrigatório
**Problema:** [[produto/requisitos]] marca o dashboard de qualidade (RF ~26) como *Diferencial*, mas existe tela `/qualidade` + endpoints `/qualidade/*` no MVP.

**Decisão:** reclassificar para **Obrigatório**. A tela `/qualidade` e os endpoints `/qualidade/{resumo,log,motivos-exclusao}` são MVP. (Correção registrada aqui; o doc de origem é atualizado só na fase de propagação, se você aprovar.)

**Impacto:** PRD-05, PRD-08.

### E4 — Filtro `qualidade` ausente na UI de Triagem
**Problema:** `GET /pedidos` aceita `qualidade` (COMPLETA/ESTIMADA/AUSENTE), mas a tela `/triagem` só lista Período/Eixo/Cidade/Status/Busca.

**Decisão:** adicionar o filtro **"Qualidade da cubagem"** (🟢/🟡/🔴) ao painel de filtros da Triagem, mapeado para o query param `qualidade`.

**Impacto:** PRD-08.

### E5 — Mapa `Correcao` → badges de "Anomalias" (tela Qualidade)
**Problema:** os campos de `Correcao` (`regra`, `criterio`) não mapeiam direto para os badges (Corrigida/Sinalizada/Estimado/Padronizada/Enriquecida).

**Decisão:** adicionar ao modelo `Correcao` um campo `acao` (enum): `CORRIGIDA` | `SINALIZADA` | `ESTIMADO` | `PADRONIZADA`. O painel "Anomalias detectadas" agrupa por `acao`. Tabela de mapeamento `regra → acao` fica no PRD-02 (ex.: `ano_fora_do_lote → CORRIGIDA`, `cidade_trailing_space → PADRONIZADA`, `sintetico:* → ESTIMADO`, `campo_obrigatorio_ausente → SINALIZADA`). Remover "Enriquecida" (viola o Charter §3.5 — proibido enriquecer com fonte externa).

**Impacto:** PRD-02 (`Correcao.acao`), PRD-05, PRD-08.

### E6 — `recomendado` de `/otimizar/comparar`: backend
**Problema:** docs dizem que o `recomendado` é calculado tanto no backend (retorna no response) quanto no frontend.

**Decisão:** **backend calcula e retorna** `recomendado` (nome do veículo com maior `0,5·Op+0,5·Ov` sem violações; empate → maior valor). O frontend **apenas exibe** — não recalcula. Remove a duplicação.

**Impacto:** PRD-05 (`/otimizar/comparar`), PRD-08 (Simulação).

---

## Resumo das decisões que precisam do seu "ok" (⚠️)

| Item | Decisão proposta | Alternativa |
|------|------------------|-------------|
| I1 | Veículo canônico `"HR / BONGO"` (com espaços) | `"HR/BONGO"` |
| I3 | `MOTOS` visível mas não selecionável (bloqueia `/otimizar`) | Remover MOTOS da frota exposta |
| I6 | Enum canônico de motivos (tabela) | Outra taxonomia |
| I7 | 🟢46/🟡35/🔴12 (soma 93); exemplos dos docs = ilustrativos | Recontar após dados reais |
| L1 | ε=1e-4 no objetivo (ADR-0008) | Solve lexicográfico 2-pass |
| L5 | Anthropic default, `claude-haiku-4-5`, timeout 8s | Outro provedor/modelo |

Os demais itens (B1–B2, I2, I4, I5, I8, L2–L4, E1–E6) seguem as convenções já estabelecidas no Charter/docs e são de baixo risco — implemento como descrito, salvo objeção.

## Ver também
- [[AGENT_CHARTER]] — regras invioláveis
- [[arquitetura/adr/0008_desempate_valor]], [[arquitetura/adr/0009_deploy_stateful]], [[arquitetura/adr/0010_persistencia_opcional]]
- [[entrega/criterios_aceite]] — o gate que valida essas decisões
