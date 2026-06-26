from backend.factory import build_support_orchestrator
from backend.storage import CsvStore


def seed_store(tmp_path):
    store = CsvStore(tmp_path)
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
    return store


def test_faq_routes_to_triage_agent(tmp_path):
    orchestrator = build_support_orchestrator(seed_store(tmp_path))

    response = orchestrator.handle_message("How do I reset my password?", user_id="guest", session_id="s1")

    assert response["agent"] == "triage_agent"
    assert response["status"] == "success"
    assert "Reset Password" in response["message"]


def test_ticket_create_and_status_routes_to_ticket_agent(tmp_path):
    store = seed_store(tmp_path)
    orchestrator = build_support_orchestrator(store)

    created = orchestrator.handle_message("Create a ticket for a billing issue", user_id="guest", session_id="s1")
    ticket_id = created["data"]["ticket_id"]
    status = orchestrator.handle_message(f"Check {ticket_id}", user_id="guest", session_id="s1")

    assert created["agent"] == "ticket_agent"
    assert status["agent"] == "ticket_agent"
    assert status["data"]["ticket"]["ticket_id"] == ticket_id


def test_urgent_message_creates_ticket_and_escalation(tmp_path):
    store = seed_store(tmp_path)
    orchestrator = build_support_orchestrator(store)

    response = orchestrator.handle_message("This is urgent and I am frustrated", user_id="guest", session_id="s1")

    assert response["agent"] == "escalation_agent"
    assert response["data"]["escalation_id"].startswith("ESC-")
    assert store.list_rows("escalations")
    assert store.list_rows("audit_logs")


def test_memory_saves_ticket_fact(tmp_path):
    store = seed_store(tmp_path)
    orchestrator = build_support_orchestrator(store)

    orchestrator.handle_message("Create a ticket for a login problem", user_id="guest", session_id="s1")
    response = orchestrator.handle_message("Do you remember anything?", user_id="guest", session_id="s1")

    assert response["memory"]["loaded"]

