from fastapi import APIRouter, HTTPException, Query

from ...state import get_state
from ..serializers import pedido_to_dict

router = APIRouter(prefix="/pedidos", tags=["pedidos"])


@router.get("")
def listar(
    eixo: int | None = Query(None, ge=1, le=5),
    semana: int | None = Query(None, ge=1, le=4),
    qualidade: str | None = Query(None, pattern="^(COMPLETA|ESTIMADA|AUSENTE)$"),
    cidade: str | None = None,
    q: str | None = None,
):
    df = get_state().pedidos_processados
    if eixo is not None:
        df = df[df["eixo_id"] == eixo]
    if semana is not None:
        df = df[df["semana"] == semana]
    if qualidade:
        df = df[df["qualidade_cubagem"] == qualidade]
    if cidade:
        df = df[df["cidade"].str.contains(cidade.upper(), na=False)]
    if q:
        df = df[df["pedido"].str.contains(q.upper(), na=False)]
    pedidos = [pedido_to_dict(r) for _, r in df.iterrows()]
    return {"total": len(pedidos), "pedidos": pedidos}


@router.get("/{pedido_id}")
def detalhe(pedido_id: str):
    df = get_state().pedidos_processados
    row = df[df["pedido"] == pedido_id]
    if row.empty:
        raise HTTPException(404, detail=f"Pedido {pedido_id} não encontrado")
    return pedido_to_dict(row.iloc[0])
