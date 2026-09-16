# NobreLOG backend — FastAPI + PuLP + WeasyPrint.
# WeasyPrint exige libs nativas (Pango/Cairo/GDK-Pixbuf) → imagem Debian (não serverless).
FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DATA_DIR=/app/data

# Dependências nativas do WeasyPrint (conforme docs oficiais para Debian)
RUN apt-get update && apt-get install -y --no-install-recommends \
      libpango-1.0-0 libpangoft2-1.0-0 libharfbuzz0b \
      libcairo2 libgdk-pixbuf-2.0-0 libffi8 \
      shared-mime-info fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000
# Render/host injeta $PORT; bind em 0.0.0.0
CMD ["sh", "-c", "uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
