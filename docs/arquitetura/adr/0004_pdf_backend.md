# ADR 0004 — Geração do PDF no backend com WeasyPrint

**Status:** Aceita
**Data:** 2026-09-16

## Contexto

O romaneio é o artefato operacional entregue à expedição. Precisa ser um PDF impressão-ready, assinável. Onde renderizar?

## Decisão

Backend gera o PDF com **WeasyPrint** a partir de um template HTML/CSS (Jinja2).

## Justificativa

- **Fonte única de verdade:** dados do plano de carga vêm do solver (Python). Manter a renderização no mesmo processo evita duplicação de tipos/formatos.
- **Layout complexo:** o romaneio (Image 1) tem cabeçalho corporativo, tabelas, barras de ocupação, área de assinatura. HTML+CSS é ergonômico para isso.
- **Reproduzibilidade:** mesma execução → mesmo PDF (determinismo).
- **URL única:** frontend faz `POST /romaneio/generate`, recebe um URL/blob e exibe/imprime.

## Alternativas descartadas

- **`react-pdf` no frontend:** duplica lógica de formatação, e o PDF final divergiria do que o coordenador vê na tela caso o backend evolua sozinho.
- **`ReportLab`:** mais poderoso mas API imperativa; layout complexo custa caro.

## Consequências

**Positivas:**
- Template versionado como HTML — fácil ajustar identidade visual.
- Fonte customizada, cores da marca e logotipo funcionam.

**Negativas:**
- WeasyPrint tem dependências nativas (Cairo, Pango) — deploy exige ambiente compatível. Aceito.

## Ver também

- [[dominio/romaneio]]
- [[api/endpoints]]#romaneio_generate
