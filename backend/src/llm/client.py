"""Cliente LLM (Anthropic default). Fallback silencioso: falha → LLMIndisponivel → 503.

Ver ADR 0007 e PRD-07. O MVP roda sem LLM (sem custo obrigatório).
"""
from __future__ import annotations

import time

from .. import config
from .prompt import montar_prompt


class LLMIndisponivel(Exception):
    """Sem chave, SDK ausente, timeout ou erro do provedor → fallback silencioso."""


def gerar_insight(plano: dict) -> tuple[str, str, int]:
    """Retorna (resumo, modelo, duracao_ms). Levanta LLMIndisponivel em qualquer falha."""
    if not config.ANTHROPIC_API_KEY:
        raise LLMIndisponivel("ANTHROPIC_API_KEY ausente")
    try:
        import anthropic
    except ImportError as e:
        raise LLMIndisponivel("SDK anthropic não instalado") from e

    t0 = time.time()
    try:
        client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        msg = client.messages.create(
            model=config.LLM_MODEL,
            max_tokens=400,
            timeout=config.LLM_TIMEOUT_S,
            messages=[{"role": "user", "content": montar_prompt(plano)}],
        )
        resumo = "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")
    except Exception as e:  # timeout, rate limit, provedor offline
        raise LLMIndisponivel(str(e)) from e
    return resumo.strip(), f"anthropic:{config.LLM_MODEL}", int((time.time() - t0) * 1000)
