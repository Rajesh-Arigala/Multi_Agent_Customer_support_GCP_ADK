# System Architecture

## Purpose
This document maps the shared multi-agent architecture to RAG by RABBIT.

## High-Level Architecture
```text
User
-> RAG by RABBIT Orchestrator
   -> profile_triage_agent
   -> web_search_agent
   -> engagement_agent
   -> contact_agent
   -> escalation_agent
-> session/memory layer
-> engagement/opportunity storage
-> notification/contact layer
```

## Architecture Visual
```mermaid
flowchart TD
    U["Website Visitor / Stakeholder"] --> W["rajesharigala.com Chat Widget"]
    W --> O["RAG by RABBIT Orchestrator"]
    O --> P["profile_triage_agent"]
    O --> WS["web_search_agent"]
    O --> EN["engagement_agent"]
    O --> C["contact_agent"]
    O --> E["escalation_agent"]
    P --> RAG["RABBIT RAG Corpus + Azure AI Search"]
    WS --> WEB["Web Search Fallback"]
    EN --> T["Engagement Tickets"]
    C --> CH["Email / WhatsApp / LinkedIn / GitHub Actions"]
    E --> RAJ["Rajesh Follow-up"]
    O --> M["Session + Memory"]
```

## Why This Architecture
It separates answering, external grounding, opportunity qualification, contact actions, and high-value escalation. This lets the system remain professional, evidence-based, and action-oriented.
