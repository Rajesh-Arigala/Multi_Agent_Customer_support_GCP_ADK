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

For the latest verified runtime state, start here:

[SESSION_HANDOFF.md](./SESSION_HANDOFF.md)

[CURRENT_STATUS.md](./CURRENT_STATUS.md)

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
doctor RAG knowledge bundle imported into backend/knowledge/latest
main backend detects imported_bundle as the active knowledge source
patient-friendly answer formatter active in /chat responses
mobile-friendly frontend served by FastAPI at /
Dockerfile and Cloud Run deploy/smoke scripts added
Cloud Shell verification: 35 tests passed
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

Current verified runtime path:

```text
FastAPI /chat
-> SupportOrchestrator
-> triage_agent
-> FaqTools
-> backend/knowledge/latest imported bundle
-> Vertex text-embedding-005 query embedding
-> BM25 + Vertex-vector hybrid retrieval
-> patient-friendly answer formatter
-> response with source and retrieval metadata
```

Current architecture status:

```text
triage_agent + RAG path       running and verified
ticket_agent                  implemented, basic tests pass
escalation_agent              implemented, basic tests pass
web_search_agent fallback     exists, needs stricter gating
local memory/audit            implemented locally
frontend chat UI              implemented
Docker/Cloud Run scripts      implemented
Vertex Session/Memory Bank    not integrated yet
Cloud Run main demo           ready to deploy from Cloud Shell
```

## Main Demo Deployment

The complete same-service demo is packaged as:

```text
FastAPI backend API
-> multi-agent orchestrator
-> imported RAG knowledge bundle
-> Vertex hybrid retrieval
-> patient-friendly answer formatter
-> frontend chat UI served at /
```

Deploy from Cloud Shell after the imported bundle is present in `backend/knowledge/latest`:

```bash
cd ~/Multi_Agent_Customer_support_GCP_ADK/implementation/usecase-0-v2
test -f backend/knowledge/latest/corpus.jsonl
test -f backend/knowledge/latest/embeddings.jsonl

bash scripts/deploy_cloud_run.sh
```

Smoke the deployed service:

```bash
SERVICE_URL="$(gcloud run services describe doctor-assistant-usecase-0-v2 \
  --project multi-agent-adk-1 \
  --region us-central1 \
  --format='value(status.url)')"

bash scripts/smoke_deployed_cloud_run.sh "$SERVICE_URL"
```

The smoke script verifies:

```text
GET  /health
GET  /metadata/status
GET  /retrieval/smoke
POST /chat with "Can Dr Madhu help with PCOS and endometriosis?"
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

Legacy approved corpus input:

```text
rag_pipeline/drmadhupatil_corpus/06_output_rag_documents_ready/drmadhupatil_rag_corpus.jsonl
```

Current active runtime corpus after the doctor-demo sync:

```text
backend/knowledge/latest/corpus.jsonl
backend/knowledge/latest/embeddings.jsonl
backend/knowledge/latest/content_version.json
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
current full test suite after imported-bundle integration: 35 passed
```

Smoke command:

```bash
PYTHONPATH=. python scripts/smoke_hybrid_retrieval.py
```

Ranking refinement:

```text
service-page ranking policy prefers matching service pages over the broad homepage for service-specific medical queries
PCOS/endometriosis -> service5
IVF/ICSI -> service2
fertility preservation -> service4
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

Local verification uses a fake embedding model and precomputed vectors. Cloud Shell verification uses real Vertex embeddings.

```text
Vertex embedding path tests pass
Cloud Shell embedding build: documents=8, dimensions=768, faiss_index_written=True
Cloud Shell smoke: service-specific queries resolve to service pages
full test suite: 35 passed after imported-bundle runtime wiring and answer formatting
```

## Implemented Backend Unit: Agent Retrieval Integration
The FAQ/retrieval tool now prefers the imported doctor-demo knowledge bundle when it is complete:

```text
FaqTools
-> FAQ rows first, if maintained in storage
-> otherwise backend/knowledge/latest imported RAG corpus
-> imported Vertex document vectors, if artifact exists
-> BM25 + Vertex-vector hybrid retrieval
-> patient-friendly answer formatter
-> web_search_agent only after local retrieval misses
```

Retrieval modes are explicit in responses:

```text
hybrid_vertex              real Vertex document/query vectors
hybrid_hash                local fallback when embeddings are absent or FAQ rows are used
hybrid_hash_missing_vectors local fallback when embedding coverage is incomplete
```

Agent-level smoke command:

```bash
PYTHONPATH=. python scripts/smoke_agent_vertex_retrieval.py
```

Expected Cloud Shell hits:

```text
PCOS/endometriosis -> WEB-DRMADHU-006, mode=hybrid_vertex
IVF/ICSI -> WEB-DRMADHU-003, mode=hybrid_vertex
fertility preservation -> WEB-DRMADHU-005, mode=hybrid_vertex
```

Local verification:

```text
FaqTools Vertex-artifact path tests pass
scripts compile
full test suite: 35 passed
```

Current Cloud Shell verification:

```text
knowledge_source=imported_bundle
PCOS/endometriosis -> WEB-DRMADHU-006, mode=hybrid_vertex
IVF/ICSI -> WEB-DRMADHU-003, mode=hybrid_vertex
fertility preservation -> WEB-DRMADHU-005, mode=hybrid_vertex
/chat returns polished max-4-bullet patient answer
```

## Implemented Backend Unit: Metadata Enrichment
The RAG corpus now has deterministic business metadata for filtering before retrieval scoring.

```text
raw approved RAG corpus
-> scripts/enrich_rag_metadata.py
-> enriched RAG corpus
-> metadata-aware filters
-> hybrid retrieval
```

Enriched artifact:

```text
rag_pipeline/drmadhupatil_corpus/07_output_enriched_documents/drmadhupatil_enriched_rag_corpus.jsonl
```

Metadata fields include:

```text
page_type
service_slug
service_name
specialty
conditions
treatments
intent
appointment_eligible
emergency_related
source_priority
metadata_version
```

Filtering behavior:

```text
PCOS/endometriosis query -> conditions filter -> service5
IVF appointment query -> treatments + appointment_eligible filters -> service2
No filtered hit -> retry without metadata filter
```

Build command:

```bash
PYTHONPATH=. python scripts/enrich_rag_metadata.py
```

Local verification:

```text
enriched documents=8
page_types={'homepage': 1, 'service': 6, 'blog': 1}
metadata enrichment tests pass
current full test suite after imported-bundle integration: 35 passed
```

Existing Vertex embeddings remain compatible because vectors are keyed by `doc_id`. Rebuild embeddings only when document text changes or when metadata is intentionally added to embedding text.

## Implemented Backend Unit: API Layer
The backend now exposes the orchestrator through FastAPI.

```text
GET  /health
GET  /metadata/status
POST /chat
GET  /retrieval/smoke
```

API files:

```text
backend/api/app.py
backend/api/runtime.py
scripts/smoke_api_local.py
requirements-api.txt
```

Run locally or in Cloud Shell after installing API dependencies:

```bash
pip install -r requirements-api.txt
PYTHONPATH=. uvicorn backend.api.app:app --host 0.0.0.0 --port 8080
```

Smoke command:

```bash
PYTHONPATH=. python scripts/smoke_api_local.py
```

Expected smoke:

```text
health 200 ok
metadata 200 ok 8
chat 200 triage_agent WEB-DRMADHU-006 hybrid_vertex
retrieval_smoke 200 3
```

Local verification:

```text
API runtime tests pass
API modules compile
full test suite: 35 passed
Cloud Shell API smoke passed
```

Verified API routes:

```text
GET  /health
GET  /metadata/status
POST /chat
GET  /retrieval/smoke
```

Note: `/metadata` is not a route. Use `/metadata/status`.

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
metadata enrichment - implemented and tested
hybrid retrieval - implemented and tested
knowledge export/import from rag-usecase-0 - verified
API layer - implemented and verified in Cloud Shell
patient-friendly answer formatting - implemented and verified
mobile frontend for main demo
Cloud Run main demo deployment
usecase-1 specialization
```


## Deferred Future Work
Future corpus refresh automation is intentionally deferred. The future pipeline should detect website content changes, rebuild the RAG corpus, regenerate embeddings only when needed, rebuild FAISS, and write a refresh report.
