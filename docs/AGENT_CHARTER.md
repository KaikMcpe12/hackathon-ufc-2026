# NobreLOG — Charter do Agente

> Este documento é o **system prompt** de qualquer agente de código que trabalhe no projeto.
> É lido antes de qualquer outra coisa. Se algo nas outras páginas conflitar com este charter, este vence.

## 1. Contexto em uma frase

Sistema para o Grupo Nobre Lar (Crateús-CE) que recebe pedidos + veículo + eixo e devolve um **plano de carga** que maximiza a ocupação física do caminhão **sem** violar peso ou volume.

## 2. Stack fixa

- **Backend:** Python 3.11+ · FastAPI · Pandas · PuLP (CBC) · WeasyPrint (PDF)
- **Frontend:** React + TypeScript · Vite · Tailwind
- **Sem banco de dados.** CSVs em `backend/data/` carregados em memória no `startup`. Upload de re-ingestão é permitido via endpoint (não persiste em disco entre reinícios).
- **Sem autenticação** no MVP.

## 3. Regras invioláveis

1. **Nunca** produzir carga com `peso_total > capacidade` ou `volume_total > capacidade`. Zero violações é *hard constraint*.
2. **Nunca** assumir `peso=0` ou `volume=0` para produto sem cubagem. Marcar como `DADO_INCOMPLETO` e barrar da otimização automática.
3. **Nunca** silenciar correção de dado. Toda transformação vai para um log rastreável exposto na API (`GET /qualidade/log`).
4. **Nunca** trocar a função objetivo por "maximizar valor financeiro". Valor é apenas critério secundário de desempate.
5. **Nunca** reidentificar clientes ou enriquecer dados com fontes externas. A base é anonimizada por contrato.
6. **Nunca** adicionar feature fora do escopo do MVP sem ADR aprovada (ver [[arquitetura/adr/0001_sem_banco_de_dados]] e demais).
7. Toda decisão do solver precisa gerar **motivo explicável** para os pedidos rejeitados (excedeu peso / excedeu volume / cubagem incompleta / ocupação global).

## 4. Estrutura de código obrigatória

Lógica de negócio em **funções puras**, isoladas de FastAPI, testáveis por script autônomo:

```
backend/
├── data/                       # CSVs versionados
├── src/
│   ├── etl/                    # funções puras: limpeza, filtros, log de correções
│   ├── cubagem/                # funções puras: m²→caixas, classificação 🟢🟡🔴
│   ├── optim/                  # funções puras: modelo PuLP + explicabilidade
│   ├── romaneio/               # gerador de PDF (WeasyPrint)
│   ├── llm/                    # camada 2 opcional (insights)
│   ├── api/                    # rotas FastAPI (thin — só orquestra)
│   ├── models/                 # Pydantic schemas
│   └── state.py                # boot in-memory: carrega CSVs no startup
└── tests/                      # pytest por módulo
```

Cada módulo do `src/` deve rodar sozinho via `python -m src.optim.solver` com dados de exemplo antes de ser plugado na API.

## 5. Ordem de leitura recomendada

1. Este charter
2. [[produto/prd]] — o quê e por quê
3. [[dominio/pipeline_etl]], [[dominio/cubagem]], [[dominio/otimizacao]] — o núcleo
4. [[api/endpoints]] + [[api/contratos]] — os contratos com o frontend
5. [[dados/dicionario]] — como os CSVs de fato vêm
6. [[frontend/telas]] — se estiver mexendo em UI

## 6. Caso oficial de aceite

**Eixo 4 + ACELLO 815** deve reproduzir (após ETL completo sobre os CSVs reais em `backend/data/`):

- 7 pedidos selecionados
- Peso: 4.797,335 / 4.800 kg (99,94%)
- Volume: 2,4421 / 2,4543 m³ (99,50%)
- Gargalo: **PESO**
- Violações: **0**
- Valor: R$ 16.770,85

Se o solver não bater esses números após o pipeline completo, algo no ETL ou na cubagem está errado. Ver [[entrega/criterios_aceite]].

## 7. Antes de qualquer PR

- [ ] Testes unitários do módulo tocado passam
- [ ] Caso oficial de aceite ainda reproduz
- [ ] Nenhum `TODO` sem ADR ou issue vinculada
- [ ] `qualidade/log` continua registrando as transformações
