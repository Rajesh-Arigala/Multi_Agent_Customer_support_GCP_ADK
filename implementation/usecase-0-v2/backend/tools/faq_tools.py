from typing import Any

from backend.storage import StorageService


class FaqTools:
    def __init__(self, store: StorageService):
        self.store = store

    def retrieve_faq_answer(self, query: str) -> dict[str, Any]:
        normalized = query.lower()
        for row in self.store.list_rows("faq"):
            if row.get("status", "active").lower() not in {"", "active"}:
                continue
            haystack = " ".join(
                [
                    row.get("faq_id", ""),
                    row.get("category", ""),
                    row.get("question", ""),
                    row.get("answer", ""),
                    row.get("tags", ""),
                    row.get("keyword", ""),
                    row.get("aliases", ""),
                ]
            ).lower()
            if any(token in haystack for token in normalized.split() if len(token) > 2):
                return {
                    "status": "success",
                    "faq_id": row.get("faq_id", ""),
                    "answer": row.get("answer", ""),
                    "source": "FAQ",
                }
        return {"status": "not_found", "message": "No FAQ answer found."}

