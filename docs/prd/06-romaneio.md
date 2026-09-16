# PRD-06 — Romaneio (PDF)

> **Status:** proposto. Depende de: [[prd/04-otimizacao]], [[prd/05-api]].
> Gera o artefato operacional final: o PDF do plano de carga entregue à expedição.

## Objetivo

Implementar `src/romaneio/` (template HTML/Jinja2 + WeasyPrint) e `POST /romaneio/generate` conforme [[dominio/romaneio]] e [[arquitetura/adr/0004_pdf_backend]].

## Escopo

**Dentro:**
- Cálculo da **sequência de descarga** a partir das cidades ordenadas do eixo — inclui cidades **sem pedido** ("Nenhum pedido") (coerente docs).
- **Orientação de carregamento LIFO** (`descricao` gerada em pt-BR: carregue na ordem inversa da descarga).
- `template.html` (Jinja2): cabeçalho corporativo, metadados (veículo, eixo+cidades, data, coordenador, status), 4 KPIs, tabela de pedidos (ordem = descarga), 3 assinaturas (Conferente, Motorista, Expedição), rodapé com **versão do sistema**.
- `gerador.py`: injeta `PlanoDeCarga` no template, renderiza PDF (WeasyPrint).
- `POST /romaneio/generate` (body `RomaneioGenerateRequest`: `plano, coordenador, data_carga`) → `application/pdf` | **422** se `violacoes>0`.

**Fora:** preview no frontend (PRD-08).

## Contratos
`RomaneioGenerateRequest` (schema explícito — lacuna apontada): `{ plano: PlanoDeCarga, coordenador: str = "—", data_carga: date }`. Erro 422 usa `{code:"PLANO_COM_VIOLACOES", message, details:{violacoes}}`.

## Regras invioláveis (Charter / domínio)
- **Números do PDF = números do solver.** Nunca recalcular no template.
- Se `violacoes > 0`, PDF **não** é gerado → 422.
- Rodapé sempre inclui a versão do sistema (rastreabilidade).
- Ordem da tabela = ordem de descarga; carregamento é o inverso (LIFO).

## Critérios de aceite
- [ ] Caso oficial gera PDF válido (A4) com 7 pedidos e KPIs 99,94% / 99,50%.
- [ ] Cidade do eixo sem pedido aparece como "Nenhum pedido".
- [ ] `violacoes>0` → 422, sem PDF.
- [ ] Rodapé mostra versão; assinaturas presentes.
- [ ] Números do PDF idênticos aos do `PlanoDeCarga` (sem recálculo).

## Testes
`test_romaneio.py`: gera PDF do caso oficial (valida bytes não vazios + header PDF), 422 em violação sintética, sequência inclui cidade vazia, versão no rodapé.

## Riscos
- WeasyPrint/Cairo/Pango no container — validado no Dockerfile do PRD-01.
- Fidelidade visual ao mockup (Image 1) — ajustar CSS do template.

## Ver também
[[dominio/romaneio]] · [[arquitetura/adr/0004_pdf_backend]] · [[frontend/telas]]#romaneio
