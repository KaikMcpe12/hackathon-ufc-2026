"""Cliente LLM provider-aware. Fallback silencioso: falha → LLMIndisponivel → 503.

Provedores:
- "anthropic" (default): SDK `anthropic`, API de mensagens.
- "nvidia" / "openai": SDK `openai` apontando para um endpoint compatível
  (NVIDIA NIM: LLM_BASE_URL=https://integrate.api.nvidia.com/v1).

A chave vem de LLM_API_KEY ou, se vazia, de ANTHROPIC_API_KEY (compat).
Ver ADR 0007 e PRD-07. O MVP roda sem LLM (sem custo obrigatório).
"""
from __future__ import annotations

import time

from .. import config
from .prompt import montar_prompt


class LLMIndisponivel(Exception):
    """Sem chave, SDK ausente, timeout ou erro do provedor → fallback silencioso."""


def _gerar_anthropic(prompt: str, key: str) -> str:
    try:
        import anthropic
    except ImportError as e:
        raise LLMIndisponivel("SDK anthropic não instalado") from e
    client = anthropic.Anthropic(api_key=key)
    msg = client.messages.create(
        model=config.LLM_MODEL,
        max_tokens=400,
        timeout=config.LLM_TIMEOUT_S,
        messages=[{"role": "user", "content": prompt}],
    )
    return "".join(b.text for b in msg.content if getattr(b, "type", "") == "text")


def _gerar_openai_compat(prompt: str, key: str) -> str:
    """NVIDIA NIM / OpenAI-compatível via SDK `openai` + base_url."""
    try:
        from openai import OpenAI
    except ImportError as e:
        raise LLMIndisponivel("SDK openai não instalado (necessário para NVIDIA NIM)") from e
    client = OpenAI(base_url=config.LLM_BASE_URL, api_key=key, timeout=config.LLM_TIMEOUT_S)
    resp = client.chat.completions.create(
        model=config.LLM_MODEL,
        max_tokens=400,
        temperature=0.4,
        messages=[{"role": "user", "content": prompt}],
    )
    return (resp.choices[0].message.content or "").strip()


def gerar_insight(plano: dict) -> tuple[str, str, int]:
    """Retorna (resumo, modelo, duracao_ms). Levanta LLMIndisponivel em qualquer falha."""
    key = config.llm_api_key()
    if not key:
        raise LLMIndisponivel("chave de LLM ausente (defina LLM_API_KEY ou ANTHROPIC_API_KEY)")

    prompt = montar_prompt(plano)
    t0 = time.time()
    try:
        if config.LLM_PROVIDER in ("nvidia", "openai"):
            resumo = _gerar_openai_compat(prompt, key)
        else:
            resumo = _gerar_anthropic(prompt, key)
    except LLMIndisponivel:
        raise
    except Exception as e:  # timeout, rate limit, provedor offline
        raise LLMIndisponivel(str(e)) from e
    return resumo.strip(), f"{config.LLM_PROVIDER}:{config.LLM_MODEL}", int((time.time() - t0) * 1000)
