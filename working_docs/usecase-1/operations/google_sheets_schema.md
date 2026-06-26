# Google Sheets Schema

## Purpose
This document defines the operational sheets for clinic staff.

## Sheet: Users
```text
user_id
name
phone
preferred_language
preferred_script
created_at
last_seen_at
notes
```

## Sheet: Leads
```text
lead_id
user_id
name
phone
service_interest
source
status
created_at
notes
```

## Sheet: Appointments
```text
appointment_id
user_id
name
phone
service_interest
consultation_type
preferred_location
preferred_date
preferred_time_window
status
desk_notified
user_notified
created_at
updated_at
```

## Sheet: EmergencyTickets
```text
ticket_id
user_id
name
phone
message
urgency_reason
status
human_notified
assigned_to
created_at
notes
```

## Sheet: FAQ
```text
faq_id
category
question
answer
tags
status
updated_at
updated_by
```

## Sheet: AuditLog
```text
event_id
timestamp
user_id
session_id
event_type
object_type
object_id
summary
```
