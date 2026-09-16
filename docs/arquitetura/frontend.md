# Arquitetura — Frontend

## Estrutura de pastas

```
frontend/
├── index.html
├── vite.config.ts
├── tailwind.config.ts
├── package.json
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── router.tsx                     # rotas das 5 telas
│   ├── api/                           # cliente HTTP
│   │   ├── client.ts                  # fetch wrapper + tipos
│   │   ├── types.ts                   # espelha [[api/contratos]]
│   │   └── endpoints.ts
│   ├── hooks/                         # React Query / SWR
│   │   ├── useEixos.ts
│   │   ├── useVeiculos.ts
│   │   ├── useSemanas.ts
│   │   ├── usePedidos.ts
│   │   ├── useOtimizar.ts
│   │   ├── useQualidade.ts
│   │   └── useRomaneio.ts
│   ├── pages/
│   │   ├── Planejamento.tsx           # tela principal (Image 5)
│   │   ├── Romaneio.tsx               # PDF preview (Image 1)
│   │   ├── Simulacao.tsx              # comparar veículos (Image 2)
│   │   ├── Qualidade.tsx              # dashboard (Image 3)
│   │   └── Triagem.tsx                # elegíveis + revisão 🔴 (Image 4)
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Header.tsx             # NobreLOG + Coordenador
│   │   │   └── Shell.tsx
│   │   ├── cards/
│   │   │   ├── KpiCard.tsx            # peso, volume, valor, pedidos
│   │   │   ├── OcupacaoBar.tsx        # barra amarela com %
│   │   │   └── GargaloBadge.tsx       # PESO / VOLUME
│   │   ├── forms/
│   │   │   ├── SeletorEixo.tsx
│   │   │   ├── SeletorVeiculo.tsx
│   │   │   └── SeletorSemana.tsx      # dropdown, default última
│   │   ├── tabelas/
│   │   │   ├── TabelaPedidos.tsx
│   │   │   ├── TabelaComparativo.tsx
│   │   │   └── TabelaTriagem.tsx
│   │   └── romaneio/
│   │       ├── RotaSequencia.tsx      # ordem de descarga
│   │       └── OrientacaoCarregamento.tsx  # LIFO
│   ├── lib/
│   │   ├── format.ts                  # currency, kg, m³
│   │   └── theme.ts                   # tokens do design system
│   └── styles/
│       └── globals.css
└── public/
    └── logo-nobre-lar.svg
```

## Estado e dados

- **React Query** (recomendado) para cache de GETs e mutations.
- Nenhum estado global do tipo Redux/Zustand para o MVP. Estado local nos componentes de página; parâmetros de otimização compartilhados via URL (searchparams) para permitir compartilhar link.
- Resultado da otimização vive na página `Planejamento`, é passado ao `Romaneio` via router state ou refetch por ID de sessão.

## Camada de API

`src/api/client.ts` exporta um `fetch` tipado:

```ts
type ApiError = { code: string; message: string; details?: unknown };

async function api<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${import.meta.env.VITE_API_URL}${path}`, {
    ...init,
    headers: { "content-type": "application/json", ...init?.headers },
  });
  if (!res.ok) throw (await res.json()) as ApiError;
  return res.json() as Promise<T>;
}
```

Tipos em `src/api/types.ts` são gerados/mantidos em paralelo com [[api/contratos]] (mesmos nomes de campos).

## Roteamento

| Rota           | Página          | Tela mockup |
|----------------|-----------------|-------------|
| `/`            | Planejamento    | Image 5     |
| `/romaneio`    | Romaneio        | Image 1     |
| `/simulacao`   | Simulação       | Image 2     |
| `/qualidade`   | Qualidade       | Image 3     |
| `/triagem`     | Triagem         | Image 4     |

## Ver também

- [[frontend/telas]] — mapa detalhado das 5 telas
- [[frontend/design_system]] — tokens, paleta, tipografia
