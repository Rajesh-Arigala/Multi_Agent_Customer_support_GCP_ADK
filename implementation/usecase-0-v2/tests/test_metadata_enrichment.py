import json
from pathlib import Path

from backend.retrieval import HybridRetriever, infer_metadata_filters, load_jsonl_documents
from backend.retrieval.metadata import enrich_document_row


ENRICHED_CORPUS_PATH = (
    Path(__file__).resolve().parents[1]
    / "rag_pipeline"
    / "drmadhupatil_corpus"
    / "07_output_enriched_documents"
    / "drmadhupatil_enriched_rag_corpus.jsonl"
)


def test_enrich_document_row_adds_business_metadata_for_pcos_page():
    row = {
        "doc_id": "WEB-DRMADHU-006",
        "source_type": "website",
        "usecase": "doctor_appointment",
        "domain": "drmadhupatil.com",
        "page_id": "service5",
        "title": "Endometriosis & PCOS - Advanced Fertility Care",
        "url": "https://drmadhupatil.com/service5",
        "content": "PCOS and endometriosis care.",
        "metadata": {"status": "active"},
    }

    enriched = enrich_document_row(row)
    metadata = enriched["metadata"]

    assert metadata["page_type"] == "service"
    assert metadata["service_name"] == "Endometriosis & PCOS"
    assert metadata["specialty"] == "gynecology"
    assert "pcos" in metadata["conditions"]
    assert metadata["appointment_eligible"] is True
    assert metadata["metadata_version"] == "v1_business_rules"


def test_enriched_corpus_has_required_filter_metadata():
    rows = [json.loads(line) for line in ENRICHED_CORPUS_PATH.read_text(encoding="utf-8").splitlines() if line.strip()]

    assert len(rows) == 8
    for row in rows:
        metadata = row["metadata"]
        for key in [
            "page_type",
            "service_name",
            "specialty",
            "conditions",
            "treatments",
            "intent",
            "appointment_eligible",
            "source_priority",
            "metadata_version",
        ]:
            assert key in metadata


def test_infer_metadata_filters_for_condition_query():
    filters = infer_metadata_filters("Can I book an appointment for PCOS and endometriosis?")

    assert filters["conditions"] == ["endometriosis", "pcos"]
    assert filters["appointment_eligible"] is True


def test_hybrid_retriever_filters_list_metadata_values():
    documents = load_jsonl_documents(ENRICHED_CORPUS_PATH)
    retriever = HybridRetriever(documents)

    result = retriever.best_match("Can Dr Madhu help with PCOS?", filters={"conditions": "pcos"})

    assert result is not None
    assert result.document.doc_id == "WEB-DRMADHU-006"
    assert "pcos" in result.document.metadata["conditions"]


def test_hybrid_retriever_filters_treatment_and_appointment():
    documents = load_jsonl_documents(ENRICHED_CORPUS_PATH)
    retriever = HybridRetriever(documents)

    result = retriever.best_match(
        "book IVF consultation",
        filters={"treatments": "ivf", "appointment_eligible": True},
    )

    assert result is not None
    assert result.document.doc_id == "WEB-DRMADHU-003"
    assert "ivf" in result.document.metadata["treatments"]
