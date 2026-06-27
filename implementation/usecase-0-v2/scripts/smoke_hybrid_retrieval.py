from pathlib import Path

from backend.retrieval import HybridRetriever, load_jsonl_documents


CORPUS_PATH = (
    Path(__file__).resolve().parents[1]
    / "rag_pipeline"
    / "drmadhupatil_corpus"
    / "07_output_enriched_documents"
    / "drmadhupatil_enriched_rag_corpus.jsonl"
)


def main() -> None:
    documents = load_jsonl_documents(CORPUS_PATH)
    retriever = HybridRetriever(documents)
    print(f"documents={len(documents)}")
    print(f"vector_backend={retriever.vector.backend}")

    queries = [
        "Do you provide IVF and ICSI treatment?",
        "Can Dr Madhu help with PCOS and endometriosis?",
        "I want fertility preservation options",
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
