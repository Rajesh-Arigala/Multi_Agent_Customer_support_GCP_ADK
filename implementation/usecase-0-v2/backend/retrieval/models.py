from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RetrievalDocument:
    doc_id: str
    source_type: str
    title: str
    content: str
    url: str = ""
    category: str = ""
    tags: tuple[str, ...] = ()
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def searchable_text(self) -> str:
        return " ".join(
            [
                self.doc_id,
                self.source_type,
                self.title,
                self.category,
                " ".join(self.tags),
                self.content,
            ]
        )


@dataclass(frozen=True)
class RetrievalResult:
    document: RetrievalDocument
    score: float
    keyword_score: float
    vector_score: float
    rank: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "doc_id": self.document.doc_id,
            "source_type": self.document.source_type,
            "title": self.document.title,
            "url": self.document.url,
            "score": round(self.score, 4),
            "keyword_score": round(self.keyword_score, 4),
            "vector_score": round(self.vector_score, 4),
            "rank": self.rank,
            "metadata": self.document.metadata,
        }
