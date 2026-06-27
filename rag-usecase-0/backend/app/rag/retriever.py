from __future__ import annotations

from app.rag.embeddings import HashEmbeddingClient, VertexEmbeddingClient, cosine
from app.rag.loader import save_vectors
from app.rag.models import Document, RetrievalHit
from app.rag.text import terms, tokenize

CONDITION_TERMS = {"pcos": "pcos", "endometriosis": "endometriosis", "irregular periods": "irregular periods", "hormonal": "hormonal issues", "hormonal issues": "hormonal issues"}
TREATMENT_TERMS = {"ivf": "ivf", "icsi": "icsi", "iui": "iui", "fertility preservation": "fertility preservation", "egg freezing": "egg freezing", "sperm freezing": "sperm freezing", "embryo freezing": "embryo freezing", "fertility assessment": "fertility assessment", "immunotherapy": "immunotherapy"}
APPOINTMENT_TERMS = {"appointment", "book", "consult", "consultation", "schedule", "visit"}

class RagRetriever:
    def __init__(self, documents: list[Document], vectors: dict[str, list[float]], embeddings_path, use_vertex: bool = True):
        self.documents = documents
        self.use_vertex = use_vertex
        self.embedding_client = VertexEmbeddingClient() if use_vertex else HashEmbeddingClient()
        self.vectors = vectors
        missing = [document for document in documents if document.doc_id not in self.vectors]
        if missing:
            self.vectors.update(self.embedding_client.embed_documents(missing))
            save_vectors(embeddings_path, self.vectors)

    def answer(self, question: str) -> dict:
        hit = self.search(question)
        if hit is None:
            return {"status": "not_found", "answer": "I could not find a confident answer in the approved clinic knowledge base.", "retrieval": {}}
        return {"status": "success", "answer": format_answer(hit.document), "retrieval": hit_payload(hit)}

    def search(self, question: str) -> RetrievalHit | None:
        filters = infer_filters(question)
        hit = self._search(question, filters, "metadata" if filters else "none")
        if hit is not None:
            return hit
        if filters:
            return self._search(question, {}, "metadata_fallback_unfiltered")
        return None

    def _search(self, question: str, filters: dict[str, object], filter_mode: str) -> RetrievalHit | None:
        query_terms = terms(question)
        query_vector = self.embedding_client.embed_query(question)
        best = None
        for document in [doc for doc in self.documents if matches_filters(doc, filters)]:
            keyword_score = keyword_overlap(query_terms, document)
            vector_score = cosine(query_vector, self.vectors.get(document.doc_id, []))
            score = min((0.55 * keyword_score) + (0.45 * vector_score) + title_boost(query_terms, document), 1.0)
            score = apply_service_boost(question, document, score)
            if score < 0.35:
                continue
            hit = RetrievalHit(document, score, keyword_score, vector_score, filter_mode, "hybrid_vertex" if self.use_vertex else "hybrid_hash")
            if best is None or hit.score > best.score:
                best = hit
        return best

def infer_filters(question: str) -> dict[str, object]:
    query_terms = terms(question)
    filters = {}
    conditions = sorted({value for term, value in CONDITION_TERMS.items() if term in query_terms})
    treatments = sorted({value for term, value in TREATMENT_TERMS.items() if term in query_terms})
    if conditions:
        filters["conditions"] = conditions
    if treatments:
        filters["treatments"] = treatments
    if query_terms.intersection(APPOINTMENT_TERMS):
        filters["appointment_eligible"] = True
    return filters

def matches_filters(document: Document, filters: dict[str, object]) -> bool:
    return all(value_matches(document.metadata.get(key), expected) for key, expected in filters.items())

def value_matches(candidate, expected) -> bool:
    if isinstance(expected, (list, tuple, set)):
        return any(value_matches(candidate, item) for item in expected)
    if isinstance(candidate, (list, tuple, set)):
        return any(str(item).lower() == str(expected).lower() for item in candidate)
    return str(candidate).lower() == str(expected).lower()

def keyword_overlap(query_terms: set[str], document: Document) -> float:
    document_terms = terms(document.searchable_text)
    return len(query_terms.intersection(document_terms)) / len(query_terms) if query_terms else 0.0

def title_boost(query_terms: set[str], document: Document) -> float:
    title_terms = set(tokenize(document.title))
    return 0.25 * (len(query_terms.intersection(title_terms)) / len(query_terms)) if query_terms else 0.0

def apply_service_boost(question: str, document: Document, score: float) -> float:
    query_terms = terms(question)
    service_terms = set(document.metadata.get("conditions", [])).union(set(document.metadata.get("treatments", [])))
    if query_terms.intersection(service_terms) and document.metadata.get("page_type") == "service":
        score += 0.12
    if document.metadata.get("page_type") == "homepage" and query_terms.intersection(service_terms):
        score -= 0.12
    return max(min(score, 1.0), 0.0)

def format_answer(document: Document) -> str:
    snippet = " ".join(document.content.split())
    if len(snippet) > 900:
        snippet = snippet[:900].rsplit(" ", 1)[0] + "..."
    if document.url:
        return f"{document.title}: {snippet}\n\nSource: {document.url}"
    return f"{document.title}: {snippet}"

def hit_payload(hit: RetrievalHit) -> dict:
    return {"doc_id": hit.document.doc_id, "title": hit.document.title, "url": hit.document.url, "score": round(hit.score, 4), "keyword_score": round(hit.keyword_score, 4), "vector_score": round(hit.vector_score, 4), "mode": hit.mode, "filter_mode": hit.filter_mode, "metadata": hit.document.metadata}
