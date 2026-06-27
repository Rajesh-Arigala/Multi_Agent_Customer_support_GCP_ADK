from __future__ import annotations

from pathlib import Path

from backend.config import EMBEDDING_MODEL_NAME, LOCATION, PROJECT_ID
from backend.retrieval import HybridRetriever, load_jsonl_documents
from backend.retrieval.embedding_store import load_embedding_records
from backend.retrieval.vertex_embeddings import VertexTextEmbeddingModel


BASE_DIR = Path(__file__).resolve().parents[1]
CORPUS_PATH = BASE_DIR / "rag_pipeline/drmadhupatil_corpus/06_output_rag_documents_ready/drmadhupatil_rag_corpus.jsonl"
EMBEDDINGS_PATH = BASE_DIR / "rag_pipeline/drmadhupatil_corpus/08_output_vertex_embeddings/drmadhupatil_vertex_embeddings.jsonl"


def main() -> None:
    documents = load_jsonl_documents(CORPUS_PATH)
    document_vectors = load_embedding_records(EMBEDDINGS_PATH)
    missing = [document.doc_id for document in documents if document.doc_id not in document_vectors]
    if missing:
        raise SystemExit(f"Missing embeddings for: {', '.join(missing)}")

    embedding_model = VertexTextEmbeddingModel(PROJECT_ID, LOCATION, EMBEDDING_MODEL_NAME)
    retriever = HybridRetriever(
        documents,
        embedding_model=embedding_model,
        document_vectors=document_vectors,
    )

    print(f"documents={len(documents)}")
    print(f"embedding_model={EMBEDDING_MODEL_NAME}")
    print(f"vector_backend={retriever.vector.backend}")

    queries = [
        "Do you provide IVF and ICSI treatment?",
        "Can Dr Madhu help with PCOS and endometriosis?",
        "I want fertility preservation options",
        "I have hormonal issues and irregular periods. Can the clinic help?",
    ]

    for query in queries:
        result = retriever.best_match(query, filters={"domain": "drmadhupatil.com"})
        if result is None:
            print(f"MISS | {query}")
            continue
        print(
            "HIT | "
            f"{query} | "
            f"{result.document.doc_id} | "
            f"score={result.score:.3f} | "
            f"keyword={result.keyword_score:.3f} | "
            f"vector={result.vector_score:.3f} | "
            f"{result.document.title}"
        )


if __name__ == "__main__":
    main()
