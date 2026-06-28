FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080
ENV PYTHONPATH=/app

WORKDIR /app

COPY requirements.txt requirements-api.txt requirements-retrieval.txt requirements-embeddings.txt ./
RUN pip install --no-cache-dir \
    -r requirements.txt \
    -r requirements-api.txt \
    -r requirements-retrieval.txt \
    -r requirements-embeddings.txt

COPY backend ./backend
COPY frontend ./frontend
COPY rag_pipeline ./rag_pipeline

CMD ["sh", "-c", "uvicorn backend.api.app:app --host 0.0.0.0 --port ${PORT}"]
