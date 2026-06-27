# Usecase 0 v2 - GCP Backend Baseline

## Purpose
`usecase-0-v2` is the production-oriented backend baseline for the multi-agent ADK project.

It is designed to prove the reusable backend foundation before implementing real business use cases such as:

```text
usecase-1: Doctor Appointment Agent
usecase-2: RAG / engagement agent
```

The goal is to avoid building usecase-1 as a one-off system. Instead, usecase-0-v2 should provide the backend contracts, storage layer, deployment pattern, and operational structure that usecase-1 can specialize.

## Current Foundation Status
The GCP backend foundation is ready.

Completed:

```text
GCP project selected
required APIs enabled
Vertex staging bucket created
backend service account created
IAM roles granted
Google Sheet shared with service account
Google Sheets access verified through service account impersonation
operational Sheet tabs created
```

Detailed setup record:

[GCP_FOUNDATION.md](./GCP_FOUNDATION.md)

Layer-by-layer construction guide:

[CONSTRUCTION_STEPS.md](./CONSTRUCTION_STEPS.md)

## GCP Configuration
```env
GOOGLE_CLOUD_PROJECT=multi-agent-adk-1
GOOGLE_CLOUD_LOCATION=us-central1
STAGING_BUCKET=gs://multi-agent-adk-1-adk-agent
GOOGLE_SHEETS_ID=1zwyHaspgLVjE5Xax0c9riylI6CBirf12v98k6mgp2c8
MODEL_NAME=gemini-2.5-flash
BACKEND_SERVICE_ACCOUNT=multi-agent-backend-sa@multi-agent-adk-1.iam.gserviceaccount.com
```

## Operational Google Sheet
Sheet:

```text
Multi-Agent-ADK-1
```

Tabs:

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

Backend code should standardize on `AuditLogs`, not `AuditLog`.

## Target Architecture
Production target:

```text
Website / chat UI
-> Cloud Run backend API
-> Vertex AI Agent Engine deployed ADK agent
-> Retrieval service
-> Google Sheets operational storage
-> local CSV mirror for development and backup
-> audit logs and notification service
```

## Implemented Backend Unit: Storage Layer
The first backend unit is now implemented:

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

Verification completed locally:

```text
CsvStore append/find/update tests passed
Sheet tab schema mapping tests passed
```

GCP verification completed:

```text
GoogleSheetsStore appended and read back an AuditLogs row from the live Sheet
```


## Implemented Backend Unit: Agent Layer
The reusable agent layer is now implemented and verified:

```text
support_orchestrator
triage_agent
web_search_agent
ticket_agent
escalation_agent
FAQ, ticket, user, escalation, memory, and audit tools
```

Verification completed:

```text
agent routing tests passed locally
agent smoke passed on Cloud Shell
```

Cloud Shell smoke command:

```bash
PYTHONPATH=. python scripts/smoke_agent_local.py
```

## Implemented Backend Unit: RAG Corpus + Hybrid Retrieval
The usecase-1 website corpus is now prepared with a RABBIT-style pipeline:

```text
drmadhupatil.com
-> rendered raw HTML
-> structured page JSON
-> clean JSON
-> clean text
-> RAG-ready documents
-> approved JSONL corpus
-> quality reports + corpus manifest
```

Approved corpus input:

```text
rag_pipeline/drmadhupatil_corpus/06_output_rag_documents_ready/drmadhupatil_rag_corpus.jsonl
```

Retrieval method:

```text
BM25-style keyword retrieval with 1-gram, 2-gram, and 3-gram terms
+ vector retrieval with a FAISS adapter when faiss is installed
+ pure-Python vector fallback for local tests
+ metadata filtering
+ hybrid score fusion
+ confidence threshold
```

Verification completed locally:

```text
Dr. Madhu corpus loads: 8 approved documents
hybrid retrieval smoke passes
full test suite: 17 passed
```

Smoke command:

```bash
PYTHONPATH=. python scripts/smoke_hybrid_retrieval.py
```

## Implemented Backend Unit: Vertex Embedding Path
The real semantic embedding path is now implemented and ready for Cloud Shell execution:

```text
Google Gen AI SDK on Vertex AI with text-embedding-005
-> document vectors saved as JSONL
-> optional FAISS index artifact
-> query embedding with same model
-> BM25 + Vertex-vector hybrid fusion
```

Embedding model configuration:

```env
EMBEDDING_MODEL_NAME=text-embedding-005
GOOGLE_CLOUD_PROJECT=multi-agent-adk-1
GOOGLE_CLOUD_LOCATION=us-central1
```

Build command:

```bash
PYTHONPATH=. python scripts/build_vertex_embeddings.py
```

Smoke command:

```bash
PYTHONPATH=. python scripts/smoke_vertex_embeddings.py
```

Local verification uses a fake embedding model and precomputed vectors:

```text
Vertex embedding path tests pass
full test suite: 17 passed
```

## Usecase Mapping
| usecase-0 baseline | usecase-1 doctor appointment agent |
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

## Current Decision
We are not deploying the agent yet.

Current order:

```text
backend foundation - done
storage layer - verified locally and on GCP
agent layer - verified locally and on Cloud Shell
RAG corpus - generated and approved for drmadhupatil.com
hybrid retrieval - implemented and tested
Cloud Run / Vertex deployment
usecase-1 specialization
```

