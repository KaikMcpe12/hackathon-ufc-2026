from fastapi import APIRouter

from ...state import get_state

router = APIRouter(prefix="/qualidade", tags=["qualidade"])


@router.get("/resumo")
def resumo():
    s = get_state().stats
    return {
        "registros_processados": s["registros_processados"],
        "inconsistencias_detectadas": s["inconsistencias_detectadas"],
        "materiais_ranking": s["materiais_ranking"],
        "pedidos_completa": s["pedidos_completa"],
        "pedidos_estimada": s["pedidos_estimada"],
        "pedidos_ausente": s["pedidos_ausente"],
        "pipeline_stages": s["pipeline_stages"],
    }


@router.get("/log")
def log():
    return {"correcoes": get_state().log_correcoes}


@router.get("/motivos-exclusao")
def motivos_exclusao():
    return {"motivos": get_state().motivos_exclusao}
