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
16 tests passed
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
16 tests passed
```

### Status
```text
RAG corpus and hybrid retrieval implemented locally and verified on Cloud Shell
```

## Layer 4E - Vertex AI Embeddings

### Goal
Replace the temporary hash-vector path with real semantic embeddings while keeping BM25 keyword retrieval and FAISS hybrid search.

### Logic
FAISS is the vector search engine. Vertex AI `text-embedding-005` creates the semantic vectors that go into FAISS.

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
Vertex embedding code implemented locally - pending Cloud Shell embedding build
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

