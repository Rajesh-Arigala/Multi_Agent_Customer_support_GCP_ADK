from __future__ import annotations

from collections.abc import Mapping

from backend.retrieval.keyword import BM25Retriever
from backend.retrieval.models import RetrievalDocument, RetrievalResult
from backend.retrieval.ranking import apply_service_ranking_policy
from backend.retrieval.text import tokenize
from backend.retrieval.vector import EmbeddingModel, VectorRetriever


class HybridRetriever:
    def __init__(
        self,
        documents: list[RetrievalDocument],
        keyword_weight: float = 0.55,
        vector_weight: float = 0.45,
        confidence_threshold: float = 0.35,
        embedding_model: EmbeddingModel | None = None,
        document_vectors: Mapping[str, list[float]] | None = None,
    ):
        self.documents = documents
        self.keyword_weight = keyword_weight
        self.vector_weight = vector_weight
        self.confidence_threshold = confidence_threshold
        self.embedding_model = embedding_model
        self.document_vectors = document_vectors or {}
        self.keyword = BM25Retriever(documents)
        self.vector = VectorRetriever(
            documents,
            embedding_model=self.embedding_model,
            document_vectors=self.document_vectors,
        )

    def search(
        self,
        query: str,
        top_k: int = 5,
        filters: dict[str, str] | None = None,
    ) -> list[RetrievalResult]:
        candidate_documents = self._filter_documents(filters)
        if not candidate_documents:
            return []

        keyword_scores = BM25Retriever(candidate_documents).score(query)
        vector_scores = VectorRetriever(
            candidate_documents,
            embedding_model=self.embedding_model,
            document_vectors=self.document_vectors,
        ).score(query)
        results = []

        for document in candidate_documents:
            keyword_score = keyword_scores.get(document.doc_id, 0.0)
            vector_score = vector_scores.get(document.doc_id, 0.0)
            fused_score = (self.keyword_weight * keyword_score) + (self.vector_weight * vector_score)
            fused_score = min(fused_score + _title_overlap_boost(query, document), 1.0)
            fused_score = apply_service_ranking_policy(query, document, fused_score)
            if fused_score <= 0:
                continue
            results.append(
                RetrievalResult(
                    document=document,
                    score=fused_score,
                    keyword_score=keyword_score,
                    vector_score=vector_score,
                    rank=0,
                )
            )

        results.sort(key=lambda item: item.score, reverse=True)
        return [
            RetrievalResult(
                document=result.document,
                score=result.score,
                keyword_score=result.keyword_score,
                vector_score=result.vector_score,
                rank=index,
            )
            for index, result in enumerate(results[:top_k], start=1)
        ]

    def best_match(
        self,
        query: str,
        filters: dict[str, str] | None = None,
    ) -> RetrievalResult | None:
        results = self.search(query, top_k=1, filters=filters)
        if not results:
            return None
        best = results[0]
        if best.score < self.confidence_threshold:
            return None
        return best

    def _filter_documents(self, filters: dict[str, str] | None) -> list[RetrievalDocument]:
        if not filters:
            return self.documents

        filtered = []
        for document in self.documents:
            keep = True
            for key, value in filters.items():
                candidate = getattr(document, key, None)
                if candidate is None:
                    candidate = document.metadata.get(key)
                if str(candidate) != str(value):
                    keep = False
                    break
            if keep:
                filtered.append(document)
        return filtered


def _title_overlap_boost(query: str, document: RetrievalDocument) -> float:
    query_tokens = set(tokenize(query))
    title_tokens = set(tokenize(document.title))
    if not query_tokens or not title_tokens:
        return 0.0
    return 0.35 * (len(query_tokens & title_tokens) / len(query_tokens))
