# Cloud Run Deployment - RAG Usecase 0

This is the recommended deployment path for the doctor review demo because service account key creation is disabled by organization policy.

Cloud Run uses the attached service account directly, so no JSON key is required.

## Service Account

Use:

```text
multi-agent-backend-sa@multi-agent-adk-1.iam.gserviceaccount.com
```

It needs Vertex AI access:

```text
roles/aiplatform.user
```

## Deploy From Cloud Shell

```bash
cd ~/Multi_Agent_Customer_support_GCP_ADK/rag-usecase-0
chmod +x scripts/deploy_cloud_run.sh scripts/smoke_cloud_run.sh
./scripts/deploy_cloud_run.sh
```

The script prints:

```text
Cloud Run URL:
https://...

Review URL:
https://.../review
```

## Smoke Test

```bash
./scripts/smoke_cloud_run.sh https://YOUR-CLOUD-RUN-URL
```

Expected:

```text
health 200
review 200
chat 200 WEB-DRMADHU-006 hybrid_vertex
```

## Share With Doctor

Send only:

```text
https://YOUR-CLOUD-RUN-URL/review
```

## Notes

The service is currently deployed with `--allow-unauthenticated` so the doctor can open the link. This is acceptable for short review windows, but for a longer-lived demo add an access control layer.

The first request may be slower because the service builds missing Vertex document vectors into `/tmp` on cold start.
