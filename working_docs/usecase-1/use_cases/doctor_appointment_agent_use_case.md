# Usecase 1: Doctor Appointment Agent

## Purpose
This document defines use case 1: a multilingual doctor-facing website agent for Dr. Madhu Patil's website. It converts website visitors into informed leads, appointment requests, video consultation requests, and emergency handoff tickets.

## Audience
- Clinic owner and registration desk
- Product and implementation team
- Future operators who will manage FAQs, appointments, and human handoffs

## Intent
The agent should not be a generic chatbot. It should be a clinic growth and patient-intake assistant that answers from website and FAQ knowledge, collects the minimum useful identity, supports multilingual interaction, and routes urgent situations to humans.

## Core Flow
```text
Visitor asks a question
-> agent answers from website/FAQ retrieval
-> if answer confidence is low, use grounded web search
-> if visitor shows intent, collect Level 1 identity
-> if booking intent appears, collect Level 2 registration details
-> create appointment request or video consultation request
-> notify registration desk and user
-> for urgent concerns, create emergency ticket and route to our doctor or concerned authority
```

## Level 1 Identity
Collected when the conversation becomes meaningful:

```text
name
phone_number
preferred_language
```

The phone number acts as the practical user ID. ADK or the deployed runtime still creates session IDs for conversation continuity.

## Level 2 Registration
Collected only when the user is interested in appointment, callback, consultation, or follow-up:

```text
age_range
location_preference
service_interest
preferred_date
preferred_time_window
consultation_type
reason_for_visit
first_visit_or_follow_up
```

## Examples
### FAQ Journey
```text
User: IVF success rate enti?
Agent: Telugu transliteration detected. The agent answers in Telugu transliteration, explains general IVF success factors, adds a short disclaimer, and offers appointment help.
```

### Appointment Journey
```text
User: I want to book a video consultation.
Agent: Collects name, phone, preferred language, service interest, date/time window, and creates an appointment request.
```

### Emergency Journey
```text
User: This is urgent, I need help immediately.
Agent: Gives emergency disclaimer, collects minimum contact details if missing, creates emergency ticket, and says the user will get a call from our doctor or concerned authority.
```

## Approved Disclaimer Direction
Use clinic-owned wording:

```text
This is general information and not a medical diagnosis. Our doctor can guide you based on your medical history, reports, and test results.
```

Urgent wording:

```text
If this is urgent or severe, please contact the clinic directly or seek emergency medical care. I can notify our registration desk, and you will receive a call from our doctor or the concerned authority.
```

## Decisions
- Do not force full registration before first interaction.
- Ask Level 1 identity early enough to preserve lead value.
- Use Google Sheets as the operational backend with local CSV mirror.
- Treat video as video consultation booking, not AI avatar video.
- Escalate medical urgency to humans; do not let the agent diagnose.

## Open Questions
- Final supported clinic locations and timings.
- SMS/WhatsApp provider.
- Exact registration desk notification channel.
- Whether video meeting links are created automatically or after desk confirmation.
