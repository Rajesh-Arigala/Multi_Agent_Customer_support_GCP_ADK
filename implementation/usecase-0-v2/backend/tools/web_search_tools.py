from typing import Any


class WebSearchTools:
    def google_search(self, query: str) -> dict[str, Any]:
        return {
            "status": "not_found",
            "tool": "google_search",
            "query": query,
            "answer": "I could not find this in the FAQ. The ADK deployment will route this to google_search.",
        }

