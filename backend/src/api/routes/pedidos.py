from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ...cubagem.classificador import selo_pedido
from ...state import get_state
from ..serializers import pedido_to_dict

router = APIRouter(prefix="/pedidos", tags=["pedidos"])


class ItemRevisao(BaseModel):
    codigo: str
    peso_kg: float = Field(gt=0)      # peso TOTAL do item no pedido (kg)
    volume_m3: float = Field(gt=0)    # volume TOTAL do item no pedido (m³)


class RevisarRequest(BaseModel):
    itens: list[ItemRevisao]


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


@router.post("/{pedido_id}/revisar")
def revisar(pedido_id: str, req: RevisarRequest):
    """UC07 — coordenador informa peso/volume dos itens de um pedido 🔴.

    Aplica a cubagem manual (marcada como estimada 🟡) e recalcula o pedido, que
    então passa a poder entrar no solver (com incluir_estimadas=true).
    """
    df = get_state().pedidos_processados
    sel = df.index[df["pedido"] == pedido_id]
    if len(sel) == 0:
        raise HTTPException(404, detail=f"Pedido {pedido_id} não encontrado")
    idx = sel[0]
    itens = list(df.at[idx, "itens"] or [])
    manuais = {i.codigo: i for i in req.itens}
    for it in itens:
        m = manuais.get(it["codigo"])
        if m:
            it["peso_total_kg"] = m.peso_kg
            it["volume_total_m3"] = m.volume_m3
            it["dado_estimado"] = True
            it["selo_item"] = "ESTIMADA"  # cubagem informada manualmente = estimada

    selo = selo_pedido([it["selo_item"] for it in itens])
    if selo == "AUSENTE":  # ainda há itens sem cubagem
        peso = vol = float("nan")
    else:
        peso = sum(it["peso_total_kg"] for it in itens)
        vol = sum(it["volume_total_m3"] for it in itens)

    df.at[idx, "itens"] = itens
    df.at[idx, "peso_kg"] = peso
    df.at[idx, "volume_m3"] = vol
    df.at[idx, "qualidade_cubagem"] = selo
    return pedido_to_dict(df.loc[idx])
