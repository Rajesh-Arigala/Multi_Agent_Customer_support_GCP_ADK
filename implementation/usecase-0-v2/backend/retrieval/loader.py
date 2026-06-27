from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable

from backend.retrieval.models import RetrievalDocument


def load_jsonl_documents(path: Path) -> list[RetrievalDocument]:
    documents = []
    if not path.exists():
        return documents

    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        row = json.loads(line)
        metadata = dict(row.get("metadata", {}))
        metadata.setdefault("usecase", row.get("usecase", ""))
        metadata.setdefault("domain", row.get("domain", ""))
        metadata.setdefault("page_id", row.get("page_id", ""))
        documents.append(
            RetrievalDocument(
                doc_id=row["doc_id"],
                source_type=row.get("source_type", "website"),
                title=row.get("title", row.get("page_id", row["doc_id"])),
                content=row.get("content", ""),
                url=row.get("url", ""),
                category=row.get("category", ""),
                tags=tuple(row.get("tags", [])),
                metadata=metadata,
            )
        )
    return documents


def documents_from_faq_rows(rows: Iterable[dict[str, str]]) -> list[RetrievalDocument]:
    documents = []
    for row in rows:
        if row.get("status", "active").lower() not in {"", "active"}:
            continue
        tags = _split_tags(row.get("tags", ""))
        answer = row.get("answer", "")
        question = row.get("question", "")
        documents.append(
            RetrievalDocument(
                doc_id=row.get("faq_id", "") or row.get("id", "") or question[:40],
                source_type="faq",
                title=question,
                content=answer,
                category=row.get("category", ""),
                tags=tuple(tags),
                metadata={
                    "status": row.get("status", "active"),
                    "question": question,
                    "answer": answer,
                },
            )
        )
    return documents


def _split_tags(value: str) -> list[str]:
    return [part.strip() for part in value.replace(";", ",").split(",") if part.strip()]
