# Knowledge Export -> Import -> Test Runbook

Project role: main multi-agent `usecase-0-v2` is the runtime consumer.  
Knowledge source: `rag-usecase-0` doctor RAG demo.

Use this runbook whenever a new doctor-approved knowledge bundle is exported from the RAG demo and must be tested inside the main multi-agent system.

## 1. What This Folder Does

This folder owns the main usecase-0 runtime:

- support orchestrator
- triage agent
- FAQ/RAG tools
- ticket agent
- escalation agent
- web search fallback
- FastAPI runtime
- tests and smoke checks

It should not receive the entire RAG demo folder. It should consume only the exported knowledge bundle.

## 2. Weekly Knowledge Flow

```text
rag-usecase-0
        ↓
exports/latest/
        ↓
backend/knowledge/latest/
        ↓
main triage_agent / FaqTools / retrieval layer
        ↓
tests
        ↓
deployment when ready
```

## 3. Expected Import Destination

Use this folder as the main project knowledge input:

```text
backend/knowledge/latest/
```

Expected files after import:

```text
backend/knowledge/latest/corpus.jsonl
backend/knowledge/latest/metadata_manifest.json
backend/knowledge/latest/embeddings.jsonl
backend/knowledge/latest/prompt_policy.md
backend/knowledge/latest/faq_exact_answers.py
backend/knowledge/latest/content_version.json
backend/knowledge/latest/README.md
```

## 4. Data Formats

### `corpus.jsonl`

JSON Lines file. One RAG document per line.

Expected fields include:

```json
{
  "doc_id": "WEB-DRMADHU-001",
  "source_type": "website",
  "usecase": "doctor_appointment",
  "domain": "drmadhupatil.com",
  "page_id": "00_Homepage",
  "title": "Dr. Madhu Patil | Gynecologist & IVF Specialist",
  "url": "https://drmadhupatil.com/",
  "canonical_url": "https://drmadhupatil.com",
  "content": "clean RAG text",
  "metadata": {}
}
```

### `metadata_manifest.json`

JSON manifest with corpus/enrichment metadata.

### `embeddings.jsonl`

JSON Lines embedding artifact. It should map document ids to embedding vectors.

Expected concept:

```json
{
  "doc_id": "WEB-DRMADHU-001",
  "embedding": [0.01, 0.02, 0.03]
}
```

### `prompt_policy.md`

Final patient-companion prompt policy from the RAG demo.

### `faq_exact_answers.py`

Deterministic answer layer for high-value clinic questions.

### `content_version.json`

Audit manifest for the imported knowledge bundle.

Check this file first when debugging knowledge mismatch.

## 5. Export From RAG Demo

Run from RAG demo:

```bash
cd /Users/jhonny001/Desktop/rag-usecase-0
scripts/run_full_knowledge_sync.sh \
  "/Users/jhonny001/Desktop/GenAi Notes/Final_GenAi/Ai Agents/GCP/Customer_support_MultiAgents/implementation/usecase-0-v2/backend/knowledge/latest"
```

Or run step by step:

```bash
cd /Users/jhonny001/Desktop/rag-usecase-0
PYTHONPATH=backend backend/.venv/bin/python scripts/build_vertex_embeddings.py
python3 scripts/export_knowledge_bundle.py
```

Validate:

```bash
ls -la exports/latest
sed -n '1,160p' exports/latest/content_version.json
```

Make sure:

```text
exports/latest/embeddings.jsonl exists
missing_source_files is empty
```

## 6. Import Into This Main Project

Run from RAG demo:

```bash
cd /Users/jhonny001/Desktop/rag-usecase-0
python3 scripts/import_knowledge_bundle.py \
  exports/latest \
  "/Users/jhonny001/Desktop/GenAi Notes/Final_GenAi/Ai Agents/GCP/Customer_support_MultiAgents/implementation/usecase-0-v2/backend/knowledge/latest"
```

Then confirm from this main project:

```bash
cd "/Users/jhonny001/Desktop/GenAi Notes/Final_GenAi/Ai Agents/GCP/Customer_support_MultiAgents/implementation/usecase-0-v2"
ls -la backend/knowledge/latest
sed -n '1,160p' backend/knowledge/latest/content_version.json
```

## 7. Runtime Wiring

Current main project config uses:

```text
backend/config.py
DATA_DIR
KNOWLEDGE_DIR
EMBEDDING_MODEL_NAME
```

The runtime now prefers a complete imported bundle in `backend/knowledge/latest`.

Runtime mapping:

```text
RAG corpus        -> backend/knowledge/latest/corpus.jsonl
Metadata manifest -> backend/knowledge/latest/metadata_manifest.json
Embeddings        -> backend/knowledge/latest/embeddings.jsonl
Prompt policy     -> backend/knowledge/latest/prompt_policy.md
FAQ exact layer    -> backend/knowledge/latest/faq_exact_answers.py
```

If `backend/knowledge/latest/corpus.jsonl` or `backend/knowledge/latest/embeddings.jsonl` is missing, the runtime falls back to the older checked-in `rag_pipeline` corpus and embedding artifact paths.

## 8. Test Commands

From this main project:

```bash
cd "/Users/jhonny001/Desktop/GenAi Notes/Final_GenAi/Ai Agents/GCP/Customer_support_MultiAgents/implementation/usecase-0-v2"
PYTHONPATH=. python -m pytest -p no:cacheprovider
```

Smoke tests:

```bash
PYTHONPATH=. python scripts/smoke_hybrid_retrieval.py
PYTHONPATH=. python scripts/smoke_agent_vertex_retrieval.py
PYTHONPATH=. python scripts/smoke_api_local.py
```

Expected historical baseline:

```text
35 tests passed
API smoke passed
agent Vertex retrieval smoke passed
```

Current verified Cloud Shell result:

```text
pytest: 35 passed
metadata_status.knowledge_source=imported_bundle
smoke_agent_vertex_retrieval:
  PCOS/endometriosis -> WEB-DRMADHU-006, hybrid_vertex
  IVF/ICSI -> WEB-DRMADHU-003, hybrid_vertex
  fertility preservation -> WEB-DRMADHU-005, hybrid_vertex
smoke_api_local:
  health 200 ok
  metadata 200 ok 8
  chat 200 triage_agent WEB-DRMADHU-006 hybrid_vertex
  retrieval_smoke 200 3
```

Manual API route checks:

```bash
curl http://localhost:8080/health
curl http://localhost:8080/metadata/status
curl http://localhost:8080/retrieval/smoke
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Can Dr Madhu help with PCOS and endometriosis?","user_id":"guest","session_id":"manual-test"}'
```

Expected `/chat` response shape:

```text
message: patient-friendly max-4-bullet answer
data.retrieval.doc_id: WEB-DRMADHU-006
data.retrieval.mode: hybrid_vertex
data.retrieval.score: 1.0
```

Important route note:

```text
Use /metadata/status. /metadata is not currently registered.
```

## 9. Acceptance Criteria

Before main deployment:

- Imported bundle exists in `backend/knowledge/latest/`.
- `content_version.json` has the expected knowledge version.
- `embeddings.jsonl` exists.
- Main tests pass.
- Smoke tests pass.
- Triage/RAG answers use local clinic knowledge first.
- `/chat` returns the patient-friendly formatted answer, not raw RAG headings.
- Web search is not used for clinic-owned questions unless policy allows it.

## 10. Deployment Rule

Do not deploy main project only because RAG demo docs changed.

Deploy main project only after:

- new knowledge bundle is imported
- runtime is wired to the imported bundle
- tests pass
- smoke tests pass

## 11. One-Line Reminder

```text
Main project consumes exported knowledge. It does not absorb the full RAG demo.
```

## 12. Cloud Shell ADC Reminder

Live Vertex query embedding smoke tests require Application Default Credentials to be forced to user ADC in each fresh Cloud Shell session.

Run before `smoke_agent_vertex_retrieval.py`, `smoke_api_local.py`, or manual `/chat` calls that trigger Vertex query embeddings:

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

If this is skipped, the likely error is:

```text
google.auth.exceptions.RefreshError: Unexpected response from metadata server: service account info is missing 'email' field.
```
