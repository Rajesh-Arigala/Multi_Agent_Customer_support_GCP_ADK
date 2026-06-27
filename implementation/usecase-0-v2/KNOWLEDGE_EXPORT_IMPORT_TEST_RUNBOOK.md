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
EMBEDDING_MODEL_NAME
```

Until the runtime is fully wired to `backend/knowledge/latest`, treat imported files as the approved weekly knowledge package.

Future runtime mapping should be:

```text
RAG corpus        -> backend/knowledge/latest/corpus.jsonl
Metadata manifest -> backend/knowledge/latest/metadata_manifest.json
Embeddings        -> backend/knowledge/latest/embeddings.jsonl
Prompt policy     -> backend/knowledge/latest/prompt_policy.md
FAQ exact layer    -> backend/knowledge/latest/faq_exact_answers.py
```

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
31 tests passed
API smoke passed
agent Vertex retrieval smoke passed
```

## 9. Acceptance Criteria

Before main deployment:

- Imported bundle exists in `backend/knowledge/latest/`.
- `content_version.json` has the expected knowledge version.
- `embeddings.jsonl` exists.
- Main tests pass.
- Smoke tests pass.
- Triage/RAG answers use local clinic knowledge first.
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
