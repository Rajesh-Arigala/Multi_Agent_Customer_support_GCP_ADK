from pathlib import Path
from typing import Any

from backend.config import EMBEDDING_MODEL_NAME, LOCATION, PROJECT_ID
from backend.retrieval import HybridRetriever, documents_from_faq_rows, load_jsonl_documents
from backend.retrieval.filters import infer_metadata_filters
from backend.retrieval.embedding_store import load_embedding_records
from backend.retrieval.vertex_embeddings import VertexTextEmbeddingModel
from backend.storage import StorageService


DEFAULT_CORPUS_PATH = (
    Path(__file__).resolve().parents[2]
    / "rag_pipeline"
    / "drmadhupatil_corpus"
    / "07_output_enriched_documents"
    / "drmadhupatil_enriched_rag_corpus.jsonl"
)
DEFAULT_EMBEDDINGS_PATH = (
    Path(__file__).resolve().parents[2]
    / "rag_pipeline"
    / "drmadhupatil_corpus"
    / "08_output_vertex_embeddings"
    / "drmadhupatil_vertex_embeddings.jsonl"
)


class FaqTools:
    def __init__(
        self,
        store: StorageService,
        corpus_path: Path = DEFAULT_CORPUS_PATH,
        embeddings_path: Path = DEFAULT_EMBEDDINGS_PATH,
        embedding_model: Any | None = None,
        use_vertex_embeddings: bool = True,
    ):
        self.store = store
        self.corpus_path = corpus_path
        self.embeddings_path = embeddings_path
        self.embedding_model = embedding_model
        self.use_vertex_embeddings = use_vertex_embeddings

    def retrieve_faq_answer(self, query: str) -> dict[str, Any]:
        faq_documents = documents_from_faq_rows(self.store.list_rows("faq"))
        documents = faq_documents or self._load_corpus_documents()
        using_faq_rows = bool(faq_documents)
        if not documents:
            return {"status": "not_found", "message": "No FAQ or website corpus is available."}

        retriever, retrieval_mode = self._build_retriever(documents, using_faq_rows)
        filters = {} if using_faq_rows else infer_metadata_filters(query)
        best = retriever.best_match(query, filters=filters or None)
        filter_mode = "metadata" if filters else "none"
        if best is None and filters:
            best = retriever.best_match(query)
            filter_mode = "metadata_fallback_unfiltered" if best is not None else "metadata"
        if best is None:
            return {
                "status": "not_found",
                "message": "No local knowledge-base answer met the confidence threshold.",
                "retrieval": {"threshold": retriever.confidence_threshold, "mode": retrieval_mode, "filter_mode": filter_mode, "filters": filters},
            }

        document = best.document
        answer = document.metadata.get("answer") or _website_answer(document.title, document.content, document.url)
        payload = best.to_dict()
        payload["mode"] = retrieval_mode
        payload["filter_mode"] = filter_mode
        payload["filters"] = filters
        return {
            "status": "success",
            "faq_id": document.doc_id,
            "answer": answer,
            "source": document.source_type,
            "retrieval": payload,
        }

    def _load_corpus_documents(self):
        documents = load_jsonl_documents(self.corpus_path)
        if documents:
            return documents
        legacy_path = (
            Path(__file__).resolve().parents[2]
            / "rag_pipeline"
            / "drmadhupatil_corpus"
            / "06_output_rag_documents_ready"
            / "drmadhupatil_rag_corpus.jsonl"
        )
        return load_jsonl_documents(legacy_path)

    def _build_retriever(self, documents, using_faq_rows: bool) -> tuple[HybridRetriever, str]:
        if using_faq_rows or not self.use_vertex_embeddings or not self.embeddings_path.exists():
            return HybridRetriever(documents), "hybrid_hash"

        document_vectors = load_embedding_records(self.embeddings_path)
        if not _has_vectors_for_documents(documents, document_vectors):
            return HybridRetriever(documents), "hybrid_hash_missing_vectors"

        embedding_model = self.embedding_model or VertexTextEmbeddingModel(
            PROJECT_ID,
            LOCATION,
            EMBEDDING_MODEL_NAME,
        )
        return (
            HybridRetriever(
                documents,
                embedding_model=embedding_model,
                document_vectors=document_vectors,
            ),
            "hybrid_vertex",
        )


def _has_vectors_for_documents(documents, document_vectors: dict[str, list[float]]) -> bool:
    return all(document.doc_id in document_vectors for document in documents)


def _website_answer(title: str, content: str, url: str) -> str:
    snippet = " ".join(content.split())
    if len(snippet) > 700:
        snippet = snippet[:700].rsplit(" ", 1)[0] + "..."
    if url:
        return f"{title}: {snippet}\n\nSource: {url}"
    return f"{title}: {snippet}"
