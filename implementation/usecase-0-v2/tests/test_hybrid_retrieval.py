from pathlib import Path

from backend.retrieval import HybridRetriever, documents_from_faq_rows, load_jsonl_documents
from backend.retrieval.text import tokenize_with_ngrams


CORPUS_PATH = (
    Path(__file__).resolve().parents[1]
    / "rag_pipeline"
    / "drmadhupatil_corpus"
    / "07_output_enriched_documents"
    / "drmadhupatil_enriched_rag_corpus.jsonl"
)


def test_loads_drmadhupatil_rag_corpus():
    documents = load_jsonl_documents(CORPUS_PATH)

    assert len(documents) == 8
    assert {doc.metadata["domain"] for doc in documents} == {"drmadhupatil.com"}


def test_hybrid_retriever_finds_ivf_page():
    documents = load_jsonl_documents(CORPUS_PATH)
    retriever = HybridRetriever(documents)

    result = retriever.best_match("Do you provide IVF ICSI treatment?")

    assert result is not None
    assert result.document.doc_id == "WEB-DRMADHU-003"
    assert result.document.metadata["page_id"] == "service2"


def test_hybrid_retriever_applies_metadata_filter():
    documents = load_jsonl_documents(CORPUS_PATH)
    retriever = HybridRetriever(documents)

    result = retriever.best_match("PCOS treatment", filters={"domain": "wrong.example"})

    assert result is None


def test_documents_from_faq_rows_preserves_existing_faq_behavior():
    documents = documents_from_faq_rows(
        [
            {
                "faq_id": "FAQ-001",
                "category": "account",
                "question": "How do I reset my password?",
                "answer": "Use Settings > Account > Reset Password.",
                "tags": "password,account",
                "status": "active",
            }
        ]
    )
    retriever = HybridRetriever(documents)

    result = retriever.best_match("reset password")

    assert result is not None
    assert result.document.doc_id == "FAQ-001"


def test_tokenize_with_ngrams_adds_phrases():
    terms = tokenize_with_ngrams("fertility preservation options", max_n=3)

    assert "fertility" in terms
    assert "fertility preservation" in terms
    assert "fertility preservation options" in terms


def test_service_specific_query_prefers_service_page_over_homepage():
    documents = load_jsonl_documents(CORPUS_PATH)
    retriever = HybridRetriever(documents)

    result = retriever.best_match("Can Dr Madhu help with PCOS and endometriosis?")

    assert result is not None
    assert result.document.doc_id == "WEB-DRMADHU-006"
    assert result.document.metadata["page_id"] == "service5"
