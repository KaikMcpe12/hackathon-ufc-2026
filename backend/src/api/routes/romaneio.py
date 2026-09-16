from datetime import date

from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel

from ...romaneio.gerador import PlanoComViolacoes, gerar_pdf

router = APIRouter(tags=["romaneio"])


class RomaneioGenerateRequest(BaseModel):
    plano: dict
    coordenador: str = "—"
    data_carga: date | None = None


@router.post("/romaneio/generate")
def generate(req: RomaneioGenerateRequest):
    data = req.data_carga.isoformat() if req.data_carga else None
    try:
        pdf = gerar_pdf(req.plano, req.coordenador, data)
    except PlanoComViolacoes as e:
        raise HTTPException(422, detail=str(e))
    return Response(
        content=pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="romaneio.pdf"'},
    )
