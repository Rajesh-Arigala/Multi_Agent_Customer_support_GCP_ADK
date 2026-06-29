"""ADK application root for clinic support orchestrator."""

import os
from pathlib import Path

try:
    from vertexai import agent_engines
    ADK_AVAILABLE = True
except ImportError:
    ADK_AVAILABLE = False

from backend.adk.agents.orchestrator import create_orchestrator_agent
from backend.config import PROJECT_ID, LOCATION, STAGING_BUCKET


def create_adk_app():
    """Create and configure the ADK application with doctor-specific agents."""
    
    if not ADK_AVAILABLE:
        raise RuntimeError("ADK packages not installed. Run: pip install -r requirements-adk.txt")
    
    # Create the root orchestrator agent
    orchestrator = create_orchestrator_agent()
    
    # Create ADK app with the orchestrator as root
    app = agent_engines.AdkApp(
        agent=orchestrator,
        enable_tracing=True,
    )
    
    return app


def get_adk_app():
    """Get or create the ADK app instance (singleton pattern)."""
    if not hasattr(get_adk_app, "_instance"):
        get_adk_app._instance = create_adk_app()
    return get_adk_app._instance
