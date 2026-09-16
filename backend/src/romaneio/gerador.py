"""Gera o Romaneio (PDF) a partir de um PlanoDeCarga. WeasyPrint + Jinja2 (ADR 0004).

Regra inviolável: números do PDF = números do solver. Nunca recalcular aqui.
"""
from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from .. import config

_TEMPLATES = Path(__file__).parent
_env = Environment(
    loader=FileSystemLoader(str(_TEMPLATES)),
    autoescape=select_autoescape(["html"]),
)


def br(v: float | None, casas: int = 2) -> str:
    """Formata número no padrão pt-BR (milhar '.', decimal ',')."""
    if v is None:
        return "—"
    s = f"{v:,.{casas}f}"  # 16,770.85
    return s.replace(",", "§").replace(".", ",").replace("§", ".")


_env.filters["br"] = br


class PlanoComViolacoes(Exception):
    pass


def render_html(plano: dict, coordenador: str = "—", data_carga: str | None = None) -> str:
    if plano.get("violacoes", 0) > 0:
        raise PlanoComViolacoes(f"Plano com {plano['violacoes']} violação(ões).")
    return _env.get_template("template.html").render(
        p=plano,
        coordenador=coordenador or "—",
        data_carga=data_carga or plano.get("data_carga", ""),
        versao=config.VERSION,
    )


def gerar_pdf(plano: dict, coordenador: str = "—", data_carga: str | None = None) -> bytes:
    """Retorna os bytes do PDF. Levanta PlanoComViolacoes se violacoes > 0 (→ 422)."""
    from weasyprint import HTML  # import tardio (dependências nativas)

    html = render_html(plano, coordenador, data_carga)
    return HTML(string=html).write_pdf()
