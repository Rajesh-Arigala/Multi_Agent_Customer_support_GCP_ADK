from __future__ import annotations

from backend.api.app import create_app
from backend.storage import CsvStore


def main() -> None:
    try:
        from fastapi.testclient import TestClient
    except ImportError as exc:
        raise SystemExit("FastAPI test client is not installed. Run: pip install -r requirements-api.txt") from exc

    app = create_app(CsvStore("/tmp/usecase0-v2-api-smoke"))
    client = TestClient(app)

    health = client.get("/health")
    print("health", health.status_code, health.json()["status"])

    metadata = client.get("/metadata/status")
    metadata_payload = metadata.json()
    print("metadata", metadata.status_code, metadata_payload["status"], metadata_payload["document_count"])

    chat = client.post(
        "/chat",
        json={
            "message": "Can Dr Madhu help with PCOS and endometriosis?",
            "user_id": "guest",
            "session_id": "api-smoke",
        },
    )
    chat_payload = chat.json()
    retrieval = chat_payload.get("data", {}).get("retrieval", {})
    print("chat", chat.status_code, chat_payload.get("agent"), chat_payload.get("data", {}).get("faq_id"), retrieval.get("mode"))

    smoke = client.get("/retrieval/smoke")
    print("retrieval_smoke", smoke.status_code, len(smoke.json()["results"]))


if __name__ == "__main__":
    main()
