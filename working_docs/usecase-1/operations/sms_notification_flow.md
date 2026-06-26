# SMS Notification Flow

## Purpose
This document defines when and how SMS or WhatsApp notifications should be triggered.

## Notification Events
```text
lead_created
appointment_requested
appointment_confirmed
appointment_updated
appointment_cancelled
emergency_ticket_created
human_followup_required
```

## Recipients
```text
registration desk
user
doctor or concerned authority when required
```

## Message Example: User
```text
Your appointment request has been received. Our registration desk will contact you to confirm the details.
```

## Message Example: Desk
```text
New appointment request: Name, phone, service interest, preferred date/time, consultation type.
```

## Language Rule
User-facing messages should use the user's preferred language where possible. Staff-facing messages can remain in English.
