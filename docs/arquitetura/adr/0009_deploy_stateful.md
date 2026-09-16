# ADR 0009 — Deploy: backend em host stateful + frontend na Vercel

**Status:** Proposta
**Data:** 2026-09-16

## Contexto

O sistema mantém o estado (CSVs processados) **em memória** (ADR 0001) e permite **upload em runtime** que substitui esse estado (ADR 0002). O fluxo esperado é: o usuário sobe os CSVs uma vez e depois consulta/otimiza em chamadas seguintes reutilizando o estado carregado.

Surgiu a dúvida de deploy: "e se o backend rodasse serverless (ex.: Vercel)?" Isso **não é compatível** com o modelo in-memory:

- **Serverless é stateless e efêmero.** Cada request pode cair em uma instância diferente ou recém-iniciada (cold start). O singleton `AppState` preenchido no upload **não sobrevive** até o request seguinte de `/otimizar`. Funciona no dev local (1 processo), falha em produção serverless.
- **WeasyPrint** (PDF do romaneio, ADR 0004) tem dependências nativas (Cairo/Pango) difíceis de empacotar na runtime Python da Vercel.

## Decisão

- **Backend** roda em **host stateful** — um processo contínuo: Render / Railway / Fly.io / Docker em VPS. A RAM do processo guarda o estado enquanto ele vive; o upload persiste até o próximo restart (volta ao seed de `backend/data/`). WeasyPrint roda no container.
- **Frontend** (estático Vite/React) é publicado na **Vercel** (ou similar), apontando `VITE_API_URL` para o host do backend. CORS liberado para o domínio do front.
- Um único container Docker com Python 3.11 + libs nativas cobre backend + PDF.

## Alternativas consideradas

- **Backend serverless single-request** (ETL+cubagem+solver numa chamada, sem estado): compatível com Vercel, mas reprocessa tudo a cada request e não resolve o PDF (WeasyPrint). Rejeitado para o MVP; pode ser reconsiderado se o volume crescer.
- **Estado no cliente** (browser guarda os CSVs): exigiria portar o solver (PuLP/CBC) e a cubagem para JS/WASM — fora da stack fixa. Rejeitado.
- **KV/Blob de sessão** (Vercel KV/Redis): viabilizaria serverless, mas quebra o "sem banco" do ADR 0001. Tratado como caminho opcional em [[arquitetura/adr/0010_persistencia_opcional]].

## Consequências

**Positivas:**
- Modelo in-memory (ADR 0001/0002) e WeasyPrint (ADR 0004) continuam válidos sem mudança.
- Deploy simples: 1 container backend + front estático.

**Negativas:**
- Requer um host que mantenha processo vivo (custo > free serverless).
- Escala horizontal exige cada instância carregar o seed (sem estado compartilhado) — aceitável no MVP mono-usuário. Para histórico/persistência, ver [[arquitetura/adr/0010_persistencia_opcional]].

## Ver também

- [[arquitetura/adr/0001_sem_banco_de_dados]]
- [[arquitetura/adr/0002_upload_ingestao]]
- [[arquitetura/adr/0004_pdf_backend]]
- [[arquitetura/adr/0010_persistencia_opcional]]
- [[prd/01-fundacao-deploy]]
