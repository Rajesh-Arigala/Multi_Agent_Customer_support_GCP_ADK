# Google Sheets Schema

## Purpose
This document defines the operational Google Sheets for RAG by RABBIT.

## Sheet: Stakeholders
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

## Sheet: EngagementTickets
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

## Sheet: ContactActions
```text
action_id
engagement_id
channel
summary
status
created_at
completed_at
```

## Sheet: OpportunityAuditLog
```text
event_id
timestamp
session_id
stakeholder_id
engagement_id
event_type
summary
```
