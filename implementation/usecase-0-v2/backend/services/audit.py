from typing import Any

from backend.services.ids import new_id, utc_now
from backend.storage import StorageService


class AuditLogService:
    def __init__(self, store: StorageService):
        self.store = store

    def log_event(
        self,
        user_id: str,
        session_id: str,
        event_type: str,
        object_type: str,
        object_id: str,
        summary: str,
    ) -> dict[str, Any]:
        row = {
            "event_id": new_id("EVT"),
            "timestamp": utc_now(),
            "user_id": user_id,
            "session_id": session_id,
            "event_type": event_type,
            "object_type": object_type,
            "object_id": object_id,
            "summary": summary,
        }
        return self.store.append_row("audit_logs", row)

