"""Support orchestrator agent with doctor-specific routing logic."""

try:
    from google.adk.agents import Agent
    from google.adk.agents.callback_context import CallbackContext
    from google.adk.tools.preload_memory_tool import PreloadMemoryTool
    ADK_AVAILABLE = True
except ImportError:
    ADK_AVAILABLE = False
    # Define dummy classes for import compatibility
    class Agent:
        pass
    class CallbackContext:
        pass
    class PreloadMemoryTool:
        pass

from backend.adk.agents.appointment import create_appointment_agent
from backend.adk.agents.escalation import create_escalation_agent
from backend.adk.agents.triage import create_triage_agent
from backend.adk.agents.web_search import create_web_search_agent
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

4. **Web Search Agent** - Route to ONLY when:
   - Triage agent indicates information is not found in local knowledge
   - Question is about external/general topics (not clinic-specific)
   - Current events or non-clinic medical information
   - NEVER route clinic service/treatment questions to web search

## Context Management
- Use preload_memory tool at the start of each conversation to load patient context
- After each agent response, save relevant facts to memory for continuity

## Important Notes
- This is a doctor appointment system, NOT a generic ticketing system
- Do NOT route to ticket-related flows
- Prioritize appointment booking for service-related queries
- Always handle urgent cases immediately via escalation
"""


# Auto-saves session to Memory Bank after every conversation
# try/except: locally there is no memory service, so we skip silently
async def save_to_memory_callback(callback_context: CallbackContext):
    try:
        await callback_context.add_session_to_memory()
    except Exception:
        pass


def create_orchestrator_agent() -> Agent:
    """Create the support orchestrator agent with sub-agents."""
    
    if not ADK_AVAILABLE:
        raise RuntimeError("ADK packages not installed. Run: pip install -r requirements-adk.txt")
    
    # Create sub-agents
    triage_agent = create_triage_agent()
    appointment_agent = create_appointment_agent()
    escalation_agent = create_escalation_agent()
    web_search_agent = create_web_search_agent()
    
    # Create orchestrator with sub-agents and tools
    orchestrator = Agent(
        name="support_orchestrator",
        model=MODEL_NAME,
        instruction=ORCHESTRATOR_INSTRUCTION,
        sub_agents=[
            triage_agent,
            appointment_agent,
            escalation_agent,
            web_search_agent,
        ],
        tools=[PreloadMemoryTool()],
        after_agent_callback=save_to_memory_callback,
    )
    
    return orchestrator
