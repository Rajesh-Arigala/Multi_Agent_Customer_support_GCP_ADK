"""User lookup tools for ADK."""

from typing import Any

from backend.storage import StorageService


# Global storage instance
_store: StorageService | None = None


def init_user_tools(store: StorageService) -> None:
    """Initialize user tools with storage service."""
    global _store
    _store = store


def _get_store() -> StorageService:
    """Get or initialize storage."""
    if _store is None:
        raise RuntimeError("User tools not initialized. Call init_user_tools() first.")
    return _store


def lookup_user_by_phone(phone: str) -> dict[str, Any]:
    """
    Look up a user by phone number in the Users sheet.
    
    Args:
        phone: The patient's phone number.
        
    Returns:
        Dictionary with status and user information if found.
    """
    store = _get_store()
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
    store = _get_store()
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
    store = _get_store()
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
