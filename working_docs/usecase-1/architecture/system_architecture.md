# System Architecture

## Purpose
This document maps the original multi-agent architecture to the doctor appointment use case.

## Reference Artifact
```text
artifacts/use_case_architecture.png
```

## High-Level Architecture
```text
User
-> PreloadMemoryTool
-> Support Orchestrator
   -> triage_agent
   -> web_search_agent
   -> appointment_agent
   -> escalation_agent
-> after_agent_callback
-> VertexAiSessionService
-> VertexAiMemoryBankService
```

## Use Case Mapping
```text
triage_agent: FAQ, website, services, clinic information
web_search_agent: grounded fallback when retrieval is insufficient
appointment_agent: create, check, update, cancel appointment requests
escalation_agent: emergency ticket and human handoff
```

## Why This Architecture
The architecture separates knowledge answering, external grounding, appointment actions, and emergency escalation. This keeps the system easier to test, safer to operate, and cheaper to run.
