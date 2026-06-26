# Usecase 1: Doctor Appointment Agent - Business Use Case

## Business Goal
Build a multilingual AI assistant for Dr. Madhu Patil's website that helps visitors understand clinic services, ask fertility and gynecology-related questions, register interest, request appointments, book video consultations, and get urgent concerns routed to humans.

The agent should convert website traffic into qualified leads and appointment requests while keeping medical safety, human handoff, and cost control at the center.

## Target Users
- First-time website visitors exploring IVF, IUI, fertility, PCOS, endometriosis, or gynecology services
- Returning users who previously shared name and phone number
- Potential patients looking for in-person, phone, or video consultation
- Users who need help in Indian languages or transliterated language typed in English letters
- Users with urgent concerns who need human follow-up

## Business Problem
Clinic website visitors often have questions before they are ready to call or book. If the website only shows static information, many potential leads leave without sharing details. The clinic also needs a safe way to separate general information requests, appointment intent, and urgent concerns.

## Proposed Solution
Deploy a website chat agent that:

- answers from approved website and FAQ knowledge
- supports multilingual text interaction
- understands transliterated Indian languages such as Telugu or Tamil written in English letters
- collects basic identity only when useful
- collects deeper registration details only when booking intent appears
- creates appointment requests and emergency tickets
- stores operational records in Google Sheets with local CSV backup
- escalates urgent cases to the registration desk and our doctor or concerned authority

## Two-Level Information Capture
Level 1 identity:

```text
name
phone number
preferred language
```

Level 2 registration:

```text
service interest
preferred clinic/location
preferred date and time
consultation type: in-person, phone, or video
reason for visit
first visit or follow-up
```

## Agent Architecture
```text
User
-> Support Orchestrator
   -> triage_agent: FAQ, website, service, and clinic Q&A
   -> web_search_agent: fallback grounding when internal retrieval is insufficient
   -> appointment_agent: create, check, update, cancel appointment requests
   -> escalation_agent: urgent concern and human handoff
-> Session memory and long-term memory
-> Google Sheets and local CSV records
```

## Core Journeys
FAQ journey:

```text
User asks about IVF or a clinic service.
Agent answers from approved knowledge, adds medical disclaimer, and offers appointment help.
```

Appointment journey:

```text
User wants to meet the doctor.
Agent collects Level 1 and Level 2 details, creates an appointment request, and notifies the registration desk.
```

Video consultation journey:

```text
User requests a video consultation.
Agent records the request and explains that the registration desk will confirm the time and consultation link.
```

Emergency journey:

```text
User expresses urgent or severe concern.
Agent advises direct clinic/emergency care, creates an emergency ticket, and notifies humans for follow-up.
```

## Medical Safety Position
The agent must not diagnose or replace our doctor. It provides general information and guides the user toward human consultation.

Standard disclaimer:

```text
This is general information and not a medical diagnosis. Our doctor can guide you based on your medical history, reports, and test results.
```

Urgent disclaimer:

```text
If this is urgent or severe, please contact the clinic directly or seek emergency medical care. I can notify our registration desk, and you will receive a call from our doctor or the concerned authority.
```

## Business Value
- More website visitors become qualified leads.
- Registration desk receives structured appointment requests instead of scattered calls/messages.
- Users get answers in their preferred language.
- Returning users can be recognized by phone number and memory.
- Emergency or high-concern messages are escalated instead of being mishandled by the bot.
- Google Sheets gives the clinic team immediate operational access without needing a full database at launch.

## Cost-Control Strategy
- Text-first V1.
- Use website/FAQ retrieval before expensive model calls.
- Use Google Search only when approved knowledge is insufficient.
- Cache embeddings and rebuild only when content changes.
- Start with Google Sheets and local CSV before moving to Firestore or Cloud SQL.
- Add audio and video-consultation automation in later phases.

## Success Metrics
```text
number of leads captured
number of appointment requests created
number of video consultation requests
FAQ resolution rate
Google Search fallback rate
emergency tickets created
human handoff completion rate
language distribution
cost per lead
cost per appointment request
```

## One-Line Summary
The Doctor Appointment Agent turns the clinic website into a multilingual, safety-aware lead and appointment engine that answers from trusted knowledge, captures patient intent, and routes urgent or high-value conversations to the right humans.
