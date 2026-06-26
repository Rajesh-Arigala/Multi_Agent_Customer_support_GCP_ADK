# Emergency Response Policy

## Purpose
This document defines safety behavior for emergency-like messages.

## Rule
The agent must not diagnose, triage clinically, or delay emergency care.

## Agent Response Pattern
```text
acknowledge urgency
advise direct clinic/emergency care
offer to notify registration desk
collect minimum details if missing
create emergency ticket
```

## Example
```text
I am sorry you are going through this. If this is urgent or severe, please contact the clinic directly or seek emergency medical care. I can notify our registration desk, and you will receive a call from our doctor or the concerned authority.
```

## Escalation Priority
```text
high: severe/urgent wording
medium: worried/frustrated but not severe
low: general follow-up request
```

## Audit Requirement
Every emergency escalation should be logged in `EmergencyTickets` and `AuditLog`.
