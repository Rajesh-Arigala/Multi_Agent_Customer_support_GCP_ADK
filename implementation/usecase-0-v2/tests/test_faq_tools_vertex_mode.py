import json

from backend.storage import CsvStore
import backend.tools.faq_tools as faq_tools
from backend.tools.faq_tools import FaqTools


class FakeEmbeddingModel:
    def embed(self, text: str) -> list[float]:
        normalized = text.lower()
        if "pcos" in normalized or "endometriosis" in normalized:
            return [0.0, 1.0, 0.0]
        return [1.0, 0.0, 0.0]


def write_corpus(path):
    docs = [
        {
            "doc_id": "WEB-001",
            "source_type": "website",
            "title": "Clinic Homepage",
            "url": "https://example.com",
            "content": "Dr Madhu provides fertility services including PCOS and endometriosis care.",
            "metadata": {"domain": "example.com", "page_id": "00_Homepage"},
        },
        {
            "doc_id": "WEB-006",
            "source_type": "website",
            "title": "Endometriosis & PCOS - Advanced Fertility Care",
            "url": "https://example.com/service5",
            "content": "Focused care for PCOS, endometriosis, hormonal issues, and irregular periods.",
            "metadata": {"domain": "example.com", "page_id": "service5"},
        },
    ]
    path.write_text("\n".join(json.dumps(doc) for doc in docs) + "\n", encoding="utf-8")


def write_embeddings(path):
    rows = [
        {"doc_id": "WEB-001", "vector": [1.0, 0.0, 0.0]},
        {"doc_id": "WEB-006", "vector": [0.0, 1.0, 0.0]},
    ]
    path.write_text("\n".join(json.dumps(row) for row in rows) + "\n", encoding="utf-8")


def test_faq_tools_uses_vertex_artifact_when_available(tmp_path):
    corpus_path = tmp_path / "corpus.jsonl"
    embeddings_path = tmp_path / "embeddings.jsonl"
    write_corpus(corpus_path)
    write_embeddings(embeddings_path)
    tool = FaqTools(
        CsvStore(tmp_path / "store"),
        corpus_path=corpus_path,
        embeddings_path=embeddings_path,
        embedding_model=FakeEmbeddingModel(),
    )

    result = tool.retrieve_faq_answer("Can Dr Madhu help with PCOS and endometriosis?")

    assert result["status"] == "success"
    assert result["faq_id"] == "WEB-006"
    assert result["retrieval"]["mode"] == "hybrid_vertex"
    assert "Dr. Madhu Patil’s Clinic" in result["answer"]
    assert "Headings:" not in result["answer"]
    assert len(result["answer"].splitlines()) <= 4


def test_faq_tools_defaults_to_imported_knowledge_bundle_when_complete(tmp_path, monkeypatch):
    imported_dir = tmp_path / "knowledge" / "latest"
    imported_dir.mkdir(parents=True)
    corpus_path = imported_dir / "corpus.jsonl"
    embeddings_path = imported_dir / "embeddings.jsonl"
    write_corpus(corpus_path)
    write_embeddings(embeddings_path)
    monkeypatch.setattr(faq_tools, "IMPORTED_CORPUS_PATH", corpus_path)
    monkeypatch.setattr(faq_tools, "IMPORTED_EMBEDDINGS_PATH", embeddings_path)

    tool = FaqTools(
        CsvStore(tmp_path / "store"),
        embedding_model=FakeEmbeddingModel(),
    )

    result = tool.retrieve_faq_answer("Can Dr Madhu help with PCOS and endometriosis?")

    assert tool.corpus_path == corpus_path
    assert tool.embeddings_path == embeddings_path
    assert result["status"] == "success"
    assert result["faq_id"] == "WEB-006"
    assert result["retrieval"]["mode"] == "hybrid_vertex"


def test_faq_tools_handles_greeting_without_raw_retrieval(tmp_path):
    corpus_path = tmp_path / "corpus.jsonl"
    embeddings_path = tmp_path / "embeddings.jsonl"
    write_corpus(corpus_path)
    write_embeddings(embeddings_path)
    tool = FaqTools(
        CsvStore(tmp_path / "store"),
        corpus_path=corpus_path,
        embeddings_path=embeddings_path,
        embedding_model=FakeEmbeddingModel(),
    )

    result = tool.retrieve_faq_answer("hi")

    assert result["status"] == "success"
    assert result["faq_id"] == "assistant"
    assert "Hello" in result["answer"]
    assert len(result["answer"].splitlines()) <= 4


def test_faq_tools_uses_exact_patient_faq_answer(tmp_path):
    corpus_path = tmp_path / "corpus.jsonl"
    embeddings_path = tmp_path / "embeddings.jsonl"
    write_corpus(corpus_path)
    write_embeddings(embeddings_path)
    tool = FaqTools(
        CsvStore(tmp_path / "store"),
        corpus_path=corpus_path,
        embeddings_path=embeddings_path,
        embedding_model=FakeEmbeddingModel(),
    )

    result = tool.retrieve_faq_answer("How successful is IVF?")

    assert result["status"] == "success"
    assert result["faq_id"] == "WEB-DRMADHU-001"
    assert "**IVF success**" in result["answer"]
    assert "website" not in result["answer"].lower()
    assert len(result["answer"].splitlines()) <= 4


def test_faq_tools_falls_back_when_embedding_artifact_missing(tmp_path):
    corpus_path = tmp_path / "corpus.jsonl"
    write_corpus(corpus_path)
    tool = FaqTools(
        CsvStore(tmp_path / "store"),
        corpus_path=corpus_path,
        embeddings_path=tmp_path / "missing.jsonl",
    )

    result = tool.retrieve_faq_answer("PCOS and endometriosis")

    assert result["status"] == "success"
    assert result["retrieval"]["mode"] == "hybrid_hash"


def test_faq_rows_override_website_corpus_and_vertex_mode(tmp_path):
    store = CsvStore(tmp_path / "store")
    store.append_row(
        "faq",
        {
            "faq_id": "FAQ-001",
            "question": "How do I reset my password?",
            "answer": "Use Settings > Account > Reset Password.",
            "tags": "password,account",
            "status": "active",
        },
    )
    tool = FaqTools(
        store,
        corpus_path=tmp_path / "missing_corpus.jsonl",
        embeddings_path=tmp_path / "missing_embeddings.jsonl",
    )

    result = tool.retrieve_faq_answer("reset password")

    assert result["status"] == "success"
    assert result["faq_id"] == "FAQ-001"
    assert result["retrieval"]["mode"] == "hybrid_hash"
