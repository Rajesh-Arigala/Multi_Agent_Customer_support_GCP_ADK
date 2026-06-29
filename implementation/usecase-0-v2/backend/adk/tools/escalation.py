"""Escalation tool wrapper for ADK."""

from typing import Any

from backend.config import KNOWLEDGE_DIR, GOOGLE_SHEETS_ID, STORAGE_BACKEND
from backend.services.ids import new_id, utc_now
from backend.storage import StorageService


def _get_storage() -> StorageService:
    """Get or create storage service instance."""
    if STORAGE_BACKEND == "google_sheets" and GOOGLE_SHEETS_ID:
        from backend.storage import GoogleSheetsStore
        return StorageService(GoogleSheetsStore(GOOGLE_SHEETS_ID))
    else:
        from backend.storage import CsvStore
        return StorageService(CsvStore(KNOWLEDGE_DIR))


def escalate_to_desk(
    user_id: str,
    reason: str,
    urgency: str = "normal",
    contact_info: dict[str, str] | None = None,
) -> dict[str, Any]:
    """
    Escalate a patient issue to the clinic desk for human follow-up.
    
    Creates an entry in the EmergencyTickets sheet for immediate desk review.
    
    Args:
        user_id: The user identifier (phone number or guest ID).
        reason: The reason for escalation (patient's concern or issue).
        urgency: Urgency level (normal, high, emergency).
        contact_info: Optional contact information (name, phone, email).
        
    Returns:
        Dictionary with status, emergency ticket ID, and escalation details.
    """
    store = _get_storage()
    
    # Look up user if contact info not provided
    if not contact_info:
        user = store.find_by_id("users", "user_id", user_id)
        if user:
            contact_info = {
                "name": user.get("name", ""),
                "phone": user.get("phone", ""),
                "email": user.get("email", ""),
            }
    
    # Create emergency ticket
    emergency_id = new_id("EMG")
    row = {
        "emergency_id": emergency_id,
        "user_id": user_id,
        "reason": reason,
        "urgency": urgency,
        "status": "open",
        "contact_name": contact_info.get("name", "") if contact_info else "",
        "contact_phone": contact_info.get("phone", "") if contact_info else "",
        "contact_email": contact_info.get("email", "") if contact_info else "",
        "desk_notified": "false",
        "created_at": utc_now(),
        "updated_at": utc_now(),
    }
    
    store.append_row("emergency_tickets", row)
    
    return {
        "status": "success",
        "emergency_id": emergency_id,
        "message": f"Emergency ticket {emergency_id} created. A clinic staff member will contact you soon.",
        "emergency_ticket": row,
    }
