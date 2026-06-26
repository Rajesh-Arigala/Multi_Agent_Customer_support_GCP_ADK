from typing import Any

from backend.storage import StorageService


class UserTools:
    def __init__(self, store: StorageService):
        self.store = store

    def fetch_user_info(self, user_id: str) -> dict[str, Any]:
        user = self.store.find_by_id("users", "user_id", user_id)
        if not user:
            user = self.store.find_by_id("users", "user_id", "guest")
        if not user:
            return {"status": "error", "message": "User not found."}
        return {"status": "success", "user": user}

