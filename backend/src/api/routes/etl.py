from fastapi import APIRouter, File, HTTPException, UploadFile

from ... import state
from .qualidade import resumo as _resumo

router = APIRouter(prefix="/etl", tags=["etl"])


@router.post("/ingest")
async def ingest(
    semana_1: UploadFile | None = File(None),
    semana_2: UploadFile | None = File(None),
    semana_3: UploadFile | None = File(None),
    semana_4: UploadFile | None = File(None),
    ranking: UploadFile | None = File(None),
    rotas: UploadFile | None = File(None),
):
    enviados = {
        "semana_1": semana_1, "semana_2": semana_2, "semana_3": semana_3,
        "semana_4": semana_4, "ranking": ranking, "rotas": rotas,
    }
    files = {slot: await uf.read() for slot, uf in enviados.items() if uf is not None}
    if not files:
        raise HTTPException(400, detail="Nenhum arquivo enviado.")
    try:
        state.reingest(files)
    except state.ColunasInvalidas as e:
        raise HTTPException(400, detail=str(e))

    semanas = sorted(int(s.split("_")[1]) for s in files if s.startswith("semana_"))
    return {"semanas_atualizadas": semanas, "resumo_qualidade": _resumo()}
