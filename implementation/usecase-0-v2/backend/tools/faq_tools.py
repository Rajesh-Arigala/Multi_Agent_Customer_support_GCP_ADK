from pathlib import Path
from typing import Any

from backend.retrieval import HybridRetriever, documents_from_faq_rows, load_jsonl_documents
from backend.storage import StorageService


DEFAULT_CORPUS_PATH = (
    Path(__file__).resolve().parents[2]
    / "rag_pipeline"
    / "drmadhupatil_corpus"
    / "06_output_rag_documents_ready"
    / "drmadhupatil_rag_corpus.jsonl"
)


class FaqTools:
    def __init__(self, store: StorageService, corpus_path: Path = DEFAULT_CORPUS_PATH):
        self.store = store
        self.corpus_path = corpus_path

    def retrieve_faq_answer(self, query: str) -> dict[str, Any]:
        faq_documents = documents_from_faq_rows(self.store.list_rows("faq"))
        documents = faq_documents or load_jsonl_documents(self.corpus_path)
        if not documents:
            return {"status": "not_found", "message": "No FAQ or website corpus is available."}

        retriever = HybridRetriever(documents)
        best = retriever.best_match(query)
        if best is None:
            return {
                "status": "not_found",
                "message": "No local knowledge-base answer met the confidence threshold.",
                "retrieval": {"threshold": retriever.confidence_threshold},
            }

        document = best.document
        answer = document.metadata.get("answer") or _website_answer(document.title, document.content, document.url)
        return {
            "status": "success",
            "faq_id": document.doc_id,
            "answer": answer,
            "source": document.source_type,
            "retrieval": best.to_dict(),
        }


def _website_answer(title: str, content: str, url: str) -> str:
    snippet = " ".join(content.split())
    if len(snippet) > 700:
        snippet = snippet[:700].rsplit(" ", 1)[0] + "..."
    if url:
        return f"{title}: {snippet}\n\nSource: {url}"
    return f"{title}: {snippet}"
