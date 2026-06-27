from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from backend.config import EMBEDDING_MODEL_NAME, LOCATION, PROJECT_ID
from backend.retrieval.embedding_store import save_embedding_records, write_embedding_manifest
from backend.retrieval.loader import load_jsonl_documents
from backend.retrieval.vertex_embeddings import VertexTextEmbeddingModel
from backend.retrieval.vector import normalize_vector


BASE_DIR = Path(__file__).resolve().parents[1]
DEFAULT_CORPUS_PATH = BASE_DIR / "rag_pipeline/drmadhupatil_corpus/07_output_enriched_documents/drmadhupatil_enriched_rag_corpus.jsonl"
DEFAULT_OUTPUT_DIR = BASE_DIR / "rag_pipeline/drmadhupatil_corpus/08_output_vertex_embeddings"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build Vertex AI embeddings for the approved RAG corpus.")
    parser.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS_PATH)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--batch-size", type=int, default=8)
    parser.add_argument("--project-id", default=PROJECT_ID)
    parser.add_argument("--location", default=LOCATION)
    parser.add_argument("--model-name", default=EMBEDDING_MODEL_NAME)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    documents = load_jsonl_documents(args.corpus)
    if not documents:
        raise SystemExit(f"No documents found in {args.corpus}")

    model = VertexTextEmbeddingModel(
        project_id=args.project_id,
        location=args.location,
        model_name=args.model_name,
    )

    vectors: list[list[float]] = []
    for start in range(0, len(documents), args.batch_size):
        batch = documents[start:start + args.batch_size]
        texts = [document.searchable_text for document in batch]
        vectors.extend([normalize_vector(vector) for vector in model.embed_texts(texts, task_type="RETRIEVAL_DOCUMENT")])
        print(f"embedded {min(start + args.batch_size, len(documents))}/{len(documents)}")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    embeddings_path = args.output_dir / "drmadhupatil_vertex_embeddings.jsonl"
    manifest_path = args.output_dir / "embedding_manifest.json"
    faiss_index_path = args.output_dir / "drmadhupatil_vertex.faiss"
    faiss_ids_path = args.output_dir / "drmadhupatil_vertex_faiss_ids.json"

    save_embedding_records(
        embeddings_path,
        documents,
        vectors,
        args.model_name,
        args.project_id,
        args.location,
    )

    faiss_backend = _write_faiss_index(vectors, documents, faiss_index_path, faiss_ids_path)
    manifest = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "project_id": args.project_id,
        "location": args.location,
        "model_name": args.model_name,
        "corpus_path": str(args.corpus),
        "document_count": len(documents),
        "embedding_dimensions": len(vectors[0]) if vectors else 0,
        "embeddings_path": str(embeddings_path),
        "faiss_index_path": str(faiss_index_path) if faiss_backend else "",
        "faiss_ids_path": str(faiss_ids_path) if faiss_backend else "",
        "faiss_index_written": faiss_backend,
    }
    write_embedding_manifest(manifest_path, manifest)

    print("Vertex embeddings built")
    print(f"documents={len(documents)}")
    print(f"dimensions={manifest['embedding_dimensions']}")
    print(f"embeddings={embeddings_path}")
    print(f"manifest={manifest_path}")
    print(f"faiss_index_written={faiss_backend}")


def _write_faiss_index(vectors, documents, index_path: Path, ids_path: Path) -> bool:
    try:
        import faiss  # type: ignore
        import numpy as np  # type: ignore
    except Exception:
        return False

    matrix = np.array(vectors, dtype="float32")
    index = faiss.IndexFlatIP(matrix.shape[1])
    index.add(matrix)
    faiss.write_index(index, str(index_path))
    ids_path.write_text(
        json.dumps([document.doc_id for document in documents], indent=2) + "\n",
        encoding="utf-8",
    )
    return True


if __name__ == "__main__":
    main()
