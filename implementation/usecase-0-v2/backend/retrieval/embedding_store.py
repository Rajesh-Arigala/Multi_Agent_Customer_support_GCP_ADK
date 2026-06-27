from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from backend.retrieval.models import RetrievalDocument


def save_embedding_records(
    path: Path,
    documents: list[RetrievalDocument],
    vectors: list[list[float]],
    model_name: str,
    project_id: str,
    location: str,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = []
    generated_at = datetime.now(timezone.utc).isoformat()
    for document, vector in zip(documents, vectors):
        lines.append(
            json.dumps(
                {
                    "doc_id": document.doc_id,
                    "vector": vector,
                    "metadata": {
                        "model_name": model_name,
                        "project_id": project_id,
                        "location": location,
                        "generated_at": generated_at,
                        "source_type": document.source_type,
                        "title": document.title,
                        "url": document.url,
                        "document_metadata": document.metadata,
                    },
                },
                ensure_ascii=False,
            )
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def load_embedding_records(path: Path) -> dict[str, list[float]]:
    vectors: dict[str, list[float]] = {}
    if not path.exists():
        return vectors
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        vectors[row["doc_id"]] = [float(value) for value in row["vector"]]
    return vectors


def write_embedding_manifest(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
