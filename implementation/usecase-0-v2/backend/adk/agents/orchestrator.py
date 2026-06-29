"""Support orchestrator agent with doctor-specific routing logic."""

try:
    from google.adk.agents import Agent
    ADK_AVAILABLE = True
except ImportError:
    ADK_AVAILABLE = False
    # Define dummy class for import compatibility
    class Agent:
        pass

from backend.adk.agents.appointment import create_appointment_agent
from backend.adk.agents.escalation import create_escalation_agent
from backend.adk.agents.triage import create_triage_agent
from backend.config import MODEL_NAME


ORCHESTRATOR_INSTRUCTION = """
You are a clinic support orchestrator for Dr. Madhu Patil's practice. Your role is to route patient queries to the appropriate specialist agent.

## Routing Rules

1. **Triage/FAQ Agent** - Route to for:
   - Questions about clinic services, treatments, doctor info
   - Medical condition questions (PCOS, endometriosis, IVF, etc.)
   - Location, hours, contact information
   - General clinic policies
   - "What services do you offer?"
   - "Does Dr. Madhu treat PCOS?"

2. **Appointment Agent** - Route to for:
   - Book, schedule, or request an appointment
   - Check appointment status
   - Update or reschedule an appointment
   - Cancel an appointment
   - "I want to book an appointment"
   - "Check my appointment status"
   - "Reschedule my appointment"

3. **Escalation Agent** - Route to for:
   - Urgent or emergency situations
   - Angry or distressed patients
   - Requests to speak to a human
   - "I need to speak to a doctor now"
   - "This is an emergency"
   - "Let me talk to a human"

## Important Notes
- This is a doctor appointment system, NOT a generic ticketing system
- Do NOT route to ticket-related flows
- Prioritize appointment booking for service-related queries
- Always handle urgent cases immediately via escalation
"""


def create_orchestrator_agent() -> Agent:
    """Create the support orchestrator agent with sub-agents."""
    
    if not ADK_AVAILABLE:
        raise RuntimeError("ADK packages not installed. Run: pip install -r requirements-adk.txt")
    
    # Create sub-agents
    triage_agent = create_triage_agent()
    appointment_agent = create_appointment_agent()
    escalation_agent = create_escalation_agent()
    
    # Create orchestrator with sub-agents (no memory tools for initial deployment)
    orchestrator = Agent(
        name="support_orchestrator",
        model=MODEL_NAME,
        instruction=ORCHESTRATOR_INSTRUCTION,
        sub_agents=[
            triage_agent,
            appointment_agent,
            escalation_agent,
        ],
    )
    
    return orchestrator
