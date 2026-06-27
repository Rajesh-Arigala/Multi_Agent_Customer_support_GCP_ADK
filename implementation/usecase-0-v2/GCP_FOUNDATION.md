# Usecase 0 v2 - GCP Backend Foundation

## Purpose
This document records the completed Google Cloud backend foundation for `usecase-0-v2`.

The goal of `usecase-0-v2` is to become the reusable backend baseline for:

```text
usecase-0: generic customer support baseline
usecase-1: doctor appointment agent
usecase-2: future RAG / engagement use case
```

This checkpoint is important because usecase-1 should not become a one-off implementation. The backend foundation must support a clean migration from generic support flows to real business flows such as appointments, emergency escalation, Google Sheets storage, and Vertex AI Agent Engine deployment.

## Current Status
The GCP foundation is ready.

Completed:

```text
GCP project selected
required APIs enabled
Vertex staging bucket created
backend service account created
IAM roles granted
Google Sheet shared with service account
Google Sheets access verified using service account impersonation
operational Sheet tabs created
```

Implemented after this foundation checkpoint:

```text
backend storage abstraction
GoogleSheetsStore implementation
CsvStore local mirror
local storage tests
Sheets smoke script
agent layer
RABBIT-style drmadhupatil.com corpus
BM25 + vector hybrid retrieval layer
Vertex AI embedding path using text-embedding-005
```

Not completed yet:

```text
Vertex AI Agent Engine deployment
Cloud Run backend wrapper
production API endpoints
managed vector search or production embedding service
```

## GCP Project
```text
Project name: Multi-Agent-ADK-1
Project ID: multi-agent-adk-1
Primary region: us-central1
```

## Shared Environment Configuration
These values should be used by the backend and deployment scripts:

```env
GOOGLE_CLOUD_PROJECT=multi-agent-adk-1
GOOGLE_CLOUD_LOCATION=us-central1
STAGING_BUCKET=gs://multi-agent-adk-1-adk-agent
GOOGLE_SHEETS_ID=1zwyHaspgLVjE5Xax0c9riylI6CBirf12v98k6mgp2c8
MODEL_NAME=gemini-2.5-flash
BACKEND_SERVICE_ACCOUNT=multi-agent-backend-sa@multi-agent-adk-1.iam.gserviceaccount.com
```

## Enabled APIs
The following APIs were enabled in the project:

```text
aiplatform.googleapis.com
run.googleapis.com
cloudbuild.googleapis.com
artifactregistry.googleapis.com
secretmanager.googleapis.com
storage.googleapis.com
sheets.googleapis.com
cloudresourcemanager.googleapis.com
```

## Vertex Staging Bucket
The staging bucket for Vertex AI Agent Engine was created:

```text
gs://multi-agent-adk-1-adk-agent
```

Bucket details observed:

```text
location: US-CENTRAL1
storage class: STANDARD
uniform bucket-level access: true
```

## Backend Service Account
Service account created:

```text
multi-agent-backend-sa@multi-agent-adk-1.iam.gserviceaccount.com
```

Purpose:

```text
Cloud Run backend runtime identity
Google Sheets operational storage access
Vertex AI Agent Engine access
GCS staging bucket access
Secret Manager read access
Cloud Logging write access
```

## IAM Roles Granted
The backend service account has these project roles:

```text
roles/aiplatform.user
roles/storage.objectAdmin
roles/secretmanager.secretAccessor
roles/logging.logWriter
```

The user also received service account impersonation permission for testing:

```text
user:rajesh.arigala@redlegos.com
role: roles/iam.serviceAccountTokenCreator
resource: multi-agent-backend-sa@multi-agent-adk-1.iam.gserviceaccount.com
```

## Google Sheet
Operational Sheet:

```text
Name: Multi-Agent-ADK-1
Sheet ID: 1zwyHaspgLVjE5Xax0c9riylI6CBirf12v98k6mgp2c8
URL: https://docs.google.com/spreadsheets/d/1zwyHaspgLVjE5Xax0c9riylI6CBirf12v98k6mgp2c8/edit
```

Sharing:

```text
multi-agent-backend-sa@multi-agent-adk-1.iam.gserviceaccount.com
permission: Editor
general access: Restricted
```

Keeping general access restricted is correct. The backend service account has explicit Editor access.

## Google Sheets Access Verification
Access was verified using service account impersonation from Cloud Shell.

Verified identity:

```text
multi-agent-backend-sa@multi-agent-adk-1.iam.gserviceaccount.com
```

Verified output:

```text
Spreadsheet title: Multi-Agent-ADK-1
Tabs:
- Sheet1
```

After verification, the operational tabs were created.

## Operational Sheet Tabs
Current intended tab list:

```text
FAQ
Users
Leads
Tickets
Appointments
Escalations
EmergencyTickets
Sessions
Memories
AuditLogs
```

Backend tab mapping should use:

```python
SHEET_TABS = {
    "faq": "FAQ",
    "users": "Users",
    "leads": "Leads",
    "tickets": "Tickets",
    "appointments": "Appointments",
    "escalations": "Escalations",
    "emergency_tickets": "EmergencyTickets",
    "sessions": "Sessions",
    "memories": "Memories",
    "audit_logs": "AuditLogs",
}
```

Note:

```text
The tab is named AuditLogs, not AuditLog.
Backend code should standardize on AuditLogs.
```

## Target Deployment Architecture
The intended production architecture is:

```text
Website / chat UI
-> Cloud Run backend API
-> Vertex AI Agent Engine deployed ADK agent
-> Retrieval service
-> Google Sheets operational storage
-> local CSV mirror for development/backup
-> audit logs and notification service
```

For local development:

```text
Backend API
-> local agent runner or Vertex remote agent
-> CsvStore / local test store
```

For production:

```text
Backend API on Cloud Run
-> Vertex AI Agent Engine remote agent
-> GoogleSheetsStore
-> Secret Manager
-> Cloud Logging
```

## Usecase-0 To Usecase-1 Mapping
The backend foundation should be generic but directly reusable for usecase-1.

| usecase-0 generic baseline | usecase-1 doctor appointment agent |
|---|---|
| support_orchestrator | support_orchestrator / doctor_orchestrator |
| triage_agent | triage_agent |
| FAQ | clinic FAQ + website/service/location KB |
| ticket_agent | appointment_agent |
| Tickets | Appointments |
| escalation_agent | emergency escalation agent |
| Escalations | EmergencyTickets |
| Users | Users / Leads |
| generic fallback | Google Search fallback after retrieval threshold |
| generic memory | returning patient/user continuity |
| AuditLogs | AuditLogs |

## Next Backend Checkpoint
The storage implementation unit has been added:

```text
StorageService interface
CsvStore local implementation
GoogleSheetsStore production implementation
basic tests
Sheets smoke script
```

Minimum storage operations:

```text
append_row(table, row)
list_rows(table)
find_by_id(table, id_field, id_value)
update_by_id(table, id_field, id_value, updates)
```

Local verification completed:

```text
CsvStore append/find/update tests passed
Sheet tab schema mapping tests passed
```

Next GCP verification target:

```text
run scripts/smoke_sheets_storage.py from Cloud Shell
append row to AuditLogs
read row from AuditLogs
```

Do not build agent logic until GoogleSheetsStore is verified against the live Sheet.

## Immediate Division Of Work
Assistant/Codex side:

```text
Create backend skeleton in usecase-0-v2
Implement StorageService
Implement CsvStore
Implement GoogleSheetsStore
Add tests
Add a small smoke script for Sheets access
```

User/GCP side:

```text
Keep Cloud Shell project set to multi-agent-adk-1
Keep service account shared on the Sheet as Editor
Confirm tab names remain unchanged
Run storage smoke tests when provided
Prepare for Vertex AI Agent Engine deployment after storage works
```

## Current Decision
We are not deploying the agent yet.

Current priority:

```text
Backend foundation first
Storage layer second
Agent layer third
Cloud Run / Vertex deployment after local and Sheets storage are verified
```


## Agent Layer Update
The local backend agent layer has been added after storage verification.

Implemented:

```text
support_orchestrator
triage_agent
web_search_agent
ticket_agent
escalation_agent
FAQ, ticket, user, escalation, memory, and audit tools
```

Local verification:

```text
9 tests passed
```

Next gate:

```text
run scripts/smoke_agent_local.py in Cloud Shell
```
