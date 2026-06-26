from datetime import datetime, timezone
from uuid import uuid4

import google.auth
from google.auth import impersonated_credentials

from backend.config import BACKEND_SERVICE_ACCOUNT, GOOGLE_SHEETS_ID
from backend.storage import GoogleSheetsStore


def impersonated_sheets_credentials():
    source_credentials, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    return impersonated_credentials.Credentials(
        source_credentials=source_credentials,
        target_principal=BACKEND_SERVICE_ACCOUNT,
        target_scopes=["https://www.googleapis.com/auth/spreadsheets"],
        lifetime=3600,
    )


def main() -> None:
    credentials = impersonated_sheets_credentials()
    store = GoogleSheetsStore(spreadsheet_id=GOOGLE_SHEETS_ID, credentials=credentials)
    event_id = f"EVT-{uuid4().hex[:8]}"
    row = {
        "event_id": event_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "user_id": "smoke-test",
        "session_id": "smoke-test",
        "event_type": "storage_smoke_test",
        "object_type": "AuditLogs",
        "object_id": event_id,
        "summary": "Verified GoogleSheetsStore append/read path using service account impersonation.",
    }

    store.append_row("audit_logs", row)
    found = store.find_by_id("audit_logs", "event_id", event_id)
    if not found:
        raise SystemExit("Smoke test failed: appended AuditLogs row was not found.")

    print("Google Sheets storage smoke test passed.")
    print(f"service_account={BACKEND_SERVICE_ACCOUNT}")
    print(f"event_id={event_id}")


if __name__ == "__main__":
    main()
