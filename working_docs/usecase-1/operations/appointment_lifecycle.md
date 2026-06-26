# Appointment Lifecycle

## Purpose
This document defines appointment states and actions.

## Appointment Types
```text
in_person
phone_call
video_consultation
```

## Status Values
```text
requested
desk_review
confirmed
rescheduled
cancelled
completed
no_show
```

## CRUD Tools
```text
create_appointment
check_appointment_status
update_appointment
cancel_appointment
```

## Create Appointment Inputs
```text
name
phone
preferred_language
service_interest
consultation_type
preferred_location
preferred_date
preferred_time_window
reason_for_visit
```

## Example Output
```text
Your appointment request has been shared with our registration desk. You will receive a call from our doctor or concerned authority to confirm the time and details.
```

## Video Consultation Rule
Do not promise an instant link unless scheduling integration exists. The desk confirms the slot and link.
