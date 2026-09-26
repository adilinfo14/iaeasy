# --- Stage 1: build frontend ---
FROM node:22-slim AS frontend-build
WORKDIR /app/frontend
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# --- Stage 2: backend runtime ---
FROM python:3.11-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgl1 \
    libglib2.0-0 \
    tesseract-ocr \
    tesseract-ocr-fra \
    espeak-ng \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app
COPY --from=frontend-build /app/frontend/dist ./static

ENV IAEASY_DATA_DIR=/data
ENV HF_HOME=/data/hf_cache
RUN mkdir -p /data

EXPOSE 8000
# timeout-graceful-shutdown borne l'attente de fermeture des connexions ouvertes (ex: un flux
# SSE d'entraînement en cours) lors d'un rechargement --reload, pour ne jamais bloquer le site
# indéfiniment pour un visiteur en train de l'utiliser.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload", "--reload-dir", "/app/app", "--timeout-graceful-shutdown", "5"]
