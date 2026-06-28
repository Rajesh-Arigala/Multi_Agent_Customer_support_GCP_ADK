# Construction Steps - Usecase 0 v2

## Purpose
This document explains the backend construction sequence for `usecase-0-v2`.

The project rule is:

```text
finish one layer -> verify it -> document it -> move to the next layer
```

This keeps the baseline understandable, testable, and reusable for later business use cases.

## Layer 1 - Backend Foundation Ready: GCP

### Goal
Prepare the Google Cloud environment so the backend has a real deployment target, runtime identity, staging bucket, and operational Google Sheet.

### Logic
Production backend code needs cloud dependencies to be known early:

```text
project
region
service account
enabled APIs
staging bucket
operational storage
permissions
```

If this layer is skipped, local code may work but fail later during Cloud Run, Vertex AI Agent Engine, or Google Sheets integration.

### Construction Steps
1. Select the GCP project:

```text
multi-agent-adk-1
```

2. Enable required APIs:

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

3. Create the Vertex AI staging bucket:

```text
gs://multi-agent-adk-1-adk-agent
```

4. Create the backend runtime service account:

```text
multi-agent-backend-sa@multi-agent-adk-1.iam.gserviceaccount.com
```

5. Grant required IAM roles:

```text
roles/aiplatform.user
roles/storage.objectAdmin
roles/secretmanager.secretAccessor
roles/logging.logWriter
```

6. Share the operational Google Sheet with the service account as Editor.

7. Keep Sheet general access restricted.

8. Verify Sheets access by impersonating the service account.

### Shared Configuration
```env
GOOGLE_CLOUD_PROJECT=multi-agent-adk-1
GOOGLE_CLOUD_LOCATION=us-central1
STAGING_BUCKET=gs://multi-agent-adk-1-adk-agent
GOOGLE_SHEETS_ID=1zwyHaspgLVjE5Xax0c9riylI6CBirf12v98k6mgp2c8
MODEL_NAME=gemini-2.5-flash
BACKEND_SERVICE_ACCOUNT=multi-agent-backend-sa@multi-agent-adk-1.iam.gserviceaccount.com
```

### Verification Gate
The service account must be able to read the Google Sheet.

Expected verification:

```text
Spreadsheet title: Multi-Agent-ADK-1
Tabs are visible from the service account
```

### Status
```text
backend foundation ready - GCP
```

## Layer 2 - Storage Layer

### Goal
Create one storage contract that supports both local development and production Google Sheets operations.

### Logic
Usecase-1 needs clinic staff to work from Google Sheets, while local development and tests need fast file-based storage.

The backend should depend on an interface, not directly on Sheets:

```text
StorageService
-> CsvStore
-> GoogleSheetsStore
```

This keeps the system replaceable later with Firestore, Cloud SQL, or another database.

### Construction Steps
1. Define the storage contract:

```text
backend/storage/base.py
```

2. Implement local CSV storage:

```text
backend/storage/csv_store.py
```

3. Implement Google Sheets storage:

```text
backend/storage/google_sheets_store.py
```

4. Define canonical table-to-tab mapping:

```text
backend/storage/schema.py
```

5. Add a GCP smoke script:

```text
scripts/smoke_sheets_storage.py
```

6. Add local tests:

```text
tests/test_csv_store.py
tests/test_schema.py
```

### Storage Contract
Every storage backend must support:

```text
append_row(table, row)
list_rows(table)
find_by_id(table, id_field, id_value)
update_by_id(table, id_field, id_value, updates)
```

### Canonical Sheet Tabs
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

### Local Verification Gate
Run tests:

```bash
python -m pytest
```

Expected result:

```text
CsvStore append/find/update tests pass
Sheet tab schema mapping tests pass
```

Current result:

```text
5 tests passed
```

### GCP Verification Gate
Run the Sheets smoke test from Cloud Shell:

```bash
python scripts/smoke_sheets_storage.py
```

Expected result:

```text
Google Sheets storage smoke test passed.
service_account=multi-agent-backend-sa@multi-agent-adk-1.iam.gserviceaccount.com
event_id=EVT-...
```

Expected Sheet behavior:

```text
a row is appended to AuditLogs
the same row is read back by event_id
```

### Status
```text
storage layer verified locally and on GCP
```

## Layer 3 - Agent Layer

### Goal
Build the reusable ADK-compatible agent structure.

### Logic
Agents should be built only after storage is verified, because agents will create records, update records, read user context, and write audit logs.

If storage is unstable, agent failures become difficult to debug.

### Implemented Components
```text
support_orchestrator
triage_agent
web_search_agent
ticket_agent
escalation_agent
```

### Implemented Tools
```text
FAQ retrieval
web search fallback placeholder
ticket create/check/update
user lookup
escalation
memory preload
after-agent fact save
audit logging
```

### Verification Gate
Run local tests:

```bash
python -m pytest
```

Expected result:

```text
agent routing tests pass
ticket lifecycle tests pass
escalation tests pass
memory/audit tests pass
```

Current result:

```text
21 tests passed
```

### Cloud Shell Smoke Gate
Run:

```bash
PYTHONPATH=. python scripts/smoke_agent_local.py
```

Expected result:

```text
triage_agent - ...
ticket_agent - ...
escalation_agent - ...
```

### Status
```text
agent layer verified locally and on Cloud Shell
```

## Layer 4 - RAG Corpus And Hybrid Retrieval

### Goal
Create a trusted local knowledge base before the agent uses web search.

### Logic
The agent should answer from owned content first. For usecase-1, the clinic website is the trusted source. Web search should only happen after local retrieval fails the confidence threshold.

The selected retrieval method is hybrid:

```text
BM25-style keyword retrieval with 1-gram, 2-gram, and 3-gram terms
+ vector retrieval
+ metadata filtering
+ hybrid score fusion
+ confidence threshold
```

The vector retriever uses a FAISS adapter when `faiss` is installed and a pure-Python fallback for local tests. This keeps the baseline portable while preserving the FAISS path for production-like indexing.

### Construction Steps
1. Create a RABBIT-style corpus workspace:

```text
rag_pipeline/drmadhupatil_corpus/
```

2. Crawl `drmadhupatil.com` through the staged pipeline:

```text
01_input_seed_and_config
02_output_raw_html_rendered
03_output_structured_json
04_output_clean_json
05_output_clean_text
06_output_rag_documents
06_output_rag_documents_ready
07_output_quality_reports_manifest
```

3. Approve canonical documents and exclude duplicate `.html` URL variants.

4. Build retrieval modules:

```text
backend/retrieval/keyword.py
backend/retrieval/vector.py
backend/retrieval/hybrid.py
backend/retrieval/loader.py
```

5. Connect `FaqTools` to the hybrid retriever before `web_search_agent` fallback.

6. Add retrieval smoke and tests:

```text
scripts/smoke_hybrid_retrieval.py
tests/test_hybrid_retrieval.py
```

### Corpus Verification Gate
Current result:

```text
pages crawled: 14
pages failed: 0
raw RAG documents: 14
approved RAG documents: 8
duplicate URL variants excluded: 6
```

Approved retrieval input:

```text
rag_pipeline/drmadhupatil_corpus/06_output_rag_documents_ready/drmadhupatil_rag_corpus.jsonl
```

### Retrieval Verification Gate
Run:

```bash
PYTHONPATH=. python scripts/smoke_hybrid_retrieval.py
```

Expected behavior:

```text
IVF query resolves to service2
fertility preservation query resolves to service4
retrieval returns confidence scores before web_search_agent fallback
```

Current result:

```text
hybrid retrieval smoke passed
21 tests passed
```

### Status
```text
RAG corpus and hybrid retrieval implemented locally and verified on Cloud Shell
```

## Layer 4E - Vertex AI Embeddings

### Goal
Replace the temporary hash-vector path with real semantic embeddings while keeping BM25 keyword retrieval and FAISS hybrid search.

### Logic
FAISS is the vector search engine. Google Gen AI SDK calls Vertex AI `text-embedding-005` to create the semantic vectors that go into FAISS.

The retrieval path becomes:

```text
approved RAG corpus
-> Vertex document embeddings
-> persisted embedding JSONL
-> FAISS index artifact when faiss is installed
-> Vertex query embedding
-> BM25 + vector hybrid scoring
```

### Construction Steps
1. Add Vertex embedding wrapper:

```text
backend/retrieval/vertex_embeddings.py
```

2. Add embedding artifact loader/saver:

```text
backend/retrieval/embedding_store.py
```

3. Extend vector retrieval to accept precomputed document vectors.

4. Add build and smoke scripts:

```text
scripts/build_vertex_embeddings.py
scripts/smoke_vertex_embeddings.py
```

5. Add local tests with a fake embedding model:

```text
tests/test_vertex_embedding_path.py
```

6. Add optional dependency file:

```text
requirements-embeddings.txt
```

### Cloud Shell Build Gate
Run:

```bash
pip install -r requirements-embeddings.txt
PYTHONPATH=. python scripts/build_vertex_embeddings.py
PYTHONPATH=. python scripts/smoke_vertex_embeddings.py
```

Expected behavior:

```text
embedding_model=text-embedding-005
vector_backend=faiss
queries resolve through BM25 + real Vertex semantic vectors
```

### Status
```text
Vertex embedding path verified on Cloud Shell
```

## Layer 4F - Retrieval Ranking Refinement

### Goal
Prefer specific service pages over the homepage when the query clearly asks about a medical service.

### Logic
The homepage contains broad content and can score highly for many exact terms. Service-specific queries should resolve to the most relevant service page when available.

Implemented policy:

```text
service-intent query terms -> boost matching service page
service-intent query terms -> dampen homepage unless title directly matches
```

Examples:

```text
PCOS/endometriosis -> service5
IVF/ICSI -> service2
fertility preservation -> service4
```

### Implemented Components
```text
backend/retrieval/ranking.py
HybridRetriever applies service ranking policy after hybrid score fusion
```

### Verification Gate
Run:

```bash
PYTHONPATH=. python scripts/smoke_hybrid_retrieval.py
PYTHONPATH=. python -m pytest -p no:cacheprovider
```

Current local result:

```text
PCOS/endometriosis query resolves to WEB-DRMADHU-006 / service5
21 tests passed
```

### Status
```text
retrieval ranking refinement verified on Cloud Shell with Vertex vectors
```

## Layer 4G - Agent Retrieval Integration

### Goal
Connect the production retrieval artifacts to the agent path before any web-search fallback.

### Logic
The agent should answer from controlled local knowledge first. Google Search should be a fallback, not the first retrieval layer.

```text
user question
-> orchestrator
-> FaqTools
-> stored FAQ rows, if present
-> approved website corpus
-> Vertex embedding artifact, if present
-> hybrid retrieval with ranking policy
-> web_search_agent only if confidence is too low
```

### Construction Steps
1. Make `FaqTools` embedding-artifact aware.
2. Load `drmadhupatil_vertex_embeddings.jsonl` when it exists.
3. Use Vertex query embeddings with the same `text-embedding-005` model.
4. Fall back to hash-vector retrieval if embeddings are missing or incomplete.
5. Keep manually maintained FAQ rows first, because direct business answers should override website corpus matches.
6. Add an agent-level smoke test for the real retrieval path.

### Verification Gate
Run locally or in Cloud Shell after embeddings have been built:

```bash
PYTHONPATH=. python scripts/smoke_agent_vertex_retrieval.py
PYTHONPATH=. python -m pytest -p no:cacheprovider
```

Expected smoke behavior:

```text
PCOS/endometriosis -> WEB-DRMADHU-006, mode=hybrid_vertex
IVF/ICSI -> WEB-DRMADHU-003, mode=hybrid_vertex
fertility preservation -> WEB-DRMADHU-005, mode=hybrid_vertex
```

### Status
```text
FaqTools connected to real Vertex embedding artifacts
local fallback modes preserved
Cloud Shell agent-level smoke verified
35 tests passed after imported-bundle and answer-formatting updates
```

## Layer 4H - Metadata Enrichment

### Goal
Add business-useful metadata so retrieval can filter by service, condition, treatment, page type, and appointment eligibility before ranking.

### Logic
Embeddings are good at semantic similarity, but business routing needs controlled metadata. The enrichment layer is deterministic so retrieval decisions remain explainable.

```text
approved RAG corpus
-> deterministic metadata rules
-> enriched RAG corpus
-> inferred query filters
-> filtered hybrid retrieval
-> fallback to unfiltered retrieval if filters are too strict
```

### Construction Steps
1. Add `backend/retrieval/metadata.py` with service-page business metadata rules.
2. Add `backend/retrieval/filters.py` to infer metadata filters from user questions.
3. Add `scripts/enrich_rag_metadata.py` to generate the enriched corpus and manifest.
4. Update default corpus paths to `07_output_enriched_documents`.
5. Extend `HybridRetriever` filters to support list fields such as `conditions` and `treatments`.
6. Update `FaqTools` to apply inferred metadata filters before normal hybrid ranking.
7. Preserve fallback to unfiltered retrieval when metadata filters miss.
8. Add metadata enrichment and filtering tests.

### Verification Gate
Run:

```bash
PYTHONPATH=. python scripts/enrich_rag_metadata.py
PYTHONPATH=. python scripts/smoke_hybrid_retrieval.py
PYTHONPATH=. python -m pytest -p no:cacheprovider
```

Expected:

```text
documents=8
page_types={'homepage': 1, 'service': 6, 'blog': 1}
PCOS/endometriosis -> WEB-DRMADHU-006
IVF/ICSI -> WEB-DRMADHU-003
fertility preservation -> WEB-DRMADHU-005
26 tests passed
```

### Status
```text
metadata enrichment implemented locally
enriched corpus generated
metadata-aware filtering verified locally
Cloud Shell verification complete
```

## Layer 5 - API Layer

### Goal
Expose the backend orchestrator as HTTP endpoints so external clients can call the system before Cloud Run deployment.

### Logic
Keep the API thin. Route handlers should validate request shape, call the existing orchestrator, and return JSON. Retrieval, storage, tickets, memory, and escalation remain in backend services/tools.

```text
client
-> FastAPI
-> SupportOrchestrator
-> FaqTools / TicketTools / EscalationTools
-> StorageService
```

### Construction Steps
1. Add `backend/api/runtime.py` for health, metadata status, storage factory, and smoke queries.
2. Add `backend/api/app.py` with FastAPI routes.
3. Add `requirements-api.txt` so API dependencies stay separate from core test dependencies.
4. Add `scripts/smoke_api_local.py` to test API behavior with FastAPI `TestClient`.
5. Add runtime tests that do not require FastAPI installation.

### Verification Gate
Run core tests:

```bash
PYTHONPATH=. python -m pytest -p no:cacheprovider
```

Run API smoke after installing API dependencies:

```bash
pip install -r requirements-api.txt
PYTHONPATH=. python scripts/smoke_api_local.py
```

Run server:

```bash
PYTHONPATH=. uvicorn backend.api.app:app --host 0.0.0.0 --port 8080
```

### Status
```text
API layer implemented and verified in Cloud Shell
35 tests passed
API smoke passed
```

## Construction Order
The intended build sequence is:

```text
GCP foundation
-> storage
-> agents
-> RAG corpus
-> hybrid retrieval
-> Vertex embeddings
-> metadata enrichment
-> API
-> deployment
-> usecase-1 specialization
```

Each layer should document:

```text
goal
logic
construction steps
verification gate
status
```


## Deferred - Corpus Refresh Automation

Future automation should refresh the corpus only when website content changes.

Target future flow:

```text
crawl website
-> rebuild RAG corpus
-> compare content hashes
-> rebuild embeddings if changed
-> rebuild FAISS
-> run retrieval smoke
-> write refresh report
```

Status:

```text
deferred until baseline completion
```

## Latest Verified Checkpoint - 2026-06-28

### Goal
Record the current handoff-ready state after integrating the doctor RAG demo knowledge bundle into the main multi-agent backend.

### Completed
```text
doctor RAG demo exported knowledge bundle
main project imported bundle into backend/knowledge/latest
runtime prefers imported bundle when corpus.jsonl and embeddings.jsonl exist
patient-friendly answer formatter copied from rag-usecase-0 into main backend
FastAPI /chat returns polished answer instead of raw RAG headings
retrieval metadata remains available in data.retrieval
```

### Verified Cloud Shell Result
```text
pytest: 35 passed
/metadata/status: knowledge_source=imported_bundle
/retrieval/smoke: 3 correct service-page hits
/chat: polished patient answer
```

### Current Running Path
```text
FastAPI
-> SupportOrchestrator
-> triage_agent
-> FaqTools
-> backend/knowledge/latest
-> Vertex query embedding
-> hybrid retrieval
-> patient-friendly formatter
```

### Next Layer
```text
main mobile frontend
Cloud Run deployment for main multi-agent demo
web_search_agent gating tests
later Vertex Session/Memory integration
```
