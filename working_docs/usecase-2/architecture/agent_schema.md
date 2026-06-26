# Agent Schema

## Purpose
This document defines the agents for RAG by RABBIT.

## Orchestrator
```text
name: rag_by_rabbit_orchestrator
purpose: route stakeholder conversations to the right specialist agent
```

## Profile Triage Agent
```text
name: profile_triage_agent
purpose: answer questions about Rajesh's profile, business experience, AI/MLOps projects, RAG work, workflow agents, action agents, and role fit
tools:
  retrieve_profile_evidence
  retrieve_project_evidence
```

## Web Search Agent
```text
name: web_search_agent
purpose: fallback external grounding when internal RAG evidence is insufficient
tools:
  google_search
```

## Engagement Agent
```text
name: engagement_agent
purpose: classify stakeholder intent and create engagement tickets
tools:
  classify_engagement_type
  create_engagement_ticket
  update_engagement_ticket
```

## Contact Agent
```text
name: contact_agent
purpose: handle contact actions and next-step routing
tools:
  prepare_email_summary
  prepare_whatsapp_message
  capture_linkedin_request
  capture_github_demo_request
```

## Escalation Agent
```text
name: escalation_agent
purpose: route high-value or urgent professional opportunities to Rajesh
tools:
  escalate_to_rajesh
  mark_priority
```
