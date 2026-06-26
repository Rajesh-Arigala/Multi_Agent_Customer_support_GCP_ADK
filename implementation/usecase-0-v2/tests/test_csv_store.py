from backend.storage import CsvStore


def test_append_and_find_row(tmp_path):
    store = CsvStore(tmp_path)

    stored = store.append_row("audit_logs", {"event_id": "EVT-1", "summary": "created"})
    found = store.find_by_id("audit_logs", "event_id", "EVT-1")

    assert stored["event_id"] == "EVT-1"
    assert found == stored


def test_update_by_id(tmp_path):
    store = CsvStore(tmp_path)
    store.append_row("tickets", {"ticket_id": "TKT-0001", "status": "open"})

    updated = store.update_by_id("tickets", "ticket_id", "TKT-0001", {"status": "closed"})

    assert updated is not None
    assert updated["status"] == "closed"
    assert store.find_by_id("tickets", "ticket_id", "TKT-0001")["status"] == "closed"


def test_update_missing_row_returns_none(tmp_path):
    store = CsvStore(tmp_path)
    store.append_row("tickets", {"ticket_id": "TKT-0001", "status": "open"})

    assert store.update_by_id("tickets", "ticket_id", "TKT-9999", {"status": "closed"}) is None

