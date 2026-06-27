from __future__ import annotations

from backend.retrieval.text import tokenize_with_ngrams

CONDITION_TERMS = {
    "pcos": "pcos",
    "endometriosis": "endometriosis",
    "irregular periods": "irregular periods",
    "hormonal": "hormonal issues",
    "hormonal issues": "hormonal issues",
    "pelvic pain": "pelvic pain",
    "recurrent miscarriage": "recurrent miscarriage",
    "recurrent implantation failure": "recurrent implantation failure",
}

TREATMENT_TERMS = {
    "ivf": "ivf",
    "icsi": "icsi",
    "iui": "iui",
    "fertility preservation": "fertility preservation",
    "egg freezing": "egg freezing",
    "sperm freezing": "sperm freezing",
    "embryo freezing": "embryo freezing",
    "fertility assessment": "fertility assessment",
    "fertility testing": "fertility testing",
    "semen analysis": "semen analysis",
    "immunotherapy": "immunotherapy",
}

APPOINTMENT_TERMS = {"appointment", "book", "consult", "consultation", "schedule", "visit"}


def infer_metadata_filters(query: str) -> dict[str, object]:
    terms = set(tokenize_with_ngrams(query, max_n=3))
    filters: dict[str, object] = {}

    conditions = sorted({value for term, value in CONDITION_TERMS.items() if term in terms})
    treatments = sorted({value for term, value in TREATMENT_TERMS.items() if term in terms})

    if conditions:
        filters["conditions"] = conditions
    if treatments:
        filters["treatments"] = treatments
    if terms.intersection(APPOINTMENT_TERMS):
        filters["appointment_eligible"] = True

    return filters
