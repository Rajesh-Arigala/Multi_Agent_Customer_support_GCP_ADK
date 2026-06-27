# Layer 5 - API Execution Log

## Goal
Expose the existing backend orchestrator through a small HTTP API so the agent can be called from Postman, frontend clients, Cloud Run, and later deployment flows.

## API Surface

```text
GET  /health
GET  /metadata/status
POST /chat
GET  /retrieval/smoke
```

## Construction

Added:

```text
backend/api/__init__.py
backend/api/runtime.py
backend/api/app.py
scripts/smoke_api_local.py
requirements-api.txt
tests/test_api_runtime.py
```

The API remains thin:

```text
HTTP request
-> FastAPI route
-> build_support_orchestrator
-> existing tools/retrieval/storage
-> JSON response
```

## Runtime Storage

`STORAGE_BACKEND` controls storage:

```text
csv            local CSV storage, default
google_sheets  Google Sheets storage using ADC/service account credentials
```

CSV runtime data defaults to `DATA_DIR`. Google Sheets uses `GOOGLE_SHEETS_ID`.

## Endpoint Behavior

### GET /health
Returns service status, project, location, and storage backend.

### GET /metadata/status
Returns enriched corpus and embedding artifact status.

### POST /chat
Payload:

```json
{
  "message": "Can Dr Madhu help with PCOS and endometriosis?",
  "user_id": "guest",
  "session_id": "api-smoke"
}
```

Returns the existing orchestrator response.

### GET /retrieval/smoke
Runs three representative retrieval questions through the orchestrator and returns the selected document IDs, modes, and scores.

## Local Verification

FastAPI is intentionally kept in `requirements-api.txt`, separate from the core test requirements.

Core local verification:

```bash
PYTHONPATH=. python -m pytest -p no:cacheprovider
```

Result:

```text
31 passed
```

API syntax verification:

```text
backend/api/app.py compiles
backend/api/runtime.py compiles
scripts/smoke_api_local.py compiles
```

## Cloud Shell Verification Gate

After pulling the code in Cloud Shell:

```bash
cd ~/Multi_Agent_Customer_support_GCP_ADK/implementation/usecase-0-v2
source ../.venv/bin/activate
pip install -r requirements-api.txt
PYTHONPATH=. python scripts/smoke_api_local.py
PYTHONPATH=. python -m pytest -p no:cacheprovider
```

Expected API smoke output:

```text
health 200 ok
metadata 200 ok 8
chat 200 triage_agent WEB-DRMADHU-006 hybrid_vertex
retrieval_smoke 200 3
```

## Run Server

Local/Cloud Shell server:

```bash
PYTHONPATH=. uvicorn backend.api.app:app --host 0.0.0.0 --port 8080
```

Example request:

```bash
curl -X POST http://127.0.0.1:8080/chat   -H "Content-Type: application/json"   -d '{"message":"Do you provide IVF and ICSI treatment?","user_id":"guest","session_id":"manual"}'
```

## Status

```text
Layer 5 API implemented and locally verified.
Cloud Shell API dependency install and smoke pending.
```
