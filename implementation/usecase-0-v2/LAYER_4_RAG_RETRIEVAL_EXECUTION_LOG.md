# Layer 4 Execution Log - RAG Corpus And Hybrid Retrieval

## Purpose
Record the completed Layer 4 work for `usecase-0-v2`.

Layer 4 prepares the trusted local knowledge base and retrieval path before the agent falls back to `web_search_agent`.

## Decision
Use a RABBIT-style corpus pipeline plus hybrid retrieval:

```text
RABBIT website corpus pipeline
+ BM25-style keyword retrieval with 1-gram, 2-gram, and 3-gram terms
+ vector retrieval with FAISS adapter
+ pure-Python vector fallback
+ metadata filtering
+ hybrid score fusion
+ confidence threshold
```

FAISS is optional at runtime. If `faiss-cpu` is installed, the vector retriever uses FAISS. If not, it falls back to a deterministic pure-Python vector scorer so local tests still run.

## Step 1 - Created Corpus Workspace
Created the doctor-site corpus workspace:

```text
rag_pipeline/drmadhupatil_corpus/
```

Copied the proven RABBIT crawler into this workspace:

```text
rag_pipeline/drmadhupatil_corpus/crawler_v4_site_crawler.py
```

Added crawl config:

```text
rag_pipeline/drmadhupatil_corpus/01_input_seed_and_config/drmadhupatil_crawl_config.json
```

Configured target:

```text
seed_url: https://drmadhupatil.com
same_domain_only: true
max_pages: 120
max_depth: 6
```

## Step 2 - Installed Temporary Crawler Runtime
Created a temporary local crawler environment outside the repo:

```text
/private/tmp/drmadhupatil-crawl-venv
```

Installed crawler dependencies:

```text
beautifulsoup4
ftfy
lxml
playwright
```

Installed Playwright Chromium.

## Step 3 - Fixed Render Wait Strategy
The first crawl reached `drmadhupatil.com`, but timed out on Playwright `networkidle`.

Reason:

```text
The site keeps background network requests open, so networkidle is not reliable.
```

Adjusted only the project-local crawler copy:

```text
wait_until="networkidle"
-> wait_until="domcontentloaded"
```

The original RABBIT project was not modified.

## Step 4 - Ran Full Site Crawl
Executed the crawler against:

```text
https://drmadhupatil.com
```

Generated staged outputs:

```text
02_output_raw_html_rendered/
03_output_structured_json/
04_output_clean_json/
05_output_clean_text/
06_output_rag_documents/
07_output_quality_reports_manifest/
```

Crawl result:

```text
pages crawled: 14
pages failed: 0
urls skipped: 6
internal links discovered: 14
```

## Step 5 - Prepared Approved RAG Corpus
Detected duplicate URL variants:

```text
/service1 and /service1.html
/service2 and /service2.html
/service3 and /service3.html
/service4 and /service4.html
/service5 and /service5.html
/service6 and /service6.html
```

Approved canonical documents:

```text
WEB-DRMADHU-001  homepage
WEB-DRMADHU-002  service1 - Fertility Assessment
WEB-DRMADHU-003  service2 - IVF & ICSI
WEB-DRMADHU-004  service3 - IUI
WEB-DRMADHU-005  service4 - Fertility Preservation
WEB-DRMADHU-006  service5 - Endometriosis & PCOS
WEB-DRMADHU-007  service6 - Immunotherapy in Infertility
WEB-DRMADHU-008  blog
```

Created approved retrieval input:

```text
rag_pipeline/drmadhupatil_corpus/06_output_rag_documents_ready/drmadhupatil_rag_corpus.jsonl
```

Created quality/report artifacts:

```text
rag_pipeline/drmadhupatil_corpus/07_output_quality_reports_manifest/crawl_manifest.json
rag_pipeline/drmadhupatil_corpus/07_output_quality_reports_manifest/drmadhupatil_corpus_manifest.json
rag_pipeline/drmadhupatil_corpus/07_output_quality_reports_manifest/drmadhupatil_RAG_Readiness_Report.md
```

## Step 6 - Added Hybrid Retrieval Layer
Added retrieval package:

```text
backend/retrieval/
```

Files:

```text
backend/retrieval/__init__.py
backend/retrieval/models.py
backend/retrieval/text.py
backend/retrieval/loader.py
backend/retrieval/keyword.py
backend/retrieval/vector.py
backend/retrieval/hybrid.py
```

Implemented:

```text
RetrievalDocument
RetrievalResult
JSONL corpus loader
FAQ-row-to-document loader
BM25-style keyword scorer with 1-gram, 2-gram, and 3-gram terms
hash-based vector scorer
FAISS adapter when faiss is installed
metadata filters
hybrid score fusion
confidence threshold
title-overlap boost
```

## Step 7 - Connected Retrieval To Agent Triage
Updated:

```text
backend/tools/faq_tools.py
```

Behavior:

```text
1. If FAQ rows exist in storage, retrieve from FAQ rows.
2. If no FAQ rows exist, retrieve from the approved website corpus.
3. If best score passes threshold, return local answer.
4. If no result passes threshold, allow orchestrator fallback to web_search_agent.
```

This keeps existing generic usecase-0 behavior while enabling usecase-1 website RAG.

## Step 8 - Added Smoke And Tests
Added smoke script:

```text
scripts/smoke_hybrid_retrieval.py
```

Added tests:

```text
tests/test_hybrid_retrieval.py
```

Added optional FAISS install file:

```text
requirements-retrieval.txt
```

## Step 9 - Verified Retrieval Behavior
Smoke command:

```bash
PYTHONPATH=. python3 scripts/smoke_hybrid_retrieval.py
```

Observed local result:

```text
documents=8
vector_backend=python
IVF query -> WEB-DRMADHU-003 / service2
PCOS and endometriosis query -> WEB-DRMADHU-006 / service5
fertility preservation query -> WEB-DRMADHU-005 / service4
```

Note:

```text
vector_backend=python locally because FAISS was not installed in the local default Python.
Cloud Shell should report vector_backend=faiss after installing requirements-retrieval.txt.
```

## Step 10 - Verified Regression Tests
Created temporary test venv:

```text
/private/tmp/usecase0-v2-test-venv
```

Ran:

```bash
PYTHONPATH=. /private/tmp/usecase0-v2-test-venv/bin/python -m pytest -p no:cacheprovider
```

Result:

```text
14 passed
```

Covered:

```text
agent routing
ticket lifecycle
escalation
memory/audit
CSV store
sheet schema
RAG corpus loading
hybrid retrieval
metadata filtering
FAQ retrieval compatibility
```

## Step 11 - Updated Documentation
Updated:

```text
README.md
CONSTRUCTION_STEPS.md
GCP_FOUNDATION.md
```

Documented:

```text
RAG corpus path
hybrid retrieval method
smoke command
test result
Layer 4 status
```

## Step 12 - Added N-Gram Phrase Retrieval
Added 1-gram, 2-gram, and 3-gram terms to BM25 keyword retrieval.

Purpose:

```text
Improve phrase-sensitive matches such as:
fertility preservation
IVF ICSI treatment
PCOS endometriosis
immunotherapy infertility
```

Added helper:

```text
backend/retrieval/text.py -> tokenize_with_ngrams()
```

Updated:

```text
backend/retrieval/keyword.py
tests/test_hybrid_retrieval.py
```

Verification after n-gram refinement:

```text
hybrid retrieval smoke passed
18 tests passed
```

## Step 13 - Added Vertex AI Embedding Path
Implemented the real semantic embedding path using:

```text
text-embedding-005
project: multi-agent-adk-1
location: us-central1
```

Added:

```text
backend/retrieval/vertex_embeddings.py
backend/retrieval/embedding_store.py
scripts/build_vertex_embeddings.py
scripts/smoke_vertex_embeddings.py
requirements-embeddings.txt
tests/test_vertex_embedding_path.py
```

Extended:

```text
backend/retrieval/vector.py
backend/retrieval/hybrid.py
backend/config.py
```

Behavior:

```text
Build document embeddings with Vertex AI.
Persist vectors as JSONL.
Write a FAISS index artifact when faiss is installed.
Embed user queries with the same Vertex model.
Use BM25 + Vertex-vector hybrid scoring.
```

Local verification uses a fake embedding model so tests do not call Vertex:

```text
18 tests passed
```

Historical note: at this step, Cloud Shell verification still needed to run in GCP.
This was completed later in Step 15 and again after the imported-bundle integration.

Added `tests/test_script_syntax.py` after Cloud Shell exposed a syntax issue in the embedding build script. This compiles project scripts into a temporary pytest directory and prevents repo `__pycache__` churn.

Handled Vertex SDK deprecation warning by migrating the embedding wrapper from:

```text
vertexai.language_models.TextEmbeddingModel
```

to the supported Google Gen AI SDK path:

```text
google.genai.Client(vertexai=True, project=..., location=..., http_options=HttpOptions(api_version="v1"))
client.models.embed_content(model="text-embedding-005", ...)
```

Updated:

```text
backend/retrieval/vertex_embeddings.py
requirements-embeddings.txt
```

## Step 14 - Added Service-Page Ranking Policy
Added deterministic ranking refinement so service-specific medical queries prefer service pages over the broad homepage.

Added:

```text
backend/retrieval/ranking.py
```

Updated:

```text
backend/retrieval/hybrid.py
tests/test_hybrid_retrieval.py
```

Policy:

```text
If query contains known service terms, boost matching service page IDs.
If query contains service terms and document is homepage, apply a small dampening factor.
```

Verified locally:

```text
PCOS/endometriosis -> WEB-DRMADHU-006 / service5
IVF/ICSI -> WEB-DRMADHU-003 / service2
fertility preservation -> WEB-DRMADHU-005 / service4
18 tests passed
```

Historical note: real Vertex-vector verification was pending at this step.
This was completed later in Step 15.

## Step 15 - Cloud Shell Verification For Vertex Embeddings And Ranking
Verified the real Vertex embedding path and service-page ranking refinement in Cloud Shell.

Environment:

```text
project: multi-agent-adk-1
location: us-central1
embedding model: text-embedding-005
SDK path: google-genai on Vertex AI
vector backend: faiss
```

Cloud Shell commands run:

```bash
PYTHONPATH=. python scripts/build_vertex_embeddings.py
PYTHONPATH=. python scripts/smoke_vertex_embeddings.py
PYTHONPATH=. python -m pytest -p no:cacheprovider
```

Embedding build result:

```text
embedded 8/8
documents=8
dimensions=768
faiss_index_written=True
```

Smoke result:

```text
IVF/ICSI -> WEB-DRMADHU-003 / service2
PCOS/endometriosis -> WEB-DRMADHU-006 / service5
fertility preservation -> WEB-DRMADHU-005 / service4
hormonal irregular periods -> WEB-DRMADHU-006 / service5
```

Test result:

```text
26 passed
```

Status:

```text
Layer 4E Vertex embeddings verified on Cloud Shell.
Layer 4F service-page ranking refinement verified on Cloud Shell.
```

## Step 16 - Connected Retrieval Artifacts To Agent FAQ Tool
Connected the real retrieval artifacts into `FaqTools`, which is the local knowledge lookup used by the orchestrator before web-search fallback.

What changed:

```text
backend/tools/faq_tools.py
scripts/smoke_agent_vertex_retrieval.py
tests/test_faq_tools_vertex_mode.py
```

Retrieval behavior:

```text
FAQ rows present -> use FAQ rows first with local hybrid fallback
No FAQ rows -> load approved website RAG corpus
Vertex embedding JSONL exists -> use BM25 + Vertex-vector hybrid retrieval
Embedding artifact missing/incomplete -> use hash-vector hybrid fallback
```

Response retrieval modes:

```text
hybrid_vertex
hybrid_hash
hybrid_hash_missing_vectors
```

Local verification completed:

```bash
PYTHONPATH=. python -m pytest -p no:cacheprovider
```

Result:

```text
26 passed
```

Script syntax verification completed:

```text
scripts/smoke_agent_vertex_retrieval.py compiles
scripts/smoke_vertex_embeddings.py compiles
scripts/build_vertex_embeddings.py compiles
```

Cloud Shell next gate:

```bash
PYTHONPATH=. python scripts/smoke_agent_vertex_retrieval.py
PYTHONPATH=. python -m pytest -p no:cacheprovider
```

Expected Cloud Shell agent smoke:

```text
PCOS/endometriosis -> WEB-DRMADHU-006, mode=hybrid_vertex
IVF/ICSI -> WEB-DRMADHU-003, mode=hybrid_vertex
fertility preservation -> WEB-DRMADHU-005, mode=hybrid_vertex
```

Status:

```text
Layer 4G was implemented and locally verified at this point.
Cloud Shell agent-level smoke was completed later after imported-bundle wiring.
```

## Step 17 - Metadata Enrichment Layer
Added deterministic business metadata to the approved RAG corpus so retrieval can filter before scoring.

New files:

```text
backend/retrieval/metadata.py
backend/retrieval/filters.py
scripts/enrich_rag_metadata.py
tests/test_metadata_enrichment.py
```

New generated artifacts:

```text
rag_pipeline/drmadhupatil_corpus/07_output_enriched_documents/drmadhupatil_enriched_rag_corpus.jsonl
rag_pipeline/drmadhupatil_corpus/07_output_enriched_documents/metadata_enrichment_manifest.json
```

Metadata fields added:

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

Filtering behavior added:

```text
conditions list membership
treatments list membership
appointment_eligible boolean filtering
metadata-filtered search with unfiltered fallback
```

Generation command:

```bash
PYTHONPATH=. python scripts/enrich_rag_metadata.py
```

Generation result:

```text
RAG metadata enriched
documents=8
page_types={'homepage': 1, 'service': 6, 'blog': 1}
```

Local smoke result:

```text
PCOS/endometriosis -> WEB-DRMADHU-006
IVF/ICSI -> WEB-DRMADHU-003
fertility preservation -> WEB-DRMADHU-005
```

Local test result:

```text
26 passed
```

Embedding note:

```text
Existing Vertex embeddings remain compatible because vectors are keyed by doc_id and searchable_text has not changed.
Rebuild embeddings only if document text changes or if metadata is intentionally added to searchable_text.
```

Cloud Shell next gate:

```bash
PYTHONPATH=. python scripts/enrich_rag_metadata.py
PYTHONPATH=. python scripts/smoke_hybrid_retrieval.py
PYTHONPATH=. python scripts/smoke_agent_vertex_retrieval.py
PYTHONPATH=. python -m pytest -p no:cacheprovider
```

Status:

```text
Layer 4H was implemented and locally verified at this point.
Cloud Shell verification was completed later after imported-bundle wiring.
```

## Future Note - Corpus Refresh Automation
Do not implement now. Future automation should refresh the corpus when website content changes.

Candidate future pipeline:

```text
crawl website
-> rebuild RAG corpus
-> compare content hashes
-> rebuild embeddings only if changed
-> rebuild FAISS index
-> run retrieval smoke
-> write refresh report
```

Potential future command:

```bash
PYTHONPATH=. python scripts/refresh_rag_corpus.py --if-changed
```

This is intentionally deferred until the current baseline is complete.

## Step 12 - Cleanliness Check
Checked for unwanted local artifacts:

```text
.DS_Store
__pycache__
.pytest_cache
```

Result:

```text
none found under implementation/usecase-0-v2
```

## Cloud Shell Verification Commands
After pushing and pulling in Cloud Shell:

```bash
cd ~/Multi_Agent_Customer_support_GCP_ADK/implementation/usecase-0-v2
source ../.venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-retrieval.txt
PYTHONPATH=. python scripts/smoke_hybrid_retrieval.py
PYTHONPATH=. python -m pytest -p no:cacheprovider
```

Expected:

```text
vector_backend=faiss
hybrid retrieval smoke passes
14 tests pass
```

## Status
```text
Historical status before Cloud Shell completion.
Superseded by Step 15, Step 18, and Step 19 below.
```

## Step 18 - Imported Doctor RAG Bundle Connected To Main Runtime

Date: 2026-06-28

Connected the standalone `rag-usecase-0` doctor demo knowledge bundle into the main multi-agent runtime.

Imported destination:

```text
backend/knowledge/latest/
```

Required files:

```text
corpus.jsonl
embeddings.jsonl
metadata_manifest.json
prompt_policy.md
faq_exact_answers.py
content_version.json
README.md
```

Runtime behavior:

```text
if backend/knowledge/latest/corpus.jsonl and embeddings.jsonl exist:
    use imported_bundle
else:
    fall back to checked-in rag_pipeline artifacts
```

Cloud Shell verification:

```text
knowledge_source=imported_bundle
corpus_exists=True
embeddings_exists=True
```

Test result:

```text
33 passed after imported-bundle runtime path fix
35 passed after answer formatter integration
```

## Step 19 - Patient-Friendly Answer Formatter

Date: 2026-06-28

Copied and adapted the deterministic answer presentation layer from `rag-usecase-0` into the main backend.

New file:

```text
backend/retrieval/answering.py
```

Updated:

```text
backend/tools/faq_tools.py
tests/test_faq_tools_vertex_mode.py
```

Answer behavior:

```text
maximum 4 bullets
warm clinic-assistant tone
icons/smileys supported
Dr. Madhu Patil’s Clinic phrasing for services
Dr. Madhu Patil’s team phrasing for appointment/help coordination
raw RAG headings removed
source and grounding score retained in data.retrieval
```

Cloud Shell verification:

```text
pytest: 35 passed
smoke_agent_vertex_retrieval.py passed
smoke_api_local.py passed
manual /chat returned polished answer
```

Manual `/chat` example:

```text
🩺 **Yes.** Dr. Madhu Patil’s Clinic offers Endometriosis & PCOS.
🔎 This is relevant to treatments such as pcos care, endometriosis care, and hormonal evaluation and conditions such as pcos, endometriosis, irregular periods, and hormonal issues.
📅 For personal guidance, __booking a consultation__ is the best next step.
```

Status:

```text
Layer 4 RAG retrieval and answer presentation are verified for the main backend.
```
