"""Entrypoint FastAPI. Boot in-memory no startup (ADR 0001)."""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import config, state
from .api.routes import etl, llm, metadados, otimizar, pedidos, qualidade, romaneio


@asynccontextmanager
async def lifespan(app: FastAPI):
    state.bootstrap()  # carrega os CSVs seed em memória
    yield


app = FastAPI(title="NobreLOG Optimizer", version=config.VERSION, lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    st = state.get_state()
    return {"status": "ok", "version": config.VERSION,
            "usa_seed": config.USE_SEED_DATA,
            "tem_dados": state.tem_dados(),
            "pedidos_processados": len(st.pedidos_processados)}


for r in (metadados.router, pedidos.router, qualidade.router, otimizar.router,
          romaneio.router, llm.router, etl.router):
    app.include_router(r, prefix="/api/v1")
