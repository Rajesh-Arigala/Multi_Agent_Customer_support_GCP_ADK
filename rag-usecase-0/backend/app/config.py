from __future__ import annotations

import os
from pathlib import Path

APP_DIR = Path(__file__).resolve().parent
PROJECT_DIR = APP_DIR.parents[1]
DATA_DIR = PROJECT_DIR / "data"
FRONTEND_DIR = PROJECT_DIR / "frontend"

CORPUS_PATH = Path(os.getenv("RAG_CORPUS_PATH", DATA_DIR / "corpus/drmadhupatil_enriched_rag_corpus.jsonl"))
EMBEDDINGS_PATH = Path(os.getenv("RAG_EMBEDDINGS_PATH", DATA_DIR / "embeddings/drmadhupatil_vertex_embeddings.jsonl"))
METADATA_MANIFEST_PATH = Path(os.getenv("RAG_METADATA_MANIFEST_PATH", DATA_DIR / "corpus/metadata_enrichment_manifest.json"))

GOOGLE_CLOUD_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "multi-agent-adk-1")
GOOGLE_CLOUD_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "text-embedding-005")
RAG_USE_VERTEX = os.getenv("RAG_USE_VERTEX", "true").strip().lower() in {"1", "true", "yes", "on"}
