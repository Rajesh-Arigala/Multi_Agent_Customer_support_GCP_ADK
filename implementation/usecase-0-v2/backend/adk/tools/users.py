"""User lookup tools for ADK."""

from typing import Any


def lookup_user_by_phone(phone: str) -> dict[str, Any]:
    """
    Look up a user by phone number in the Users sheet.
    
    Args:
        phone: The patient's phone number.
        
    Returns:
        Dictionary with status and user information if found.
    """
    # For deployed environment, return a mock response
    # TODO: Integrate with actual storage in production
    return {
        "status": "not_found",
        "message": f"No user found with phone {phone}",
    }


def lookup_appointments_by_phone(phone: str) -> dict[str, Any]:
    """
    Look up all appointments for a phone number in the Appointments sheet.
    
    Args:
        phone: The patient's phone number.
        
    Returns:
        Dictionary with status and list of appointments if found.
    """
    return {
        "status": "not_found",
        "message": f"No appointments found for phone {phone}",
    }


def lookup_open_leads_by_phone(phone: str) -> dict[str, Any]:
    """
    Look up open leads for a phone number in the Leads sheet.
    
    Args:
        phone: The patient's phone number.
        
    Returns:
        Dictionary with status and list of open leads if found.
    """
    return {
        "status": "not_found",
        "message": f"No open leads found for phone {phone}",
    }
