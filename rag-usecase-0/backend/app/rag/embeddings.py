from __future__ import annotations

import math
from collections import Counter

from app.config import EMBEDDING_MODEL_NAME, GOOGLE_CLOUD_LOCATION, GOOGLE_CLOUD_PROJECT
from app.rag.models import Document
from app.rag.text import tokenize

class VertexEmbeddingClient:
    def __init__(self):
        from google import genai
        from google.genai.types import HttpOptions

        self._embed_config_class = None
        self.client = genai.Client(vertexai=True, project=GOOGLE_CLOUD_PROJECT, location=GOOGLE_CLOUD_LOCATION, http_options=HttpOptions(api_version="v1"))

    def embed_query(self, text: str) -> list[float]:
        return self._embed([text], "RETRIEVAL_QUERY")[0]

    def embed_documents(self, documents: list[Document]) -> dict[str, list[float]]:
        texts = [document.searchable_text for document in documents]
        vectors: list[list[float]] = []
        batch_size = 8
        for start in range(0, len(texts), batch_size):
            vectors.extend(self._embed(texts[start:start + batch_size], "RETRIEVAL_DOCUMENT"))
        return {document.doc_id: vector for document, vector in zip(documents, vectors)}

    def _embed(self, texts: list[str], task_type: str) -> list[list[float]]:
        from google.genai.types import EmbedContentConfig

        response = self.client.models.embed_content(model=EMBEDDING_MODEL_NAME, contents=texts, config=EmbedContentConfig(task_type=task_type))
        return [normalize([float(value) for value in embedding.values]) for embedding in response.embeddings]

class HashEmbeddingClient:
    def embed_query(self, text: str) -> list[float]:
        buckets = [0.0] * 256
        for token, count in Counter(tokenize(text)).items():
            buckets[hash(token) % len(buckets)] += float(count)
        return normalize(buckets)

    def embed_documents(self, documents: list[Document]) -> dict[str, list[float]]:
        return {document.doc_id: self.embed_query(document.searchable_text) for document in documents}

def normalize(vector: list[float]) -> list[float]:
    norm = math.sqrt(sum(value * value for value in vector))
    if not norm:
        return vector
    return [value / norm for value in vector]

def cosine(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0
    return max(sum(a * b for a, b in zip(left, right)), 0.0)
