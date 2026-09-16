from datetime import date

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ...optim.planejador import CenarioInvalido, otimizar_cenario
from ...state import get_state

router = APIRouter(tags=["otimizacao"])


class OtimizarRequest(BaseModel):
    eixo: int = Field(ge=1, le=5)
    veiculo: str
    semana: int | None = Field(default=None, ge=1, le=4)  # None = todas (protótipo/gate)
    data_carga: date | None = None
    incluir_estimadas: bool = True


class CompararRequest(BaseModel):
    eixo: int = Field(ge=1, le=5)
    semana: int | None = Field(default=None, ge=1, le=4)
    veiculos: list[str]
    data_carga: date | None = None


@router.post("/otimizar")
def otimizar(req: OtimizarRequest):
    st = get_state()
    try:
        return otimizar_cenario(st, req.eixo, req.veiculo, req.semana,
                                req.incluir_estimadas, req.data_carga)
    except CenarioInvalido as e:
        raise HTTPException(400, detail=str(e))


@router.post("/otimizar/comparar")
def comparar(req: CompararRequest):
    st = get_state()
    cenarios = []
    for veic in req.veiculos:
        try:
            plano = otimizar_cenario(st, req.eixo, veic, req.semana, True, req.data_carga)
        except CenarioInvalido as e:
            raise HTTPException(400, detail=str(e))
        cenarios.append({"veiculo": veic, "resultado": plano})

    # recomendado: maior (0,5·Op+0,5·Ov) sem violações; empate → maior valor (E6)
    def score(c):
        t = c["resultado"]["totais"]
        return (0.5 * t["ocupacao_peso"] + 0.5 * t["ocupacao_volume"], t["valor_total"])

    validos = [c for c in cenarios if c["resultado"]["violacoes"] == 0]
    recomendado = max(validos or cenarios, key=score)["veiculo"]
    return {"cenarios": cenarios, "recomendado": recomendado}
