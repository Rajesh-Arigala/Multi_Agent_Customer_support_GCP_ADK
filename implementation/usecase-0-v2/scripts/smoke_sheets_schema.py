from __future__ import annotations

from backend.api.runtime import build_runtime_store


REQUIRED_HEADERS = {
    "appointments": {
        "appointment_id",
        "user_id",
        "name",
        "phone",
        "service_interest",
        "consultation_type",
        "preferred_location",
        "preferred_date",
        "preferred_time_window",
        "status",
        "desk_notified",
        "user_notified",
        "created_at",
        "updated_at",
    },
    "emergency_tickets": {
        "ticket_id",
        "user_id",
        "name",
        "phone",
        "message",
        "urgency_reason",
        "status",
        "human_notified",
        "assigned_to",
        "created_at",
        "notes",
    },
    "leads": {"lead_id", "user_id", "name", "phone", "service_interest", "source", "status", "created_at", "notes"},
    "users": {"user_id", "name", "phone", "preferred_language", "created_at", "last_seen_at", "notes"},
    "audit_logs": {"event_id", "timestamp", "user_id", "session_id", "event_type", "object_type", "object_id", "summary"},
}


def main() -> None:
    store = build_runtime_store()
    for table, required in REQUIRED_HEADERS.items():
        rows = store.list_rows(table)
        headers = set(rows[0].keys()) if rows else set()
        missing = sorted(required - headers)
        print(table, "rows", len(rows), "missing_headers", ",".join(missing) if missing else "none")


if __name__ == "__main__":
    main()
