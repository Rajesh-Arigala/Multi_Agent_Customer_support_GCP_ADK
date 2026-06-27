# RAG Usecase 0 - Doctor Review Demo

Standalone, mobile-compatible RAG demo for reviewing answer quality with a doctor. This folder is intentionally separate from `implementation/usecase-0-v2`.

## Doctor Experience

Share:

```text
https://YOUR-CLOUD-RUN-URL/review
```

The doctor can ask patient-style questions and see:

```text
answer
matched document
retrieval mode
filter mode
score
source URL
```

## Full RAG Path

```text
Cloud Run FastAPI backend
-> attached GCP service account
-> approved enriched clinic corpus
-> Vertex text-embedding-005 document vectors, built if missing
-> Vertex text-embedding-005 query embedding
-> metadata filters
-> hybrid retrieval
-> mobile review page
```

## Local Tests

These avoid Vertex calls:

```bash
cd rag-usecase-0/backend
RAG_USE_VERTEX=false PYTHONPATH=. pytest -p no:cacheprovider
```

## Cloud Run Deployment

Use Cloud Run because service account JSON key creation is blocked by organization policy.

```bash
cd rag-usecase-0
chmod +x scripts/deploy_cloud_run.sh scripts/smoke_cloud_run.sh
./scripts/deploy_cloud_run.sh
```

Smoke:

```bash
./scripts/smoke_cloud_run.sh https://YOUR-CLOUD-RUN-URL
```

Expected:

```text
health 200
review 200
chat 200 WEB-DRMADHU-006 hybrid_vertex
```

See `CLOUD_RUN_DEPLOYMENT.md` for details.

## Security Note

The deploy script uses `--allow-unauthenticated` so the doctor can open the review link. Use this for a controlled review window. Add auth before making it a long-lived public service.
