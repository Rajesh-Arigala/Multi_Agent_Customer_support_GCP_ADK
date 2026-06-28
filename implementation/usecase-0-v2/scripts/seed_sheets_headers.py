from __future__ import annotations

from backend.api.runtime import build_runtime_store
from backend.storage.google_sheets_store import GoogleSheetsStore


HEADERS = {
    "appointments": [
        "appointment_id",
        "user_id",
        "name",
        "phone",
        "preferred_language",
        "service_interest",
        "consultation_type",
        "preferred_location",
        "preferred_date",
        "preferred_time_window",
        "reason_for_visit",
        "status",
        "desk_notified",
        "user_notified",
        "created_at",
        "updated_at",
    ],
    "emergency_tickets": [
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
    ],
    "leads": [
        "lead_id",
        "user_id",
        "name",
        "phone",
        "service_interest",
        "source",
        "status",
        "created_at",
        "notes",
    ],
    "users": [
        "user_id",
        "name",
        "phone",
        "preferred_language",
        "preferred_script",
        "created_at",
        "last_seen_at",
        "notes",
    ],
    "audit_logs": [
        "event_id",
        "timestamp",
        "user_id",
        "session_id",
        "event_type",
        "object_type",
        "object_id",
        "summary",
    ],
}


def main() -> None:
    store = build_runtime_store()
    if not isinstance(store, GoogleSheetsStore):
        raise SystemExit("Set STORAGE_BACKEND=google_sheets before running this script.")

    for table, required_headers in HEADERS.items():
        sheet = store._sheet_name(table)
        existing = store._headers(sheet)
        merged = list(existing)
        for header in required_headers:
            if header not in merged:
                merged.append(header)
        if merged != existing:
            store._set_headers(sheet, merged)
        print(table, "headers", "updated" if merged != existing else "ok")


if __name__ == "__main__":
    main()
