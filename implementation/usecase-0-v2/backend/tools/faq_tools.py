from pathlib import Path
from typing import Any

from backend.config import EMBEDDING_MODEL_NAME, KNOWLEDGE_DIR, LOCATION, PROJECT_ID
from backend.retrieval import HybridRetriever, documents_from_faq_rows, load_jsonl_documents
from backend.retrieval.answering import format_answer, not_sure_answer, retrieval_for_document, special_answer
from backend.retrieval.filters import infer_metadata_filters
from backend.retrieval.embedding_store import load_embedding_records
from backend.retrieval.vertex_embeddings import VertexTextEmbeddingModel
from backend.storage import StorageService


IMPORTED_CORPUS_PATH = KNOWLEDGE_DIR / "corpus.jsonl"
IMPORTED_EMBEDDINGS_PATH = KNOWLEDGE_DIR / "embeddings.jsonl"
IMPORTED_METADATA_MANIFEST_PATH = KNOWLEDGE_DIR / "metadata_manifest.json"

PIPELINE_CORPUS_PATH = (
    Path(__file__).resolve().parents[2]
    / "rag_pipeline"
    / "drmadhupatil_corpus"
    / "07_output_enriched_documents"
    / "drmadhupatil_enriched_rag_corpus.jsonl"
)
PIPELINE_EMBEDDINGS_PATH = (
    Path(__file__).resolve().parents[2]
    / "rag_pipeline"
    / "drmadhupatil_corpus"
    / "08_output_vertex_embeddings"
    / "drmadhupatil_vertex_embeddings.jsonl"
)
PIPELINE_METADATA_MANIFEST_PATH = (
    Path(__file__).resolve().parents[2]
    / "rag_pipeline"
    / "drmadhupatil_corpus"
    / "07_output_enriched_documents"
    / "metadata_enrichment_manifest.json"
)


def imported_knowledge_available() -> bool:
    return IMPORTED_CORPUS_PATH.exists() and IMPORTED_EMBEDDINGS_PATH.exists()


def default_corpus_path() -> Path:
    if imported_knowledge_available():
        return IMPORTED_CORPUS_PATH
    return PIPELINE_CORPUS_PATH


def default_embeddings_path() -> Path:
    if imported_knowledge_available():
        return IMPORTED_EMBEDDINGS_PATH
    return PIPELINE_EMBEDDINGS_PATH


def default_metadata_manifest_path() -> Path:
    if imported_knowledge_available() and IMPORTED_METADATA_MANIFEST_PATH.exists():
        return IMPORTED_METADATA_MANIFEST_PATH
    return PIPELINE_METADATA_MANIFEST_PATH


DEFAULT_CORPUS_PATH = default_corpus_path()
DEFAULT_EMBEDDINGS_PATH = default_embeddings_path()


class FaqTools:
    def __init__(
        self,
        store: StorageService,
        corpus_path: Path | None = None,
        embeddings_path: Path | None = None,
        embedding_model: Any | None = None,
        use_vertex_embeddings: bool = True,
    ):
        self.store = store
        self.corpus_path = corpus_path or default_corpus_path()
        self.embeddings_path = embeddings_path or default_embeddings_path()
        self.embedding_model = embedding_model
        self.use_vertex_embeddings = use_vertex_embeddings

    def retrieve_faq_answer(self, query: str) -> dict[str, Any]:
        faq_documents = documents_from_faq_rows(self.store.list_rows("faq"))
        documents = faq_documents or self._load_corpus_documents()
        using_faq_rows = bool(faq_documents)
        if not documents:
            return {"status": "not_found", "message": "No FAQ or website corpus is available."}

        if not using_faq_rows:
            answer = special_answer(query)
            if answer is not None:
                text, doc_id = answer
                document = _document_by_id(documents, doc_id)
                return {
                    "status": "success",
                    "faq_id": doc_id or "assistant",
                    "answer": text,
                    "source": document.source_type if document else "assistant",
                    "retrieval": retrieval_for_document(document, "faq_exact") if document else {},
                }

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
                "message": not_sure_answer(),
                "retrieval": {"threshold": retriever.confidence_threshold, "mode": retrieval_mode, "filter_mode": filter_mode, "filters": filters},
            }

        document = best.document
        answer = document.metadata.get("answer") if using_faq_rows else format_answer(document, query)
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


def _document_by_id(documents, doc_id: str):
    if not doc_id:
        return None
    for document in documents:
        if document.doc_id == doc_id:
            return document
    return None
