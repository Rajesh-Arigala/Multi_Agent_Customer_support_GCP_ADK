# Emergency Escalation Flow

## Purpose
This document defines how the agent handles urgent or severe medical concerns.

## Core Rule
The agent must not handle emergencies medically. It must escalate to humans and advise direct clinic or emergency-care contact when the situation sounds urgent or severe.

## Flow
```text
Urgent message detected
-> give emergency-safe response
-> collect name and phone if missing
-> create emergency ticket
-> notify registration desk
-> mark human follow-up required
-> tell user they will receive a call from our doctor or concerned authority
```

## Emergency Ticket Fields
```text
ticket_id
user_id
name
phone
message
urgency_reason
preferred_language
status
assigned_to
created_at
human_notified
notes
```

## Example Response
```text
If this is urgent or severe, please contact the clinic directly or seek emergency medical care. I can notify our registration desk, and you will receive a call from our doctor or the concerned authority.
```

## Escalation Triggers
```text
urgent
severe pain
bleeding
emergency
cannot wait
very worried
need doctor immediately
```
