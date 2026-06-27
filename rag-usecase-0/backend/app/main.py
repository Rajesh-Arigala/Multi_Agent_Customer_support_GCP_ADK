from __future__ import annotations

from functools import lru_cache
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.config import CORPUS_PATH, EMBEDDINGS_PATH, FRONTEND_DIR, METADATA_MANIFEST_PATH, RAG_USE_VERTEX
from app.rag.loader import load_documents, load_manifest, load_vectors
from app.rag.retriever import RagRetriever

app = FastAPI(title="RAG Usecase 0 Doctor Review", version="0.1.0")
if FRONTEND_DIR.exists():
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR), name="assets")

@lru_cache(maxsize=1)
def get_retriever() -> RagRetriever:
    return RagRetriever(load_documents(CORPUS_PATH), load_vectors(EMBEDDINGS_PATH), EMBEDDINGS_PATH, use_vertex=RAG_USE_VERTEX)

@app.get("/", response_class=HTMLResponse)
def root():
    index = FRONTEND_DIR / "index.html"
    if index.exists():
        return FileResponse(index)
    return HTMLResponse("<h1>RAG Usecase 0</h1>")

@app.get("/review", response_class=HTMLResponse)
def review():
    return root()

@app.get("/health")
def health() -> dict[str, Any]:
    return {"status": "ok", "service": "rag-usecase-0", "use_vertex": RAG_USE_VERTEX}

@app.get("/metadata/status")
def metadata_status() -> dict[str, Any]:
    manifest = load_manifest(METADATA_MANIFEST_PATH)
    return {"status": "ok" if CORPUS_PATH.exists() else "missing_corpus", "corpus_exists": CORPUS_PATH.exists(), "embeddings_exists": EMBEDDINGS_PATH.exists(), "document_count": manifest.get("document_count", len(load_documents(CORPUS_PATH)) if CORPUS_PATH.exists() else 0), "metadata_version": manifest.get("metadata_version", ""), "page_types": manifest.get("page_types", {}), "use_vertex": RAG_USE_VERTEX}

@app.post("/api/chat")
def chat(payload: dict[str, Any]) -> dict[str, Any]:
    question = str(payload.get("question") or payload.get("message") or "").strip()
    if not question:
        raise HTTPException(status_code=400, detail="question is required")
    result = get_retriever().answer(question)
    return {"question": question, **result}

@app.get("/api/smoke")
def smoke() -> dict[str, Any]:
    questions = ["Do you provide IVF and ICSI treatment?", "Can Dr Madhu help with PCOS and endometriosis?", "I want fertility preservation options"]
    retriever = get_retriever()
    results = []
    for question in questions:
        result = retriever.answer(question)
        retrieval = result.get("retrieval", {})
        results.append({"question": question, "doc_id": retrieval.get("doc_id"), "mode": retrieval.get("mode"), "score": retrieval.get("score")})
    return {"status": "ok", "results": results}
