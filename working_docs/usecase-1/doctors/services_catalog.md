# Services Catalog

## Purpose
This document defines the service categories the agent can discuss and use for appointment routing.

## Initial Service Categories
```text
IVF
ICSI
IUI
Fertility preservation
PCOS-related consultation
Endometriosis-related consultation
Male infertility discussion
Repeated IVF failure discussion
General fertility consultation
Gynecology consultation
Video consultation
```

## Service Record Schema
```text
service_id
service_name
category
short_description
website_source_url
faq_ids
appointment_allowed
video_consult_allowed
requires_human_review
status
last_updated_at
```

## Example
```text
service_id: SVC-001
service_name: IVF consultation
category: fertility
appointment_allowed: true
video_consult_allowed: true
requires_human_review: false
```

## Agent Behavior Example
User:

```text
I want to know about IVF.
```

Expected behavior:

```text
The agent gives a general website-grounded explanation, includes the medical disclaimer, and offers to help request an appointment if the user wants personalized guidance from our doctor.
```

## Safety Boundary
The agent can explain services at a general level. It must not say whether a user is eligible for IVF or predict outcomes.
