from __future__ import annotations

import json
from pathlib import Path

from app.rag.models import Document


def load_documents(path: Path) -> list[Document]:
    documents: list[Document] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        metadata = dict(row.get("metadata", {}))
        metadata.setdefault("domain", row.get("domain", ""))
        metadata.setdefault("page_id", row.get("page_id", ""))
        documents.append(
            Document(
                doc_id=row["doc_id"],
                title=row.get("title", row["doc_id"]),
                content=row.get("content", ""),
                url=row.get("url", ""),
                source_type=row.get("source_type", "website"),
                metadata=metadata,
            )
        )
    return documents


def load_vectors(path: Path) -> dict[str, list[float]]:
    vectors: dict[str, list[float]] = {}
    if not path.exists():
        return vectors
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        vectors[row["doc_id"]] = [float(value) for value in row["vector"]]
    return vectors


def save_vectors(path: Path, vectors: dict[str, list[float]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [json.dumps({"doc_id": doc_id, "vector": vector}) for doc_id, vector in vectors.items()]
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")


def load_manifest(path: Path) -> dict:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))
