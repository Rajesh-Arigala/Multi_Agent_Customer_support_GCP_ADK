from __future__ import annotations

from copy import deepcopy
from urllib.parse import urlparse


SERVICE_METADATA_BY_PAGE_ID: dict[str, dict[str, object]] = {
    "00_Homepage": {
        "page_type": "homepage",
        "service_slug": "",
        "service_name": "Clinic Homepage",
        "specialty": "fertility",
        "conditions": ["infertility", "pcos", "endometriosis"],
        "treatments": ["ivf", "icsi", "iui", "fertility assessment", "fertility preservation"],
        "intent": ["informational", "appointment"],
        "appointment_eligible": True,
        "emergency_related": False,
        "source_priority": "medium",
    },
    "service1": {
        "page_type": "service",
        "service_slug": "service1",
        "service_name": "Fertility Assessment",
        "specialty": "fertility",
        "conditions": ["infertility", "ovulation issues", "male infertility"],
        "treatments": ["fertility assessment", "fertility testing", "semen analysis", "ovarian reserve test"],
        "intent": ["informational", "appointment", "eligibility"],
        "appointment_eligible": True,
        "emergency_related": False,
        "source_priority": "high",
    },
    "service2": {
        "page_type": "service",
        "service_slug": "service2",
        "service_name": "IVF & ICSI Treatments",
        "specialty": "fertility",
        "conditions": ["infertility", "male infertility", "female infertility"],
        "treatments": ["ivf", "icsi", "embryo transfer", "blastocyst culture", "fertilization"],
        "intent": ["informational", "appointment", "treatment"],
        "appointment_eligible": True,
        "emergency_related": False,
        "source_priority": "high",
    },
    "service3": {
        "page_type": "service",
        "service_slug": "service3",
        "service_name": "IUI Treatment",
        "specialty": "fertility",
        "conditions": ["infertility", "mild male factor infertility", "ovulation issues"],
        "treatments": ["iui", "intrauterine insemination", "insemination"],
        "intent": ["informational", "appointment", "treatment"],
        "appointment_eligible": True,
        "emergency_related": False,
        "source_priority": "high",
    },
    "service4": {
        "page_type": "service",
        "service_slug": "service4",
        "service_name": "Fertility Preservation",
        "specialty": "fertility",
        "conditions": ["fertility preservation need", "cancer treatment", "delayed pregnancy"],
        "treatments": ["fertility preservation", "egg freezing", "sperm freezing", "embryo freezing"],
        "intent": ["informational", "appointment", "treatment"],
        "appointment_eligible": True,
        "emergency_related": False,
        "source_priority": "high",
    },
    "service5": {
        "page_type": "service",
        "service_slug": "service5",
        "service_name": "Endometriosis & PCOS",
        "specialty": "gynecology",
        "conditions": ["pcos", "endometriosis", "irregular periods", "hormonal issues", "pelvic pain"],
        "treatments": ["pcos care", "endometriosis care", "hormonal evaluation"],
        "intent": ["informational", "appointment", "condition_care"],
        "appointment_eligible": True,
        "emergency_related": False,
        "source_priority": "high",
    },
    "service6": {
        "page_type": "service",
        "service_slug": "service6",
        "service_name": "Immunotherapy in Infertility",
        "specialty": "fertility",
        "conditions": ["recurrent miscarriage", "recurrent implantation failure", "immune factors", "infertility"],
        "treatments": ["immunotherapy", "intralipid", "ivig", "heparin", "aspirin"],
        "intent": ["informational", "appointment", "treatment"],
        "appointment_eligible": True,
        "emergency_related": False,
        "source_priority": "high",
    },
    "blog": {
        "page_type": "blog",
        "service_slug": "",
        "service_name": "Blog",
        "specialty": "fertility",
        "conditions": [],
        "treatments": [],
        "intent": ["informational"],
        "appointment_eligible": False,
        "emergency_related": False,
        "source_priority": "low",
    },
}


def enrich_document_row(row: dict) -> dict:
    enriched = deepcopy(row)
    metadata = dict(enriched.get("metadata", {}))
    page_id = enriched.get("page_id") or metadata.get("page_id") or _page_id_from_url(enriched.get("url", ""))
    base = SERVICE_METADATA_BY_PAGE_ID.get(str(page_id), _default_metadata(enriched))

    metadata.update(base)
    metadata["page_id"] = str(page_id)
    metadata.setdefault("usecase", enriched.get("usecase", ""))
    metadata.setdefault("domain", enriched.get("domain", ""))
    metadata["metadata_version"] = "v1_business_rules"

    enriched["metadata"] = metadata
    enriched["metadata_version"] = metadata["metadata_version"]
    return enriched


def _page_id_from_url(url: str) -> str:
    path = urlparse(url).path.strip("/")
    if not path:
        return "00_Homepage"
    return path.split("/")[-1]


def _default_metadata(row: dict) -> dict[str, object]:
    return {
        "page_type": "website",
        "service_slug": "",
        "service_name": row.get("title", ""),
        "specialty": "fertility",
        "conditions": [],
        "treatments": [],
        "intent": ["informational"],
        "appointment_eligible": False,
        "emergency_related": False,
        "source_priority": "medium",
    }
