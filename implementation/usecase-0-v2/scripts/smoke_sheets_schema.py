from __future__ import annotations

from backend.api.runtime import build_runtime_store
from backend.config import GOOGLE_SHEETS_ID
from backend.storage.google_sheets_store import GoogleSheetsStore


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
    if isinstance(store, GoogleSheetsStore):
        print("spreadsheet", GOOGLE_SHEETS_ID)
        print("tabs", ", ".join(list_sheet_titles(store)) or "none")
    for table, required in REQUIRED_HEADERS.items():
        try:
            rows = store.list_rows(table)
            headers = set(table_headers(store, table)) if isinstance(store, GoogleSheetsStore) else set(rows[0].keys()) if rows else set()
        except Exception as exc:
            print(table, "error", str(exc).splitlines()[0])
            continue
        missing = sorted(required - headers)
        print(table, "rows", len(rows), "missing_headers", ",".join(missing) if missing else "none")


def list_sheet_titles(store: GoogleSheetsStore) -> list[str]:
    result = store.service.spreadsheets().get(spreadsheetId=store.spreadsheet_id).execute()
    return [sheet["properties"]["title"] for sheet in result.get("sheets", [])]


def table_headers(store: GoogleSheetsStore, table: str) -> list[str]:
    return store._headers(store._sheet_name(table))


if __name__ == "__main__":
    main()
