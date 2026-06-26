# Data Storage Schema

## Purpose
This document defines the starting storage design for RAG by RABBIT.

## Storage Decision
Use Google Sheets first for operational simplicity and local CSV mirrors for backup/dev.

## Core Tables
```text
Stakeholders
EngagementTickets
ContactActions
OpportunityAuditLog
ConversationSummaries
```

## Stakeholders Fields
```text
stakeholder_id
name
organization
role
email
phone
country
preferred_contact_channel
created_at
last_seen_at
notes
```

## EngagementTickets Fields
```text
engagement_id
stakeholder_id
engagement_type
capital_type
national_or_international
intent_summary
priority
status
next_action
created_at
updated_at
```

## Local Mirror
```text
data/stakeholders.csv
data/engagement_tickets.csv
data/contact_actions.csv
data/opportunity_audit_log.csv
data/conversation_summaries.csv
```
