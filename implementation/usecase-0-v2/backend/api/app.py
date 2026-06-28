from __future__ import annotations

from typing import Any

from backend.api.runtime import build_runtime_store, health_payload, metadata_status, retrieval_smoke_queries
from backend.config import BASE_DIR
from backend.factory import build_support_orchestrator
from backend.storage import StorageService

try:
    from fastapi import FastAPI, HTTPException
    from fastapi.responses import FileResponse
    from fastapi.staticfiles import StaticFiles
except ImportError:  # pragma: no cover - exercised in environments without API deps
    FastAPI = None
    FileResponse = None
    HTTPException = None
    StaticFiles = None


STATIC_DIR = BASE_DIR / "frontend" / "static"
INDEX_PATH = BASE_DIR / "frontend" / "index.html"


def create_app(store: StorageService | None = None):
    if FastAPI is None:
        raise RuntimeError("FastAPI is not installed. Run: pip install -r requirements-api.txt")

    runtime_store = store or build_runtime_store()
    orchestrator = build_support_orchestrator(runtime_store)
    app = FastAPI(title="Usecase 0 Multi-Agent Backend", version="0.1.0")

    if StaticFiles is not None and STATIC_DIR.exists():
        app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    @app.get("/", include_in_schema=False)
    def index():
        if FileResponse is None or not INDEX_PATH.exists():
            raise HTTPException(status_code=404, detail="frontend is not packaged")
        return FileResponse(INDEX_PATH)

    @app.get("/health")
    def health() -> dict[str, Any]:
        return health_payload()

    @app.get("/metadata/status")
    def metadata() -> dict[str, Any]:
        return metadata_status()

    @app.post("/chat")
    def chat(payload: dict[str, Any]) -> dict[str, Any]:
        message = str(payload.get("message", "")).strip()
        if not message:
            raise HTTPException(status_code=400, detail="message is required")
        user_id = str(payload.get("user_id", "guest") or "guest")
        session_id = str(payload.get("session_id", "default") or "default")
        return orchestrator.handle_message(message, user_id=user_id, session_id=session_id)

    @app.get("/retrieval/smoke")
    def retrieval_smoke() -> dict[str, Any]:
        results = []
        for query in retrieval_smoke_queries():
            response = orchestrator.handle_message(query, user_id="smoke", session_id="api-smoke")
            data = response.get("data", {})
            retrieval = data.get("retrieval", {})
            results.append(
                {
                    "query": query,
                    "agent": response.get("agent"),
                    "faq_id": data.get("faq_id", ""),
                    "mode": retrieval.get("mode", ""),
                    "filter_mode": retrieval.get("filter_mode", ""),
                    "score": retrieval.get("score"),
                    "title": retrieval.get("title", ""),
                }
            )
        return {"status": "ok", "results": results}

    return app


app = create_app() if FastAPI is not None else None
