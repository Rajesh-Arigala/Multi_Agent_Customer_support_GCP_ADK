"""Appointment tools wrapper for ADK."""

from typing import Any
import random
import string


def _generate_appointment_id() -> str:
    """Generate a random appointment ID."""
    return f"APT-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"


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
    # For deployed environment, return a mock response
    # TODO: Integrate with actual storage in production
    return {
        "status": "success",
        "appointment_id": _generate_appointment_id(),
        "message": "Appointment request created. The clinic will contact you to confirm.",
    }


def check_appointment_status(appointment_id: str) -> dict[str, Any]:
    """
    Check the status of an existing appointment.
    
    Args:
        appointment_id: The appointment ID (e.g., APT-XXXXXXXX).
        
    Returns:
        Dictionary with status and appointment details if found.
    """
    return {
        "status": "success",
        "appointment_id": appointment_id,
        "appointment_status": "requested",
        "message": "Appointment is currently being reviewed by the clinic.",
    }


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
    return {
        "status": "success",
        "appointment_id": appointment_id,
        "message": "Appointment update request submitted.",
    }


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
    return {
        "status": "success",
        "appointment_id": appointment_id,
        "message": "Appointment cancellation request submitted.",
    }
