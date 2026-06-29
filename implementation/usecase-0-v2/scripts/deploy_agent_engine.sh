#!/bin/bash
# Deploy ADK app to Vertex AI Agent Engine

set -e

PROJECT_ID="multi-agent-adk-1"
LOCATION="us-central1"
STAGING_BUCKET="gs://multi-agent-adk-1-adk-agent"

echo "Deploying ADK app to Vertex AI Agent Engine..."
echo "Project: $PROJECT_ID"
echo "Location: $LOCATION"
echo "Staging: $STAGING_BUCKET"

# Deploy using Python script (more reliable than gcloud for ADK)
python scripts/deploy_agent_engine.py
