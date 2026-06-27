from __future__ import annotations

from backend.retrieval.models import RetrievalDocument
from backend.retrieval.text import tokenize, tokenize_with_ngrams


SERVICE_TERMS_BY_PAGE_ID = {
    "service1": {"fertility assessment", "assessment", "fertility testing", "semen analysis", "ovulation"},
    "service2": {"ivf", "icsi", "ivf icsi", "embryo", "blastocyst", "fertilization"},
    "service3": {"iui", "insemination", "intrauterine insemination"},
    "service4": {"fertility preservation", "egg freezing", "sperm freezing", "embryo freezing", "preservation"},
    "service5": {"pcos", "endometriosis", "irregular periods", "hormonal", "hormonal issues"},
    "service6": {"immunotherapy", "recurrent miscarriage", "infertility", "immune"},
}

SERVICE_INTENT_TERMS = set().union(*SERVICE_TERMS_BY_PAGE_ID.values())
HOMEPAGE_PAGE_IDS = {"00_Homepage", "homepage", "home"}


def apply_service_ranking_policy(query: str, document: RetrievalDocument, score: float) -> float:
    query_terms = set(tokenize_with_ngrams(query, max_n=3))
    if not query_terms or not query_terms.intersection(SERVICE_INTENT_TERMS):
        return score

    page_id = str(document.metadata.get("page_id", ""))
    adjusted_score = score

    service_terms = SERVICE_TERMS_BY_PAGE_ID.get(page_id, set())
    matched_service_terms = query_terms.intersection(service_terms)
    if matched_service_terms:
        adjusted_score += min(0.22, 0.12 + 0.05 * len(matched_service_terms))

    if page_id in HOMEPAGE_PAGE_IDS:
        adjusted_score -= _homepage_dampening(query_terms, document)

    return max(min(adjusted_score, 1.0), 0.0)


def _homepage_dampening(query_terms: set[str], document: RetrievalDocument) -> float:
    title_terms = set(tokenize(document.title))
    if query_terms.intersection(title_terms):
        return 0.08
    return 0.18
