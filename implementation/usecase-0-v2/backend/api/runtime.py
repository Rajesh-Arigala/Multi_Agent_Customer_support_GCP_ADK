from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from backend.config import DATA_DIR, GOOGLE_SHEETS_ID, LOCATION, PROJECT_ID
from backend.storage import CsvStore, GoogleSheetsStore, StorageService
from backend.tools.faq_tools import DEFAULT_CORPUS_PATH, DEFAULT_EMBEDDINGS_PATH

BASE_DIR = Path(__file__).resolve().parents[2]
METADATA_MANIFEST_PATH = (
    BASE_DIR
    / "rag_pipeline"
    / "drmadhupatil_corpus"
    / "07_output_enriched_documents"
    / "metadata_enrichment_manifest.json"
)


def build_runtime_store() -> StorageService:
    backend = os.getenv("STORAGE_BACKEND", "csv").strip().lower()
    if backend in {"google_sheets", "sheets"}:
        return GoogleSheetsStore(os.getenv("GOOGLE_SHEETS_ID", GOOGLE_SHEETS_ID))
    if backend == "csv":
        return CsvStore(Path(os.getenv("DATA_DIR", str(DATA_DIR))))
    raise ValueError(f"Unsupported STORAGE_BACKEND: {backend}")


def health_payload() -> dict[str, Any]:
    return {
        "status": "ok",
        "service": "usecase-0-v2-backend-api",
        "project_id": PROJECT_ID,
        "location": LOCATION,
        "storage_backend": os.getenv("STORAGE_BACKEND", "csv"),
    }


def metadata_status() -> dict[str, Any]:
    corpus_exists = DEFAULT_CORPUS_PATH.exists()
    embeddings_exists = DEFAULT_EMBEDDINGS_PATH.exists()
    manifest = _load_json(METADATA_MANIFEST_PATH)
    return {
        "status": "ok" if corpus_exists else "missing_corpus",
        "corpus_path": str(DEFAULT_CORPUS_PATH),
        "corpus_exists": corpus_exists,
        "embeddings_path": str(DEFAULT_EMBEDDINGS_PATH),
        "embeddings_exists": embeddings_exists,
        "metadata_manifest_path": str(METADATA_MANIFEST_PATH),
        "metadata_manifest_exists": METADATA_MANIFEST_PATH.exists(),
        "document_count": manifest.get("document_count", 0),
        "metadata_version": manifest.get("metadata_version", ""),
        "page_types": manifest.get("page_types", {}),
    }


def retrieval_smoke_queries() -> list[str]:
    return [
        "Can Dr Madhu help with PCOS and endometriosis?",
        "Do you provide IVF and ICSI treatment?",
        "I want fertility preservation options",
    ]


def _load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))
