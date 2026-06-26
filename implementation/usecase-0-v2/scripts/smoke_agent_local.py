from backend.factory import build_support_orchestrator
from backend.storage import CsvStore


def main() -> None:
    store = CsvStore("data/local_smoke")
    store.append_row(
        "faq",
        {
            "faq_id": "FAQ-001",
            "category": "account",
            "question": "How do I reset my password?",
            "answer": "Use Settings > Account > Reset Password.",
            "tags": "password,account",
            "status": "active",
        },
    )
    store.append_row("users", {"user_id": "guest", "name": "Guest User", "email": "guest@example.com"})

    orchestrator = build_support_orchestrator(store)
    for message in [
        "How do I reset my password?",
        "Create a ticket for a billing issue",
        "This is urgent and I am frustrated",
    ]:
        response = orchestrator.handle_message(message, user_id="guest", session_id="local-smoke")
        print(response["agent"], "-", response["message"])


if __name__ == "__main__":
    main()

