# Telas

O produto tem **5 telas** mapeadas a partir dos mockups.

## Planejamento — `/` <a id="planejamento"></a>

**Fonte:** mockup Image 5.
**Objetivo:** tela principal. Coordenador configura carga, clica "Otimizar" e vê o resultado.

### Blocos

1. **Header hero** — "Planejamento inteligente de cargas" com subtítulo.
2. **Painel "Configurar carga"** — 3 selects (Eixo, Veículo, Data da carga) + botão principal `[Otimizar carga]` (amarelo, ícone barras).
3. **Link "Configurações avançadas"** — abre modal com toggle `incluir_estimadas` e outros parâmetros.
4. **4 KPI cards** (após otimização):
   - Peso utilizado `X / Y kg` + barra + %
   - Volume utilizado `X / Y m³` + barra + %
   - Valor da carga `R$ X`
   - Pedidos selecionados `N de M disponíveis`
5. **Painel lateral "Resumo da carga"** (direita):
   - Cards de Fator limitante (badge PESO/VOLUME) e Violações (0)
   - Imagem do veículo + capacidades
   - Rota de descarga (numerada)
   - Botões `[Gerar plano de carga]` (preto) e `[Imprimir]`
6. **Tabela "Pedidos selecionados"** — colunas Nº, Cidade, Valor, Peso, Volume + linha Total.

### Dados

- `GET /eixos`, `GET /veiculos`, `GET /semanas` no mount.
- `POST /otimizar` no clique do botão.
- Resultado alimenta os KPIs, o painel lateral e a tabela.

### Interações

- Botão "Otimizar carga" fica desabilitado até selecionar Eixo, Veículo e Data.
- Após otimização, o botão "Gerar plano de carga" ativa e leva para `/romaneio` com o resultado no state.

## Romaneio — `/romaneio` <a id="romaneio"></a>

**Fonte:** mockup Image 1.
**Objetivo:** apresentar plano de carga preview + ações (imprimir, exportar PDF, compartilhar).

### Blocos

1. **Header hero** — "Plano de carga / Romaneio" com imagem do galpão.
2. **5 metadata cards** — Veículo, Eixo (com setas cidade → cidade), Data, Coordenador, Status ("Carga válida").
3. **4 KPI cards** — Peso, Volume, Valor, Pedidos.
4. **Painel lateral direito:**
   - "Sequência de descarga" numerada
   - Alerta amarelo quando uma cidade da rota não tem pedido ("Não há pedidos para Poranga. Manter a rota para atendimento comercial da região.")
   - "Orientação de carregamento" (LIFO) com ícone e texto explicativo
   - Alerta "Confira os volumes e identifique cada pedido"
5. **Tabela "Pedidos da carga"** — colunas Ordem, Pedido, Cidade, Valor, Peso, Volume, Observação + total.
6. **Rodapé com 3 campos de assinatura** — Conferente, Motorista, Expedição.
7. **Botões:** `[Imprimir]`, `[Exportar PDF]`, `[Compartilhar]` (preto).

### Dados

- Recebe `PlanoDeCarga` via router state (vindo de `/`).
- Se acessada diretamente sem state, oferece dropdown para escolher plano da sessão atual.
- `POST /romaneio/generate` no clique do "Exportar PDF".

## Simulação — `/simulacao` <a id="simulacao"></a>

**Fonte:** mockup Image 2.
**Objetivo:** comparar 2 veículos lado a lado para o mesmo eixo.

### Blocos

1. **Header hero** — "Simulação e comparação de cenários".
2. **Painel "Parâmetros da simulação":**
   - Select Data da carga
   - Select Eixo
   - Toggle "Comparar veículos" (default ligado)
3. **Duas colunas de cenário** (Cenário 1 e Cenário 2):
   - Ícone + nome do veículo + descrição curta
   - Badge no topo direito ("Limite de peso", "Melhor equilíbrio operacional", "Limite de volume")
   - Foto do veículo + capacidades
   - KPIs: Peso utilizado, Volume utilizado, Pedidos selecionados, Valor da carga
4. **Painel "Comparativo dos cenários"** (embaixo, largura total):
   - Tabela linha por linha (Pedidos, Peso usado, Volume usado, Gargalo, Valor, Situação)
   - Coluna "melhor equilíbrio" destacada em amarelo
5. **Painel lateral "Rota selecionada"** (direita) — sequência numerada de cidades.
6. **Botões:** `[Nova simulação]`, `[Salvar cenário recomendado]` (amarelo).

### Dados

- `POST /otimizar/comparar` no clique de simulação.
- Frontend calcula "recomendado" com base no maior valor de `0.5·Op + 0.5·Ov` sem violações.

## Qualidade — `/qualidade` <a id="qualidade_dados"></a>

**Fonte:** mockup Image 3.
**Objetivo:** dashboard de qualidade dos dados. Não é obrigatório para operar; é diferencial de pitch.

### Blocos

1. **Header hero** — "Qualidade dos dados e cubagem".
2. **4 KPI cards** — Registros processados, Inconsistências detectadas, Materiais no ranking, Pedidos com cubagem completa (com variação vs. período anterior — quando disponível).
3. **Painel "Pipeline de tratamento"** — 5 estágios em stepper horizontal (Importação → Limpeza → Conversão → Cubagem → Validação), cada um com contagem + %.
4. **Painel lateral "Cobertura da cubagem"** (direita) — donut chart Completa/Parcial/Ausente.
5. **Painel "Conversão de pisos"** — exemplo prático (Área ÷ Área por caixa = Caixas → peso e volume).
6. **Painel "Anomalias detectadas"** — tabela com Tipo, Exemplo, Ação aplicada (badges: Corrigida, Sinalizada, Estimado, Padronizada, Enriquecida).
7. **Painel "Materiais mais recorrentes"** — barras horizontais top 5.

### Dados

- `GET /qualidade/resumo`
- `GET /qualidade/log`

## Triagem — `/triagem` <a id="triagem"></a>

**Fonte:** mockup Image 4.
**Objetivo:** listar pedidos e permitir revisão dos 🔴.

### Blocos

1. **Header hero** — "Pedidos elegíveis e triagem operacional".
2. **Painel "Filtros":** Período, Eixo, Cidade, Status, Busca livre. Link "Limpar filtros".
3. **4 KPI cards** — Pedidos totais, Elegíveis, Cubagem completa, Com pendências (com barrinhas de %).
4. **Painel "Motivos de exclusão"** (direita) — lista rankeada com contagem e % (Retirada, Crateús, Cancelado, Cubagem ausente, Data inconsistente).
5. **Tabela "Lista de pedidos"** — Pedido, Cidade, Situação, Status logístico, Valor, Peso, Volume, Elegibilidade (badges: Elegível, Cubagem incompleta, Retirada, Cancelado).
6. **Painel lateral "Detalhe do pedido"** (direita, embaixo dos motivos) — abre ao clicar em uma linha. Se pedido é 🔴, mostra alerta amarelo "Pedido não entrou na otimização: cubagem incompleta. Informe as dimensões dos itens para tornar o pedido elegível." + botão para editar cubagem (UC07).
7. **Botão "Exportar"** no topo direito da tabela.

### Dados

- `GET /pedidos?filtros...`
- `POST /pedidos/{id}/revisar` no formulário de edição.

## Ver também

- [[frontend/design_system]] — tokens, cores, tipografia
- [[arquitetura/frontend]] — estrutura de componentes
