# Deployment Architecture

## Purpose
This document defines the intended deployment shape.

## Target
The agent should eventually be deployable as a website chat widget backed by a production API and managed agent runtime.

## Deployment Layers
```text
Website chat widget
-> Backend API
-> ADK multi-agent application
-> Retrieval/index service
-> Google Sheets/local CSV storage
-> SMS/notification provider
-> Vertex session/memory services
```

## Production Requirements
```text
environment config
secret management
logging
request IDs
error handling
rate limits
human handoff path
FAQ rebuild workflow
appointment status tracking
```

## First Deployable Version
```text
Text chat
Website/FAQ retrieval
Google Sheets storage
Appointment request creation
Emergency ticket creation
SMS/desk notification placeholder or integration
```
