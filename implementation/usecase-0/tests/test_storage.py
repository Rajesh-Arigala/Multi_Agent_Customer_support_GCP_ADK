from support_agent.storage import JsonStore


def test_json_store_persists_updates(tmp_path):
    store = JsonStore(tmp_path)
    result = store.update(
        "tickets",
        {"_counter": 1, "items": {}},
        lambda payload: payload["items"].setdefault("TKT-0001", {"status": "open"}),
    )

    assert result == {"status": "open"}
    assert store.read("tickets", {})["items"]["TKT-0001"]["status"] == "open"
