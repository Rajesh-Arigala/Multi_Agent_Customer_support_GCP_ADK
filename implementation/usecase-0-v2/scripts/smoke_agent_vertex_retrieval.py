from __future__ import annotations

from backend.factory import build_support_orchestrator
from backend.storage import CsvStore


def main() -> None:
    store = CsvStore("/tmp/usecase0-v2-agent-vertex-smoke")
    store.append_row("users", {"user_id": "guest", "name": "Guest User", "email": "guest@example.com"})
    orchestrator = build_support_orchestrator(store)

    queries = [
        "Can Dr Madhu help with PCOS and endometriosis?",
        "Do you provide IVF and ICSI treatment?",
        "I want fertility preservation options",
    ]
    for query in queries:
        response = orchestrator.handle_message(query, user_id="guest", session_id="vertex-smoke")
        retrieval = response.get("data", {}).get("retrieval", {})
        print(
            f"{response['agent']} | {query} | "
            f"{response.get('data', {}).get('faq_id', '')} | "
            f"mode={retrieval.get('mode')} | "
            f"score={retrieval.get('score')} | "
            f"{response['message'].splitlines()[0][:120]}"
        )


if __name__ == "__main__":
    main()
