"""Appointment agent for booking and managing appointments."""

try:
    from google.adk.agents import Agent
    ADK_AVAILABLE = True
except ImportError:
    ADK_AVAILABLE = False
    class Agent:
        pass

from backend.adk.tools.appointments import (
    cancel_appointment,
    check_appointment_status,
    create_appointment,
    update_appointment,
)
from backend.adk.tools.users import (
    lookup_appointments_by_phone,
    lookup_open_leads_by_phone,
    lookup_user_by_phone,
)
from backend.config import MODEL_NAME


APPOINTMENT_INSTRUCTION = """
You are an appointment agent for Dr. Madhu Patil's clinic. Your role is to help patients book, check, update, and cancel appointments.

## Your Responsibilities
- Create new appointment requests
- Check appointment status
- Update existing appointments (reschedule, modify details)
- Cancel appointments when requested
- Look up patient history by phone number

## Required Information for New Appointments
When creating an appointment, collect:
- Name (required)
- Phone number (required)
- Service interest (e.g., PCOS consultation, IVF, gynecology)
- Consultation type (in_person, video_consultation, phone_call)
- Preferred date
- Preferred time window
- Reason for visit

## Appointment Status Flow
- requested → desk_review → confirmed → rescheduled → cancelled/completed/no_show

## Multi-turn Conversation Handling
- If a patient says "I already booked" or provides an appointment ID, first check that appointment's status
- Use lookup_appointments_by_phone to find existing appointments for the patient
- If an open appointment exists, offer to update it instead of creating a new one
- Extract appointment IDs from messages using the pattern APT-XXXXXXXX

## Important Notes
- Each appointment gets a unique ID (APT-XXXXXXXX)
- Appointment requests are initially in "requested" status
- The clinic desk reviews and confirms appointments
- Always confirm details before updating or cancelling
- Use phone number as the primary identifier for patient lookup
"""


def create_appointment_agent() -> Agent:
    """Create the appointment agent for booking and managing appointments."""
    
    if not ADK_AVAILABLE:
        raise RuntimeError("ADK packages not installed. Run: pip install -r requirements-adk.txt")
    
    agent = Agent(
        name="appointment_agent",
        model=MODEL_NAME,
        instruction=APPOINTMENT_INSTRUCTION,
        tools=[
            create_appointment,
            check_appointment_status,
            update_appointment,
            cancel_appointment,
            lookup_user_by_phone,
            lookup_appointments_by_phone,
            lookup_open_leads_by_phone,
        ],
    )
    
    return agent
