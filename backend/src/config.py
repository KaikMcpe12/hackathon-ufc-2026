"""Configuração via ambiente. Sem segredos no código (Charter)."""
from __future__ import annotations

import os
from pathlib import Path

# Raiz de dados (CSVs seed). Sobrescrevível por env para testes/deploy.
DATA_DIR = Path(os.getenv("DATA_DIR", str(Path(__file__).resolve().parent.parent / "data")))

# CORS: origens liberadas para o frontend (Vite dev + Vercel em produção).
CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")

# Lote de referência dos dados (para correção de datas fora do lote).
LOTE_ANO = int(os.getenv("LOTE_ANO", "2026"))

# LLM (camada 2 opcional — ver ADR 0007 / PRD-07).
# Provider: "anthropic" (default) ou "nvidia"/"openai" (endpoint compatível com OpenAI).
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "anthropic").lower()
LLM_MODEL = os.getenv("LLM_MODEL", "claude-haiku-4-5")
LLM_TIMEOUT_S = float(os.getenv("LLM_TIMEOUT_S", "8"))
# Chave genérica; se vazia, cai para ANTHROPIC_API_KEY (compat — pode reusar a mesma env).
LLM_API_KEY = os.getenv("LLM_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
# Base URL para provedores compatíveis com OpenAI (NVIDIA NIM: https://integrate.api.nvidia.com/v1).
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://integrate.api.nvidia.com/v1")


def llm_api_key() -> str:
    """Chave efetiva: LLM_API_KEY tem prioridade; senão reusa ANTHROPIC_API_KEY."""
    return LLM_API_KEY or ANTHROPIC_API_KEY

# Solver
SOLVER_TIME_LIMIT = int(os.getenv("SOLVER_TIME_LIMIT", "30"))
DESEMPATE_EPSILON = float(os.getenv("DESEMPATE_EPSILON", "1e-4"))  # ADR 0008

# Ocupação mínima no gargalo para o frete "valer a viagem" (alerta, não bloqueia).
OCUPACAO_MINIMA = float(os.getenv("OCUPACAO_MINIMA", "0.6"))

VERSION = "0.1.0"
