"""FAQ tool wrapper for ADK."""

from typing import Any

from backend.config import KNOWLEDGE_DIR
from backend.storage import StorageService
from backend.tools.faq_tools import FaqTools


# Global storage instance (will be initialized from config)
_store: StorageService | None = None
_faq_tools: FaqTools | None = None


def init_faq_tools(store: StorageService) -> None:
    """Initialize FAQ tools with storage service."""
    global _store, _faq_tools
    _store = store
    _faq_tools = FaqTools(store=store)


def _get_faq_tools() -> FaqTools:
    """Get or initialize FAQ tools."""
    if _faq_tools is None:
        raise RuntimeError("FAQ tools not initialized. Call init_faq_tools() first.")
    return _faq_tools


def get_faq_answer(query: str) -> dict[str, Any]:
    """
    Retrieve an answer from the clinic FAQ or knowledge base.
    
    Args:
        query: The patient's question or query.
        
    Returns:
        Dictionary with status, answer, source, and retrieval metadata.
        Returns not_found status if no relevant information is available.
    """
    tools = _get_faq_tools()
    return tools.retrieve_faq_answer(query)
