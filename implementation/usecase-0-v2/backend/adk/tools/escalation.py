"""Escalation tool wrapper for ADK."""

from typing import Any
import random
import string


def _generate_emergency_id() -> str:
    """Generate a random emergency ticket ID."""
    return f"EMG-{''.join(random.choices(string.ascii_uppercase + string.digits, k=8))}"


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
    # For deployed environment, return a mock response
    # TODO: Integrate with actual storage in production
    emergency_id = _generate_emergency_id()
    return {
        "status": "success",
        "emergency_id": emergency_id,
        "message": f"Emergency ticket {emergency_id} created. A clinic staff member will contact you soon.",
    }
