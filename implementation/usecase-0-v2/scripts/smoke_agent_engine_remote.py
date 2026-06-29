#!/usr/bin/env python3
"""
Test the deployed ADK agent on Vertex AI Agent Engine.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import vertexai
from google.cloud.aiplatform import AgentEngine

from backend.config import PROJECT_ID, LOCATION


def extract_text(event):
    """Pull the final text response out of an event."""
    parts = event.get("content", {}).get("parts", [])
    for part in parts:
        if part.get("text") and not part.get("function_call"):
            return part["text"]
    return ""


async def test_remote_agent():
    """Test the remote deployed agent."""
    
    # Initialize Vertex AI
    vertexai.init(project=PROJECT_ID, location=LOCATION)
    
    print(f"Testing remote agent on Vertex AI Agent Engine...")
    print(f"Project: {PROJECT_ID}")
    print(f"Location: {LOCATION}\n")
    
    # Load the deployed agent
    print("Loading deployed agent...")
    agent_engine = AgentEngine(
        project=PROJECT_ID,
        location=LOCATION,
        agent_id="doctor-assistant-adk",  # This should match the display_name from deployment
    )
    
    # Create a session
    print("Creating session...")
    session = agent_engine.create_session(user_id="test_user_001")
    print(f"Session created: {session.id}\n")
    
    # Test queries
    queries = [
        "What services does the clinic offer?",
        "I want to book an appointment for PCOS consultation",
        "Check my appointment status",
    ]
    
    for query in queries:
        print(f"User: {query}")
        async for event in agent_engine.stream_query(
            user_id="test_user_001",
            session_id=session.id,
            message=query,
        ):
            text = extract_text(event)
            if text:
                print(f"Agent: {text}")
        print("-" * 60)
    
    print("\n✓ Remote agent test completed")


if __name__ == "__main__":
    import asyncio
    try:
        asyncio.run(test_remote_agent())
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
