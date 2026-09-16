from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ...llm.client import LLMIndisponivel, gerar_insight

router = APIRouter(tags=["insight"])


class InsightRequest(BaseModel):
    plano: dict


@router.post("/insight")
def insight(req: InsightRequest):
    try:
        resumo, modelo, ms = gerar_insight(req.plano)
    except LLMIndisponivel as e:
        # fallback silencioso no frontend (bloco de IA recolhe)
        raise HTTPException(503, detail=str(e))
    return {"resumo": resumo, "modelo": modelo, "duracao_ms": ms}
