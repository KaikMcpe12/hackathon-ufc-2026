from fastapi import APIRouter

from ...state import get_state
from ..serializers import eixo_to_dict, veiculo_to_dict

router = APIRouter(tags=["metadados"])


@router.get("/eixos")
def listar_eixos():
    st = get_state()
    return {"eixos": [eixo_to_dict(r) for _, r in st.eixos.iterrows()]}


@router.get("/veiculos")
def listar_veiculos():
    st = get_state()
    return {"veiculos": [veiculo_to_dict(r) for _, r in st.veiculos.iterrows()]}


@router.get("/semanas")
def listar_semanas():
    st = get_state()
    semanas = sorted(int(s) for s in st.pedidos_processados["semana"].unique())
    return {"semanas": semanas, "padrao": max(semanas) if semanas else None}
