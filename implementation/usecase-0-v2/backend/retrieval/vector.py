from __future__ import annotations

import hashlib
import math

from backend.retrieval.models import RetrievalDocument
from backend.retrieval.text import tokenize


class HashEmbeddingModel:
    def __init__(self, dimensions: int = 384):
        self.dimensions = dimensions

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * self.dimensions
        for token in tokenize(text):
            digest = hashlib.sha256(token.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % self.dimensions
            sign = 1.0 if digest[4] % 2 == 0 else -1.0
            vector[index] += sign

        norm = math.sqrt(sum(value * value for value in vector))
        if norm == 0:
            return vector
        return [value / norm for value in vector]


class VectorRetriever:
    def __init__(self, documents: list[RetrievalDocument], embedding_model: HashEmbeddingModel | None = None):
        self.documents = documents
        self.embedding_model = embedding_model or HashEmbeddingModel()
        self.doc_vectors = [self.embedding_model.embed(document.searchable_text) for document in documents]
        self.backend = "python"
        self._faiss_index = None
        self._try_build_faiss_index()

    def score(self, query: str) -> dict[str, float]:
        if not self.documents:
            return {}

        query_vector = self.embedding_model.embed(query)
        if self._faiss_index is not None:
            return self._faiss_scores(query_vector)
        return self._python_scores(query_vector)

    def _try_build_faiss_index(self) -> None:
        try:
            import faiss  # type: ignore
            import numpy as np  # type: ignore
        except Exception:
            return

        if not self.doc_vectors:
            return

        vectors = np.array(self.doc_vectors, dtype="float32")
        index = faiss.IndexFlatIP(vectors.shape[1])
        index.add(vectors)
        self._faiss_index = index
        self._np = np
        self.backend = "faiss"

    def _faiss_scores(self, query_vector: list[float]) -> dict[str, float]:
        query = self._np.array([query_vector], dtype="float32")
        scores, indexes = self._faiss_index.search(query, len(self.documents))
        return {
            self.documents[int(index)].doc_id: max(float(score), 0.0)
            for score, index in zip(scores[0], indexes[0])
            if int(index) >= 0
        }

    def _python_scores(self, query_vector: list[float]) -> dict[str, float]:
        scores = {}
        for document, vector in zip(self.documents, self.doc_vectors):
            score = sum(left * right for left, right in zip(query_vector, vector))
            scores[document.doc_id] = max(score, 0.0)
        return scores
