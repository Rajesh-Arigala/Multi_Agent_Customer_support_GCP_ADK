"""Appointment tools wrapper for ADK."""

from typing import Any

from backend.config import KNOWLEDGE_DIR, GOOGLE_SHEETS_ID, STORAGE_BACKEND
from backend.storage import StorageService
from backend.tools.appointment_tools import AppointmentTools


def _get_storage() -> StorageService:
    """Get or create storage service instance."""
    if STORAGE_BACKEND == "google_sheets" and GOOGLE_SHEETS_ID:
        from backend.storage import GoogleSheetsStore
        return StorageService(GoogleSheetsStore(GOOGLE_SHEETS_ID))
    else:
        from backend.storage import CsvStore
        return StorageService(CsvStore(KNOWLEDGE_DIR))


def _get_appointment_tools() -> AppointmentTools:
    """Get appointment tools instance."""
    store = _get_storage()
    return AppointmentTools(store=store)


def create_appointment(
    user_id: str,
    message: str,
    details: dict[str, str] | None = None,
) -> dict[str, Any]:
    """
    Create a new appointment request.
    
    Args:
        user_id: The user identifier (phone number or guest ID).
        message: The patient's message containing appointment details.
        details: Optional pre-extracted appointment details (name, phone, service, etc.).
        
    Returns:
        Dictionary with status, appointment_id, appointment details, and any missing fields.
    """
    tools = _get_appointment_tools()
    return tools.create_appointment(user_id, message, details)


def check_appointment_status(appointment_id: str) -> dict[str, Any]:
    """
    Check the status of an existing appointment.
    
    Args:
        appointment_id: The appointment ID (e.g., APT-XXXXXXXX).
        
    Returns:
        Dictionary with status and appointment details if found.
    """
    tools = _get_appointment_tools()
    return tools.check_appointment_status(appointment_id)


def update_appointment(
    appointment_id: str | None,
    updates: dict[str, str],
) -> dict[str, Any]:
    """
    Update an existing appointment.
    
    Args:
        appointment_id: The appointment ID to update.
        updates: Dictionary of fields to update (e.g., status, preferred_date, etc.).
        
    Returns:
        Dictionary with status and updated appointment details.
    """
    tools = _get_appointment_tools()
    return tools.update_appointment(appointment_id, updates)


def cancel_appointment(
    appointment_id: str | None,
    reason: str = "",
) -> dict[str, Any]:
    """
    Cancel an existing appointment.
    
    Args:
        appointment_id: The appointment ID to cancel.
        reason: Optional reason for cancellation.
        
    Returns:
        Dictionary with status and cancellation confirmation.
    """
    tools = _get_appointment_tools()
    return tools.cancel_appointment(appointment_id, reason)
