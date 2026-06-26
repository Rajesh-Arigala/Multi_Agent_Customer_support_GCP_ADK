from support_agent.orchestrator import SupportOrchestrator
from support_agent.storage import JsonStore
from support_agent.tools import SupportTools


def seed_store(tmp_path):
    store = JsonStore(tmp_path)
    store.write("faq", [{"keyword": "password", "aliases": [], "answer": "Reset password answer."}])
    store.write("tickets", {"_counter": 1, "items": {}})
    store.write("users", {"guest": {"name": "Guest", "email": "guest@example.com", "company": "Example"}})
    store.write("escalations", {"items": {}})
    return store


def test_faq_lookup_and_ticket_lifecycle(tmp_path):
    tools = SupportTools(seed_store(tmp_path))

    assert tools.get_faq_answer("password help")["status"] == "success"
    created = tools.create_ticket("guest", "Cannot log in", "high")
    ticket_id = created["ticket_id"]

    assert ticket_id == "TKT-0001"
    assert tools.check_ticket_status(ticket_id)["ticket"]["status"] == "open"
    assert tools.update_ticket(ticket_id, "resolved", "Fixed")["status"] == "success"
    assert tools.check_ticket_status(ticket_id)["ticket"]["status"] == "resolved"


def test_urgent_message_creates_ticket_and_escalation(tmp_path):
    tools = SupportTools(seed_store(tmp_path))
    orchestrator = SupportOrchestrator(tools)

    response = orchestrator.handle_message("This is urgent and broken", user_id="guest", session_id="s1")

    assert response["agent"] == "escalation_agent"
    assert response["data"]["ticket"]["ticket_id"] == "TKT-0001"
    assert response["data"]["escalation_id"].startswith("ESC-")
