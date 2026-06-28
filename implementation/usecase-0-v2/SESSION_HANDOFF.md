# Session Handoff - Usecase 0 v2

Last updated: 2026-06-28

Use this file first when opening a fresh Codex/Cloud Shell session.

## 1. Where The Project Lives

Local consolidated workspace:

```text
/Users/jhonny001/Desktop/4-Multi-Agents-customer-support
```

Two active projects:

```text
rag-usecase-0/
  Doctor RAG demo and knowledge factory.

Customer_support_MultiAgents/
  Main multi-agent project and production-oriented runtime.
```

Main usecase folder:

```text
Customer_support_MultiAgents/implementation/usecase-0-v2
```

Cloud Shell main folder:

```text
~/Multi_Agent_Customer_support_GCP_ADK/implementation/usecase-0-v2
```

## 2. Current Verified State

The main backend RAG path is working end to end.

```text
FastAPI /chat
-> SupportOrchestrator
-> triage_agent
-> FaqTools
-> backend/knowledge/latest imported bundle
-> Vertex text-embedding-005 query embedding
-> BM25 + Vertex-vector hybrid retrieval
-> patient-friendly answer formatter
-> JSON response with retrieval metadata
```

Verified in Cloud Shell:

```text
pytest: 35 passed
GET /health: ok
GET /metadata/status: imported_bundle active
GET /retrieval/smoke: 3 correct hits
POST /chat: polished answer, no raw headings
```

Active imported bundle:

```text
backend/knowledge/latest/corpus.jsonl
backend/knowledge/latest/embeddings.jsonl
backend/knowledge/latest/metadata_manifest.json
backend/knowledge/latest/prompt_policy.md
backend/knowledge/latest/faq_exact_answers.py
backend/knowledge/latest/content_version.json
```

Current bundle version:

```text
2026_06_28_knowledge_bundle
```

## 3. What Is Complete

```text
GCP foundation                         done
storage layer                          done
agent layer skeleton                   done
RAG corpus                             done
metadata enrichment                    done
Vertex document embeddings             done
knowledge export/import pipeline       done
main runtime imported-bundle detection done
FastAPI backend                        done
patient-friendly answer formatter      done
```

## 4. What Is Partially Complete

```text
ticket_agent              implemented, basic tests pass
escalation_agent          implemented, basic tests pass
web_search_agent fallback exists, needs stricter clinic-owned gating
memory_service            local memory only, not Vertex Memory Bank
audit_log                 local audit only
```

## 5. What Is Not Done Yet

```text
main mobile frontend
main Cloud Run deployment
VertexAiSessionService
VertexAiMemoryBankService
production auth/security for public demo
full ticket/appointment/eCRM business flow
web_search_agent gating policy tests
```

## 6. Start Commands In Cloud Shell

```bash
cd ~/Multi_Agent_Customer_support_GCP_ADK
git pull

cd ~/Multi_Agent_Customer_support_GCP_ADK/implementation/usecase-0-v2
source ../.venv/bin/activate
```

For live Vertex query embeddings, run ADC setup in every fresh Cloud Shell session:

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

If ADC is not set, Vertex calls may fail with:

```text
service account info is missing 'email' field
```

## 7. Verification Commands

Run tests:

```bash
PYTHONPATH=. python -m pytest -p no:cacheprovider
```

Expected:

```text
35 passed
```

Verify imported bundle:

```bash
PYTHONPATH=. python - <<'PY'
from backend.api.runtime import metadata_status
p = metadata_status()
print(p["knowledge_source"])
print(p["corpus_exists"], p["embeddings_exists"])
print(p["corpus_path"])
print(p["embeddings_path"])
PY
```

Expected:

```text
imported_bundle
True True
.../backend/knowledge/latest/corpus.jsonl
.../backend/knowledge/latest/embeddings.jsonl
```

Run smoke checks:

```bash
PYTHONPATH=. python scripts/smoke_agent_vertex_retrieval.py
PYTHONPATH=. python scripts/smoke_api_local.py
```

Expected service hits:

```text
PCOS/endometriosis     -> WEB-DRMADHU-006
IVF/ICSI               -> WEB-DRMADHU-003
fertility preservation -> WEB-DRMADHU-005
```

## 8. Run The API Locally In Cloud Shell

```bash
PYTHONPATH=. uvicorn backend.api.app:app --host 0.0.0.0 --port 8080
```

In another Cloud Shell tab:

```bash
curl http://localhost:8080/health
curl http://localhost:8080/metadata/status
curl http://localhost:8080/retrieval/smoke
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Can Dr Madhu help with PCOS and endometriosis?","user_id":"guest","session_id":"manual-test"}'
```

Important route note:

```text
/metadata/status is valid.
/metadata is not registered.
```

## 9. Expected Chat Response Style

The response should be patient-friendly, not raw RAG text.

Expected shape:

```text
🩺 **Yes.** Dr. Madhu Patil’s Clinic offers Endometriosis & PCOS.
🔎 This is relevant to treatments such as pcos care, endometriosis care, and hormonal evaluation and conditions such as pcos, endometriosis, irregular periods, and hormonal issues.
📅 For personal guidance, __booking a consultation__ is the best next step.
```

Retrieval proof remains in:

```text
data.retrieval.doc_id
data.retrieval.title
data.retrieval.url
data.retrieval.score
data.retrieval.keyword_score
data.retrieval.vector_score
data.retrieval.mode
data.retrieval.filter_mode
```

## 10. Knowledge Update Loop

The doctor RAG demo remains the knowledge factory.

Future content flow:

```text
doctor provides Q&A / articles / interviews / patient scenarios in markdown
-> curate into rag-usecase-0 content folders
-> rebuild RAG-ready corpus
-> rebuild Vertex embeddings
-> export knowledge bundle
-> import into main usecase-0-v2/backend/knowledge/latest
-> run tests and smoke checks
-> deploy main demo if needed
```

Runbook:

```text
KNOWLEDGE_EXPORT_IMPORT_TEST_RUNBOOK.md
```

## 11. Current Architecture Truth

The full diagram is not fully implemented yet.

Running:

```text
User/API -> FastAPI -> SupportOrchestrator -> triage_agent -> imported RAG -> formatted answer
```

Implemented but not demo-polished:

```text
ticket_agent
escalation_agent
web_search_agent
local memory
local audit
```

Not yet implemented:

```text
VertexAiSessionService
VertexAiMemoryBankService
main Cloud Run public demo
main mobile frontend
```

## 12. Next Recommended Work

Next sequence:

```text
1. Build mobile-friendly main frontend.
2. Reuse the rag-usecase-0 chat UI style.
3. Connect frontend to main /chat, /metadata/status, /retrieval/smoke.
4. Add Cloud Run deployment files for main usecase-0-v2.
5. Deploy main demo.
6. Run doctor-style test set on deployed URL.
7. Add web_search_agent gating so clinic-owned questions do not go to Google.
8. Later add real Vertex Session/Memory services.
```

## 13. Commit Hygiene

Before ending a session:

```bash
git status
PYTHONPATH=. python -m pytest -p no:cacheprovider
```

Document:

```text
what changed
what passed
what failed
next exact step
```

## 14. One-Line Reminder

```text
The RAG demo creates knowledge; the main project consumes knowledge and runs the multi-agent backend.
```
