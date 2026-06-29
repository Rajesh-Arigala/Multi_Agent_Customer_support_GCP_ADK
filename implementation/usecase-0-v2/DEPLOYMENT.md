# Deployment Instructions for Vertex AI Agent Engine

## Prerequisites
- GCP project with Vertex AI API enabled
- Cloud Shell access
- Google Cloud credentials configured (automatic in Cloud Shell)

## Step 1: Push Code to GitHub
```bash
git add .
git commit -m "Add ADK architecture for doctor assistant"
git push origin main
```

## Step 2: Pull Code in Cloud Shell
```bash
git clone https://github.com/Rajesh-Arigala/Multi_Agent_Customer_support_GCP_ADK.git
cd Multi_Agent_Customer_support_GCP_ADK/implementation/usecase-0-v2
```

## Step 3: Install Dependencies
```bash
pip install -r requirements-adk.txt
```

## Step 4: Deploy to Vertex AI Agent Engine
```bash
python scripts/deploy_agent_engine.py
```

This will:
- Create the ADK app with doctor-specific agents
- Deploy to Vertex AI Agent Engine
- Save the agent ID to `.agent_engine_id.txt`
- Take 3-5 minutes to complete

## Step 5: Test the Deployed Agent
```bash
python scripts/smoke_agent_engine_remote.py
```

## Step 6: Update Cloud Run to Use Agent Engine
After deployment, update the Cloud Run backend to call the Agent Engine instead of the local keyword router.

The agent ID will be saved in `.agent_engine_id.txt` - use this in your Cloud Run environment variables.
