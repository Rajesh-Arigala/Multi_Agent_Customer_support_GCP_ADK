from __future__ import annotations

import math
from collections import Counter

from backend.retrieval.models import RetrievalDocument
from backend.retrieval.text import normalize_score, tokenize, tokenize_with_ngrams


class BM25Retriever:
    def __init__(self, documents: list[RetrievalDocument], k1: float = 1.5, b: float = 0.75):
        self.documents = documents
        self.k1 = k1
        self.b = b
        self.doc_tokens = [tokenize_with_ngrams(document.searchable_text) for document in documents]
        self.doc_lengths = [len(tokens) for tokens in self.doc_tokens]
        self.avg_doc_length = sum(self.doc_lengths) / len(self.doc_lengths) if self.doc_lengths else 0.0
        self.doc_frequencies = self._build_doc_frequencies()

    def score(self, query: str) -> dict[str, float]:
        query_tokens = tokenize_with_ngrams(query)
        if not query_tokens or not self.documents:
            return {}

        raw_scores = {}
        query_counts = Counter(query_tokens)
        for index, tokens in enumerate(self.doc_tokens):
            token_counts = Counter(tokens)
            score = 0.0
            for token in query_counts:
                frequency = token_counts.get(token, 0)
                if not frequency:
                    continue
                doc_frequency = self.doc_frequencies.get(token, 0)
                idf = math.log(1 + (len(self.documents) - doc_frequency + 0.5) / (doc_frequency + 0.5))
                denominator = frequency + self.k1 * (
                    1 - self.b + self.b * self.doc_lengths[index] / (self.avg_doc_length or 1)
                )
                score += idf * (frequency * (self.k1 + 1)) / denominator

            phrase_bonus = _phrase_bonus(query, self.documents[index])
            raw_scores[self.documents[index].doc_id] = score + phrase_bonus

        max_score = max(raw_scores.values(), default=0.0)
        return {doc_id: normalize_score(score, max_score) for doc_id, score in raw_scores.items()}

    def _build_doc_frequencies(self) -> dict[str, int]:
        frequencies: dict[str, int] = {}
        for tokens in self.doc_tokens:
            for token in set(tokens):
                frequencies[token] = frequencies.get(token, 0) + 1
        return frequencies


def _phrase_bonus(query: str, document: RetrievalDocument) -> float:
    query_tokens = set(tokenize(query))
    title_tokens = set(tokenize(document.title))
    normalized_query = " ".join(tokenize(query))
    normalized_title = " ".join(tokenize(document.title))
    normalized_text = " ".join(tokenize(document.searchable_text))

    bonus = 0.0
    if query_tokens and title_tokens:
        bonus += 0.8 * (len(query_tokens & title_tokens) / len(query_tokens))
    if normalized_query and normalized_query in normalized_title:
        bonus += 1.0
    elif normalized_query and normalized_query in normalized_text:
        bonus += 0.35
    return bonus
