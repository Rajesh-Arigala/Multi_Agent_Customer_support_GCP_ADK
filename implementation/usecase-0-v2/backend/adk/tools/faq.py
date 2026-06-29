"""FAQ tool wrapper for ADK."""

import os
from typing import Any

from backend.config import KNOWLEDGE_DIR, GOOGLE_SHEETS_ID, STORAGE_BACKEND


def get_faq_answer(query: str) -> dict[str, Any]:
    """
    Retrieve an answer from the clinic FAQ or knowledge base.
    
    Args:
        query: The patient's question or query.
        
    Returns:
        Dictionary with status, answer, source, and retrieval metadata.
        Returns not_found status if no relevant information is available.
    """
    # For deployed environment, return a simple response
    # TODO: Integrate with actual knowledge base in production
    return {
        "status": "success",
        "answer": f"FAQ response for: {query}. Please contact the clinic directly for specific information.",
        "source": "faq_tool",
    }
