from typing import Any

from backend.services.ids import new_id, utc_now
from backend.storage import StorageService


class MemoryService:
    def __init__(self, store: StorageService):
        self.store = store

    def preload_memory(self, user_id: str) -> list[dict[str, Any]]:
        return [row for row in self.store.list_rows("memories") if row.get("user_id") == user_id][-5:]

    def save_session_turn(self, session_id: str, user_id: str, role: str, content: str) -> dict[str, Any]:
        return self.store.append_row(
            "sessions",
            {
                "session_event_id": new_id("SES"),
                "session_id": session_id,
                "user_id": user_id,
                "role": role,
                "content": content,
                "created_at": utc_now(),
            },
        )

    def save_facts(self, user_id: str, facts: list[str]) -> list[dict[str, Any]]:
        saved = []
        existing = {row.get("fact") for row in self.preload_memory(user_id)}
        for fact in facts:
            if fact and fact not in existing:
                saved.append(
                    self.store.append_row(
                        "memories",
                        {
                            "memory_id": new_id("MEM"),
                            "user_id": user_id,
                            "fact": fact,
                            "created_at": utc_now(),
                        },
                    )
                )
        return saved

