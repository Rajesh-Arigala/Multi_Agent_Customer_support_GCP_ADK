# Agent Schema

## Purpose
This document defines the agents, responsibilities, and tools for usecase 1.

## Orchestrator
```text
name: support_orchestrator
purpose: route each user request to the correct specialist agent
memory: PreloadMemoryTool + after_agent_callback
```

## Triage Agent
```text
name: triage_agent
purpose: answer FAQ, service, website, location, and general clinic questions
tools:
  retrieve_faq_answer
  retrieve_website_answer
```

## Web Search Agent
```text
name: web_search_agent
purpose: use Google Search only when internal retrieval cannot answer confidently
tools:
  google_search
```

## Appointment Agent
```text
name: appointment_agent
purpose: manage appointment lifecycle
tools:
  create_appointment
  check_appointment_status
  update_appointment
  cancel_appointment
```

## Escalation Agent
```text
name: escalation_agent
purpose: create emergency ticket and notify humans
tools:
  fetch_user_info
  create_emergency_ticket
  escalate_to_registration_desk
```

## Example Routing
```text
User asks IVF question -> triage_agent
FAQ confidence low -> web_search_agent
User wants appointment -> appointment_agent
User says urgent/severe -> escalation_agent
```
