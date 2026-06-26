# Clinic Locations

## Purpose
This document defines how clinic location information should be stored and used by the agent.

## Requirement
The agent must answer location questions only from verified clinic records. Locations must also be used during appointment creation.

## Initial Location Model
```text
location_id
clinic_name
address
area
city
phone
map_link
available_days
available_time_windows
services_available
status
last_verified_at
```

## Example Record
```text
location_id: LOC-001
clinic_name: Motherhood Hospital
area: Sarjapur
city: Bengaluru
available_days: To be confirmed
available_time_windows: To be confirmed
status: active
```

## Example User Journey
User:

```text
Where can I meet the doctor?
```

Expected behavior:

```text
The agent lists verified clinic locations and asks whether the user prefers in-person, phone, or video consultation.
```

## Open Questions
- Final address list.
- Final timings.
- Which locations support video consultation scheduling.
- Whether map links should be included in SMS.
