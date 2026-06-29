#!/usr/bin/env python3
"""
Deploy ADK app to Vertex AI Agent Engine.

Run this in Cloud Shell after pulling from GitHub:
  git clone https://github.com/Rajesh-Arigala/Multi_Agent_Customer_support_GCP_ADK.git
  cd Multi_Agent_Customer_support_GCP_ADK/implementation/usecase-0-v2
  pip install -r requirements-adk.txt
  python scripts/deploy_agent_engine.py
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import vertexai
from vertexai import agent_engines

from backend.adk.app import create_adk_app
from backend.config import PROJECT_ID, LOCATION, STAGING_BUCKET


def main():
    """Deploy ADK app to Vertex AI Agent Engine."""
    
    # Initialize Vertex AI
    vertexai.init(project=PROJECT_ID, location=LOCATION, staging_bucket=STAGING_BUCKET)
    
    # Create client for deployment
    client = vertexai.Client(project=PROJECT_ID, location=LOCATION)
    
    print(f"Initializing Vertex AI...")
    print(f"  Project: {PROJECT_ID}")
    print(f"  Location: {LOCATION}")
    print(f"  Staging: {STAGING_BUCKET}")
    
    # Create ADK app
    print("\nCreating ADK app...")
    app = create_adk_app()
    
    # Deploy to Agent Engine
    print("\nDeploying to Vertex AI Agent Engine...")
    print("This typically takes 3-5 minutes...")
    
    remote_app = client.agent_engines.create(
        agent=app,
        config={
            "requirements": [
                "google-adk>=1.5.0",
                "google-cloud-aiplatform[adk,agent_engines]>=1.70.0",
                "google-api-python-client>=2.198.0",
                "google-auth>=2.55.1",
                "deprecated>=1.2.14",
                "cloudpickle>=3.0.0",
                "pydantic>=2.12",
                "google-cloud-storage>=1.32.0",
                "requests>=2.32.0",
                "python-dotenv>=1.0.0",
            ],
            "staging_bucket": STAGING_BUCKET,
        }
    )
    
    print(f"\n✓ Deployed successfully!")
    print(f"Resource name: {remote_app.api_resource.name}")
    
    # Save the agent resource name for later use
    with open(".agent_engine_id.txt", "w") as f:
        f.write(remote_app.api_resource.name)
    print(f"Agent resource name saved to .agent_engine_id.txt")
    
    return remote_app


if __name__ == "__main__":
    try:
        remote_app = main()
        print(f"\nTo test the deployed agent:")
        print(f"  python scripts/smoke_agent_engine_remote.py")
    except Exception as e:
        print(f"\n✗ Deployment failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
