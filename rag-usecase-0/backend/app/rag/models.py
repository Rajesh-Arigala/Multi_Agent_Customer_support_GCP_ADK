from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

@dataclass(frozen=True)
class Document:
    doc_id: str
    title: str
    content: str
    url: str
    source_type: str
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def searchable_text(self) -> str:
        metadata_text = " ".join(
            str(value) if not isinstance(value, list) else " ".join(str(item) for item in value)
            for key, value in self.metadata.items()
            if key in {"service_name", "specialty", "conditions", "treatments", "intent"}
        )
        return " ".join([self.doc_id, self.title, metadata_text, self.content])

@dataclass(frozen=True)
class RetrievalHit:
    document: Document
    score: float
    keyword_score: float
    vector_score: float
    filter_mode: str
    mode: str
