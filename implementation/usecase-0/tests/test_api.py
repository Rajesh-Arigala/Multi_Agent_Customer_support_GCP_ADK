import app as app_module
from support_agent.orchestrator import SupportOrchestrator
from support_agent.storage import JsonStore
from support_agent.tools import SupportTools


def test_health_endpoint():
    client = app_module.app.test_client()
    response = client.get("/health")

    assert response.status_code == 200
    assert response.get_json()["status"] == "healthy"


def test_chat_endpoint_uses_orchestrator(tmp_path):
    store = JsonStore(tmp_path)
    store.write("faq", [{"keyword": "password", "aliases": [], "answer": "Reset password answer."}])
    store.write("tickets", {"_counter": 1, "items": {}})
    store.write("users", {"guest": {"name": "Guest", "email": "guest@example.com", "company": "Example"}})
    store.write("escalations", {"items": {}})
    app_module.orchestrator = SupportOrchestrator(SupportTools(store))

    client = app_module.app.test_client()
    response = client.post("/api/chat", json={"message": "How do I reset my password?", "user_id": "guest"})

    assert response.status_code == 200
    payload = response.get_json()
    assert payload["agent"] == "triage_agent"
    assert "Reset password answer" in payload["message"]
