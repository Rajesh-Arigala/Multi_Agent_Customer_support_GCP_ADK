# Usecase 2: RAG by RABBIT - Implementation One Page

## Implementation Goal
Build RAG by RABBIT as the action-agent evolution of RABBIT Assistant. It should reuse the existing RABBIT RAG system, add opportunity classification and engagement-ticket tools, and eventually deploy as a chat widget on `rajesharigala.com`.

## Build Strategy
```text
Phase 1: Stabilize existing RABBIT Assistant as evidence Q&A
Phase 2: Add stakeholder identity and intent capture
Phase 3: Add engagement ticket workflow
Phase 4: Add contact/action tools
Phase 5: Add memory and returning stakeholder continuity
Phase 6: Add analytics, opportunity scoring, and economics
Phase 7: Connect to Sentinel-style governance and production hardening
```

## Core Architecture
```text
rajesharigala.com chat widget
-> RAG by RABBIT backend
-> RABBIT RAG retrieval layer
-> profile_triage_agent
-> engagement_agent
-> contact_agent
-> escalation_agent
-> Google Sheets / CRM-style opportunity storage
-> notification/contact layer
```

## Phase 1 Implementation
```text
reuse Azure AI Search RAG corpus
clean User Mode
profile and project retrieval
proof-of-work positioning
professional boundaries
```

## Phase 2 Implementation
```text
stakeholder identity capture
organization/role/contact capture
intent classification
money vs social capital classification
national/international flag
```

## Phase 3 Implementation
```text
create_engagement_ticket
check_engagement_status
update_engagement_ticket
close_engagement_ticket
EngagementTickets sheet
OpportunityAuditLog
```

## Phase 4 Implementation
```text
prepare_email_summary
prepare_whatsapp_message
capture_linkedin_request
capture_github_demo_request
meeting/demo request workflow
```

## Phase 5 Implementation
```text
session continuity
returning stakeholder lookup
conversation summaries
preferred contact channel memory
prior engagement recall
```

## Phase 6 Implementation
```text
opportunity analytics
cost per qualified opportunity
money-capital vs social-capital reporting
priority scoring
conversion dashboard
```

## Phase 7 Implementation
```text
production deployment
secret management
rate limiting
monitoring
Sentinel Gateway governance path
model routing/cost controls
```

## Initial Data Stores
```text
Google Sheets:
  Stakeholders
  EngagementTickets
  ContactActions
  OpportunityAuditLog
  ConversationSummaries

Local CSV:
  stakeholders.csv
  engagement_tickets.csv
  contact_actions.csv
  opportunity_audit_log.csv
  conversation_summaries.csv
```

## Implementation Principles
- Reuse existing RABBIT RAG assets.
- Answer from evidence first.
- Make the agent itself part of the proof-of-work story.
- Capture only useful professional details.
- Treat serious intent as an engagement ticket.
- Track both money capital and social capital.
- Support national and international opportunities.
- Keep personal/private boundaries strict.
- Connect later to Sentinel for governance and cost control.

## First Milestone
```text
RABBIT Assistant + stakeholder intent capture + basic engagement ticket creation.
```

## One-Line Implementation Summary
Implement RAG by RABBIT as a phased action-agent layer that reuses the existing RABBIT RAG system, captures professional opportunity intent, and routes structured national/international money-capital and social-capital leads to Rajesh.
