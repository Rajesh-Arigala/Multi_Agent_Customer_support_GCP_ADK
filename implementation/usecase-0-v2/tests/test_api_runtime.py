from backend.api.runtime import build_runtime_store, health_payload, metadata_status, retrieval_smoke_queries
from backend.config import BASE_DIR, KNOWLEDGE_DIR
from backend.storage import CsvStore


def test_health_payload_contains_service_identity(monkeypatch):
    monkeypatch.setenv("STORAGE_BACKEND", "csv")

    payload = health_payload()

    assert payload["status"] == "ok"
    assert payload["service"] == "usecase-0-v2-backend-api"
    assert payload["storage_backend"] == "csv"


def test_metadata_status_reports_enriched_corpus():
    payload = metadata_status()

    assert payload["status"] == "ok"
    assert payload["corpus_exists"] is True
    assert payload["metadata_manifest_exists"] is True
    assert payload["document_count"] == 8
    assert payload["metadata_version"] == "v1_business_rules"
    assert payload["page_types"]["service"] == 6


def test_default_knowledge_dir_matches_import_destination():
    assert KNOWLEDGE_DIR == BASE_DIR / "backend" / "knowledge" / "latest"


def test_retrieval_smoke_queries_are_business_representative():
    queries = retrieval_smoke_queries()

    assert len(queries) == 3
    assert any("PCOS" in query for query in queries)
    assert any("IVF" in query for query in queries)


def test_build_runtime_store_defaults_to_csv(monkeypatch, tmp_path):
    monkeypatch.setenv("STORAGE_BACKEND", "csv")
    monkeypatch.setenv("DATA_DIR", str(tmp_path))

    store = build_runtime_store()

    assert isinstance(store, CsvStore)
    store.append_row("users", {"user_id": "guest", "name": "Guest"})
    assert store.find_by_id("users", "user_id", "guest")["name"] == "Guest"


def test_build_runtime_store_rejects_unknown_backend(monkeypatch):
    monkeypatch.setenv("STORAGE_BACKEND", "unknown")

    try:
        build_runtime_store()
    except ValueError as exc:
        assert "Unsupported STORAGE_BACKEND" in str(exc)
    else:
        raise AssertionError("Expected unsupported storage backend to raise ValueError")
