"""User lookup tools for ADK."""

from typing import Any

from backend.config import KNOWLEDGE_DIR, GOOGLE_SHEETS_ID, STORAGE_BACKEND
from backend.storage import StorageService


def _get_storage() -> StorageService:
    """Get or create storage service instance."""
    if STORAGE_BACKEND == "google_sheets" and GOOGLE_SHEETS_ID:
        from backend.storage import GoogleSheetsStore
        return StorageService(GoogleSheetsStore(GOOGLE_SHEETS_ID))
    else:
        from backend.storage import CsvStore
        return StorageService(CsvStore(KNOWLEDGE_DIR))


def lookup_user_by_phone(phone: str) -> dict[str, Any]:
    """
    Look up a user by phone number in the Users sheet.
    
    Args:
        phone: The patient's phone number.
        
    Returns:
        Dictionary with status and user information if found.
    """
    store = _get_storage()
    user = store.find_by_id("users", "phone", phone)
    if not user:
        return {"status": "not_found", "message": f"No user found with phone {phone}"}
    return {"status": "success", "user": user}


def lookup_appointments_by_phone(phone: str) -> dict[str, Any]:
    """
    Look up all appointments for a phone number in the Appointments sheet.
    
    Args:
        phone: The patient's phone number.
        
    Returns:
        Dictionary with status and list of appointments if found.
    """
    store = _get_storage()
    # Filter appointments by phone number
    all_appointments = store.list_rows("appointments")
    user_appointments = [apt for apt in all_appointments if apt.get("phone") == phone]
    
    if not user_appointments:
        return {"status": "not_found", "message": f"No appointments found for phone {phone}"}
    
    return {"status": "success", "appointments": user_appointments}


def lookup_open_leads_by_phone(phone: str) -> dict[str, Any]:
    """
    Look up open leads for a phone number in the Leads sheet.
    
    Args:
        phone: The patient's phone number.
        
    Returns:
        Dictionary with status and list of open leads if found.
    """
    store = _get_storage()
    # Filter leads by phone number and open status
    all_leads = store.list_rows("leads")
    open_statuses = {"new", "contacted", "in_progress"}
    user_leads = [
        lead for lead in all_leads 
        if lead.get("phone") == phone and lead.get("status") in open_statuses
    ]
    
    if not user_leads:
        return {"status": "not_found", "message": f"No open leads found for phone {phone}"}
    
    return {"status": "success", "leads": user_leads}
