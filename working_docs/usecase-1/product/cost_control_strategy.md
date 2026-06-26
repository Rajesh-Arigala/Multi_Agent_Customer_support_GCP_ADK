# Cost Control Strategy

## Purpose
This document defines how to keep the doctor appointment agent affordable long term.

## Cost Principles
```text
text-first V1
retrieval before generation
Google Search only on low-confidence retrieval
cache embeddings
rebuild indexes only when content changes
Google Sheets before database
audio optional
video consultation as booking type, not AI video
```

## Model Strategy
Use a cost-effective model for most turns. Reserve stronger models for complex escalation summaries, multilingual ambiguity, or high-value interactions.

## Retrieval Strategy
```text
FAQ hit with high confidence -> answer directly
website retrieval hit -> answer with source grounding
low confidence -> web_search_agent
booking intent -> appointment_agent
urgent intent -> escalation_agent
```

## Avoid Waste
Do not run search or expensive model calls for:

```text
simple greetings
known FAQ answers
appointment status lookup
language detection when lightweight detection is enough
```

## Future Measurement
Track:

```text
cost per conversation
cost per lead
cost per appointment request
Google Search fallback rate
emergency escalation count
language distribution
```
