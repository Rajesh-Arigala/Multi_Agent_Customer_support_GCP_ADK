# Current Status - Usecase 0 v2

Last updated: 2026-06-28

## Executive Summary

`usecase-0-v2` now has a verified main backend path for the doctor RAG demo:

```text
FastAPI /chat
-> SupportOrchestrator
-> triage_agent
-> FaqTools
-> imported doctor knowledge bundle
-> Vertex text-embedding-005 query embedding
-> BM25 + Vertex-vector hybrid retrieval
-> patient-friendly answer formatter
-> JSON response with retrieval metadata
```

This is enough for a backend/API demo. The full target multi-agent architecture is not fully complete yet because Cloud Run deployment, mobile frontend, Vertex Session Service, and Vertex Memory Bank are still future layers.

## What Is Running

Verified in Cloud Shell:

```text
GET  /health             -> ok
GET  /metadata/status    -> imported_bundle active
GET  /retrieval/smoke    -> 3/3 correct service-page hits
POST /chat               -> polished patient-facing answer
pytest                   -> 35 passed
```

The active knowledge source is:

```text
backend/knowledge/latest/corpus.jsonl
backend/knowledge/latest/embeddings.jsonl
```

The active bundle version is:

```text
2026_06_28_knowledge_bundle
```

## Verified Retrieval Hits

```text
PCOS/endometriosis       -> WEB-DRMADHU-006 / service5 / hybrid_vertex
IVF/ICSI                 -> WEB-DRMADHU-003 / service2 / hybrid_vertex
fertility preservation   -> WEB-DRMADHU-005 / service4 / hybrid_vertex
```

## Patient Answer Layer

The main backend now uses the same deterministic answer-presentation policy developed in the doctor RAG demo.

Answer rules:

```text
maximum 4 bullets
warm clinic-assistant tone
icons/smileys allowed
Dr. Madhu Patil’s Clinic phrasing for services
Dr. Madhu Patil’s team phrasing for appointment/help coordination
no raw RAG heading dumps
source and score retained in data.retrieval
```

Example `/chat` answer:

```text
🩺 **Yes.** Dr. Madhu Patil’s Clinic offers Endometriosis & PCOS.
🔎 This is relevant to treatments such as pcos care, endometriosis care, and hormonal evaluation and conditions such as pcos, endometriosis, irregular periods, and hormonal issues.
📅 For personal guidance, __booking a consultation__ is the best next step.
```

## Architecture Status

```text
RAG knowledge factory                  ✅ complete in rag-usecase-0
Knowledge export/import pipeline        ✅ complete
Imported bundle runtime detection       ✅ complete
Vertex embedding query path             ✅ complete, requires ADC in Cloud Shell
Patient-friendly answer formatter       ✅ complete
FastAPI backend                         ✅ complete locally / Cloud Shell
ticket_agent                            🟡 implemented, basic tests pass
escalation_agent                        🟡 implemented, basic tests pass
web_search_agent fallback               🟡 exists, needs stricter clinic-owned gating
local memory and audit                  🟡 implemented locally
mobile frontend for main demo           ❌ next
Cloud Run deployment for main demo      ❌ next
VertexAiSessionService                  ❌ later
VertexAiMemoryBankService               ❌ later
```

## Cloud Shell ADC Requirement

Live Vertex query embedding calls require ADC to be forced to user credentials in each fresh Cloud Shell session.

Run before Vertex smoke tests:

```bash
gcloud auth application-default login \
  --scopes=https://www.googleapis.com/auth/cloud-platform

gcloud auth application-default set-quota-project multi-agent-adk-1

export GOOGLE_CLOUD_PROJECT=multi-agent-adk-1
export GOOGLE_GENAI_USE_VERTEXAI=true
export GOOGLE_CLOUD_LOCATION=us-central1
ADC_DIR="$(gcloud info --format='value(config.paths.global_config_dir)')"
export GOOGLE_APPLICATION_CREDENTIALS="$ADC_DIR/application_default_credentials.json"
```

Without this, Cloud Shell may try to use the default metadata credential and fail with:

```text
service account info is missing 'email' field
```

## Verification Commands

```bash
cd ~/Multi_Agent_Customer_support_GCP_ADK/implementation/usecase-0-v2
source ../.venv/bin/activate

PYTHONPATH=. python -m pytest -p no:cacheprovider
PYTHONPATH=. python scripts/smoke_agent_vertex_retrieval.py
PYTHONPATH=. python scripts/smoke_api_local.py
```

Run the API:

```bash
PYTHONPATH=. uvicorn backend.api.app:app --host 0.0.0.0 --port 8080
```

Manual checks:

```bash
curl http://localhost:8080/health
curl http://localhost:8080/metadata/status
curl http://localhost:8080/retrieval/smoke
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Can Dr Madhu help with PCOS and endometriosis?","user_id":"guest","session_id":"manual-test"}'
```

## Next Work

Recommended next sequence:

```text
1. Add a mobile-friendly frontend to main usecase-0-v2.
2. Keep the same polished answer UI pattern from rag-usecase-0.
3. Containerize main API + frontend for Cloud Run.
4. Deploy the main multi-agent demo to Cloud Run.
5. Run doctor/patient test questions on the deployed URL.
6. Add stricter web_search_agent gating for clinic-owned questions.
7. Later integrate real Vertex Session/Memory services.
```

## One-Line Handoff

```text
The main backend RAG path is verified; the next deliverable is a mobile frontend and Cloud Run deployment for the main multi-agent demo.
```
