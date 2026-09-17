"""Cadastro de produtos/pedidos (form = 1 · CSV = N) com upsert. Requer SQLite (PRD-12)."""
from __future__ import annotations

import io

import pandas as pd
from fastapi import APIRouter, File, HTTPException, UploadFile
from pydantic import BaseModel

from ... import state
from ...db.models import Pedido, Produto

router = APIRouter(prefix="/cadastro", tags=["cadastro"])


class ProdutoForm(BaseModel):
    codigo: str
    produto: str = ""
    unidade_venda: str = ""
    peso_kg: str = ""
    volume_m3: str = ""
    dado_estimado: str = "NAO"
    fonte: str = ""


class PedidoForm(BaseModel):
    pedido: str
    data: str = ""
    vendedor: str = ""
    situacao: str = ""
    cidade: str = ""
    logistica: str = ""
    situacao_csv_entrega: str = ""
    valor_pedido: str = ""
    qtd_itens: str = ""
    itens_resumo: str = ""
    semana: int = 4


def _guard():
    if not state.repo_ativo():
        raise HTTPException(400, detail="Cadastro requer STATE_BACKEND=sqlite.")


def _csv_rows(raw: bytes, csvmap: dict) -> list[dict]:
    df = pd.read_csv(io.BytesIO(raw), sep=";", dtype=str, encoding="utf-8-sig",
                     keep_default_na=False)
    df.columns = [c.strip() for c in df.columns]
    return [{attr: str(r.get(csv, "")) for csv, attr in csvmap.items()} for _, r in df.iterrows()]


@router.get("/status")
def status():
    return {"ativo": state.repo_ativo(), **state.contagem_db()}


@router.post("/produto")
def cadastrar_produto(req: ProdutoForm):
    _guard()
    return state.cadastrar_produtos([req.model_dump()])


@router.post("/pedido")
def cadastrar_pedido(req: PedidoForm):
    _guard()
    return state.cadastrar_pedidos([req.model_dump()])


@router.post("/produtos")
async def cadastrar_produtos_csv(arquivo: UploadFile = File(...)):
    _guard()
    return state.cadastrar_produtos(_csv_rows(await arquivo.read(), Produto.CSV))


@router.post("/pedidos")
async def cadastrar_pedidos_csv(arquivo: UploadFile = File(...), semana: int = 4):
    _guard()
    rows = _csv_rows(await arquivo.read(), Pedido.CSV)
    for row in rows:
        row["semana"] = semana
    return state.cadastrar_pedidos(rows)
