"""Helpers puros de normalização de texto/números vindos dos CSVs brasileiros."""
from __future__ import annotations

import re
import unicodedata

import pandas as pd


def strip_accents(s: str) -> str:
    """Remove acentos preservando o resto. 'Ararendá' -> 'Ararenda'."""
    if not isinstance(s, str):
        return s
    nfkd = unicodedata.normalize("NFKD", s)
    return "".join(c for c in nfkd if not unicodedata.combining(c))


def norm_cidade(s: str | float) -> str:
    """Uppercase, sem acentos, sem espaços duplicados/extras. Para comparação de eixo."""
    if not isinstance(s, str):
        return ""
    out = strip_accents(s).upper().strip()
    out = re.sub(r"\s+", " ", out)
    return out


def norm_upper(s: str | float) -> str:
    if not isinstance(s, str):
        return ""
    return s.upper().strip()


_MOEDA_RE = re.compile(r"[^\d,.-]")


def parse_valor_br(s: str | float) -> float:
    """'R$ 1.811,87' -> 1811.87 ; '4.800 kg' -> 4800.0 ; '2,4543' -> 2.4543."""
    if isinstance(s, (int, float)):
        return float(s)
    if not isinstance(s, str) or not s.strip():
        return float("nan")
    txt = _MOEDA_RE.sub("", s)  # remove R$, kg, espaços, símbolos
    # Formato BR: ponto = milhar, vírgula = decimal.
    if "," in txt:
        txt = txt.replace(".", "").replace(",", ".")
    else:
        # sem vírgula: ponto só é separador de milhar quando seguido de 3 dígitos
        # ('1.700' -> 1700). Mantém decimais reais como '0.9'.
        txt = re.sub(r"\.(?=\d{3}(\D|$))", "", txt)
    try:
        return float(txt)
    except ValueError:
        return float("nan")


def parse_faixa_maior(s: str | float) -> float:
    """Extrai todos os números BR de um texto e retorna o MAIOR.

    Regra conservadora da cubagem: quando o Ranking indica faixa
    ('≈0,45 (faixa 0,40-0,47)'), usar o valor maior para nunca subestimar peso.
    """
    if isinstance(s, (int, float)):
        return float(s)
    if not isinstance(s, str) or not s.strip():
        return float("nan")
    vals = []
    for tok in re.findall(r"\d[\d.]*(?:,\d+)?", s):
        v = parse_valor_br(tok)
        if v == v:  # não NaN
            vals.append(v)
    return max(vals) if vals else float("nan")


def parse_volume_tolerante(s: str | float) -> tuple[float, bool]:
    """Ranking Volume_m3 pode vir '≈0,009 (estimado)'. Retorna (valor, estimado)."""
    if isinstance(s, (int, float)):
        return float(s), False
    if not isinstance(s, str) or not s.strip():
        return float("nan"), False
    estimado = "estimado" in s.lower()
    return parse_valor_br(s), estimado


def parse_data_br(s: str, lote_ano: int) -> tuple[pd.Timestamp | None, str | None]:
    """Parse dd/mm/yyyy (ou dd/mm/yy). Corrige ano fora do lote.

    Retorna (data, regra_correcao|None). Nunca adivinha data completa — só o ano,
    e apenas quando dia/mês são plausíveis.
    """
    raw = (s or "").strip()
    dt = pd.to_datetime(raw, dayfirst=True, errors="coerce")
    if dt is pd.NaT or pd.isna(dt):
        return None, None
    if dt.year != lote_ano and 1 <= dt.month <= 12 and 1 <= dt.day <= 31:
        corrigida = dt.replace(year=lote_ano)
        return corrigida, "ano_fora_do_lote"
    return dt, None
