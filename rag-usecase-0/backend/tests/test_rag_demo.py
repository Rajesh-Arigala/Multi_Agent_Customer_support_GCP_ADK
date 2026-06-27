from pathlib import Path

from app.config import CORPUS_PATH, METADATA_MANIFEST_PATH
from app.rag.loader import load_documents, load_manifest
from app.rag.retriever import infer_filters, matches_filters


def test_demo_artifacts_exist():
    assert CORPUS_PATH.exists()
    assert METADATA_MANIFEST_PATH.exists()


def test_loads_approved_documents():
    documents = load_documents(CORPUS_PATH)
    assert len(documents) == 8
    assert any(document.doc_id == "WEB-DRMADHU-006" for document in documents)


def test_metadata_manifest_is_present():
    manifest = load_manifest(METADATA_MANIFEST_PATH)
    assert manifest["document_count"] == 8
    assert manifest["metadata_version"] == "v1_business_rules"


def test_pcos_filter_matches_service_page():
    documents = load_documents(CORPUS_PATH)
    filters = infer_filters("Can Dr Madhu help with PCOS and endometriosis?")
    matches = [document.doc_id for document in documents if matches_filters(document, filters)]
    assert "WEB-DRMADHU-006" in matches
