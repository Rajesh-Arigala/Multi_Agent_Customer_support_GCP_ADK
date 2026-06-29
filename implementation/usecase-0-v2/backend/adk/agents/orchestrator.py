"""Support orchestrator agent with doctor-specific routing logic."""

try:
    from google.adk.agents import Agent
    ADK_AVAILABLE = True
except ImportError:
    ADK_AVAILABLE = False
    # Define dummy class for import compatibility
    class Agent:
        pass

from backend.config import MODEL_NAME


ORCHESTRATOR_INSTRUCTION = """
You are a clinic support assistant for Dr. Madhu Patil's practice. Help patients with general questions about the clinic.

Your role is to:
- Answer questions about clinic services, treatments, and doctor information
- Provide information about medical conditions the clinic treats (PCOS, endometriosis, IVF, etc.)
- Share location, hours, and contact information
- Explain clinic policies and procedures

Important: You are NOT a doctor - do not provide specific medical diagnoses or treatment plans. Always include a disclaimer that patients should consult with Dr. Madhu Patil for personalized medical advice.
"""


def create_orchestrator_agent() -> Agent:
    """Create a simple support agent for testing deployment."""
    
    if not ADK_AVAILABLE:
        raise RuntimeError("ADK packages not installed. Run: pip install -r requirements-adk.txt")
    
    # Create a simple single agent (no sub-agents for initial deployment test)
    agent = Agent(
        name="support_orchestrator",
        model=MODEL_NAME,
        instruction=ORCHESTRATOR_INSTRUCTION,
    )
    
    return agent
