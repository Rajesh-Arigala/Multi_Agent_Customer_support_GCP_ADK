# Usecase 1: Doctor Appointment Agent - Implementation One Page

## Implementation Goal
Build the Doctor Appointment Agent as a phased, production-ready website chat system that starts with low-cost text Q&A and lead capture, then expands into appointment workflow, emergency escalation, memory, multilingual/audio support, analytics, and production hardening.

## Build Strategy
Use a phased build so each version creates business value without overbuilding too early.

```text
Phase 1: Text Q&A + lead capture
Phase 2: Appointment request workflow
Phase 3: Emergency escalation + human handoff
Phase 4: Memory + returning user continuity
Phase 5: Advanced multilingual + audio
Phase 6: Analytics + cost governance
Phase 7: Production hardening + future database
```

## Core Architecture
```text
Website chat widget
-> Backend API
-> Doctor Agent Orchestrator
   -> triage_agent
   -> web_search_agent
   -> appointment_agent
   -> escalation_agent
-> Retrieval/index layer
-> Google Sheets + local CSV
-> Session/memory layer
-> Notification layer
```

## Phase 1 Implementation
Build first:

```text
chat widget
backend API
FAQ/website knowledge files
embedding generation
vector retrieval
triage_agent
medical disclaimer policy
Level 1 lead capture
Google Sheets Users/Leads
local CSV mirror
```

Success:

```text
User can ask questions, get grounded answers, and share name + phone as a lead.
```

## Phase 2 Implementation
Add:

```text
appointment_agent
create_appointment
check_appointment_status
update_appointment
cancel_appointment
Appointments Google Sheet
appointment status lifecycle
in-person / phone / video consultation type
```

Success:

```text
User can request an appointment and the registration desk can review it.
```

## Phase 3 Implementation
Add:

```text
emergency intent detection
emergency disclaimer
create_emergency_ticket
EmergencyTickets sheet
AuditLog sheet
desk notification workflow
human handoff status
```

Success:

```text
Urgent messages create human-follow-up tickets instead of being handled medically by the agent.
```

## Phase 4 Implementation
Add:

```text
phone-based user lookup
session continuity
PreloadMemoryTool
after_agent_callback
VertexAiSessionService
VertexAiMemoryBankService
preferred language memory
previous lead/appointment lookup
```

Success:

```text
Returning users can continue using their phone number without repeating all details.
```

## Phase 5 Implementation
Add:

```text
language detection
transliteration detection
speech-to-text
text-to-speech
language-specific disclaimer templates
language-specific SMS templates
staff-facing English summaries
```

Success:

```text
Users can interact in supported Indian languages, including transliterated Telugu/Tamil/Hindi/etc. typed in English letters.
```

## Phase 6 Implementation
Add:

```text
request logging
cost tracking
lead analytics
appointment funnel analytics
FAQ performance report
Google Search fallback report
language distribution report
model routing and budget rules
```

Success:

```text
Clinic can see cost per lead, cost per appointment request, FAQ performance, and handoff metrics.
```

## Phase 7 Implementation
Add:

```text
production deployment
secret management
rate limiting
monitoring
backup/restore
test suite
Firestore or Cloud SQL migration option
role-based access
CI/CD
```

Success:

```text
System is production-hardened and can scale beyond Google Sheets when needed.
```

## Initial Data Stores
Start with:

```text
Google Sheets:
  Users
  Leads
  Appointments
  EmergencyTickets
  FAQ
  AuditLog

Local CSV:
  users.csv
  leads.csv
  appointments.csv
  emergency_tickets.csv
  faqs.csv
  audit_log.csv
```

Later:

```text
Firestore or Cloud SQL
```

## Implementation Principles
- Retrieval before generation.
- Google Search only when internal knowledge is insufficient.
- Medical disclaimer for service/symptom answers.
- No diagnosis or treatment recommendation.
- Structured tools for actions.
- Google Sheets first, database later.
- Text-first launch, audio later.
- Video means video consultation booking, not AI avatar.
- Store only necessary user data.
- Keep staff-facing operational summaries in English.

## First Milestone
The first useful milestone is:

```text
Text chat widget + FAQ/website retrieval + lead capture + Google Sheets + medical disclaimers.
```

This proves the value before appointment automation, emergency workflow, audio, analytics, or database migration.

## One-Line Implementation Summary
Implement the Doctor Appointment Agent as a phased ADK-style multi-agent system that begins with grounded text Q&A and lead capture, then adds appointment CRUD, emergency handoff, memory, multilingual/audio support, analytics, and production hardening.
