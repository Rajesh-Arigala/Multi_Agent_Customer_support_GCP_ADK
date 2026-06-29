"""FAQ tool wrapper for ADK."""

import os
from typing import Any

from backend.config import KNOWLEDGE_DIR, GOOGLE_SHEETS_ID, STORAGE_BACKEND
from backend.storage import StorageService
from backend.tools.faq_tools import FaqTools


def _get_storage() -> StorageService:
    """Get or create storage service instance."""
    if STORAGE_BACKEND == "google_sheets" and GOOGLE_SHEETS_ID:
        from backend.storage import GoogleSheetsStore
        return StorageService(GoogleSheetsStore(GOOGLE_SHEETS_ID))
    else:
        from backend.storage import CsvStore
        return StorageService(CsvStore(KNOWLEDGE_DIR))


def get_faq_answer(query: str) -> dict[str, Any]:
    """
    Retrieve an answer from the clinic FAQ or knowledge base.
    
    Args:
        query: The patient's question or query.
        
    Returns:
        Dictionary with status, answer, source, and retrieval metadata.
        Returns not_found status if no relevant information is available.
    """
    store = _get_storage()
    faq_tools = FaqTools(store=store)
    return faq_tools.retrieve_faq_answer(query)
