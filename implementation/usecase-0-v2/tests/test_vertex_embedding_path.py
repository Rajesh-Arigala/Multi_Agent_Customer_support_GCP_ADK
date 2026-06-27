from backend.retrieval import HybridRetriever
from backend.retrieval.embedding_store import load_embedding_records, save_embedding_records
from backend.retrieval.models import RetrievalDocument


class FakeEmbeddingModel:
    def embed(self, text: str) -> list[float]:
        normalized = text.lower()
        if "ivf" in normalized or "icsi" in normalized:
            return [1.0, 0.0, 0.0]
        if "pcos" in normalized or "endometriosis" in normalized:
            return [0.0, 1.0, 0.0]
        return [0.0, 0.0, 1.0]


def test_hybrid_retriever_uses_precomputed_vectors():
    documents = [
        RetrievalDocument("DOC-IVF", "website", "IVF Treatment", "IVF and ICSI support"),
        RetrievalDocument("DOC-PCOS", "website", "PCOS Care", "Endometriosis and PCOS support"),
    ]
    document_vectors = {
        "DOC-IVF": [1.0, 0.0, 0.0],
        "DOC-PCOS": [0.0, 1.0, 0.0],
    }
    retriever = HybridRetriever(
        documents,
        embedding_model=FakeEmbeddingModel(),
        document_vectors=document_vectors,
    )

    result = retriever.best_match("hormonal PCOS issue")

    assert result is not None
    assert result.document.doc_id == "DOC-PCOS"
    assert result.vector_score > 0.9


def test_embedding_store_round_trip(tmp_path):
    documents = [RetrievalDocument("DOC-1", "website", "Title", "Content")]
    path = tmp_path / "embeddings.jsonl"

    save_embedding_records(
        path,
        documents,
        [[0.1, 0.2, 0.3]],
        "text-embedding-005",
        "multi-agent-adk-1",
        "us-central1",
    )

    loaded = load_embedding_records(path)

    assert loaded == {"DOC-1": [0.1, 0.2, 0.3]}
