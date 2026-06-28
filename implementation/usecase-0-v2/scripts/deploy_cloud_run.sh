#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${PROJECT_ID:-multi-agent-adk-1}"
REGION="${REGION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-doctor-assistant-usecase-0-v2}"
SERVICE_ACCOUNT="${SERVICE_ACCOUNT:-multi-agent-backend-sa@multi-agent-adk-1.iam.gserviceaccount.com}"
GOOGLE_SHEETS_ID="${GOOGLE_SHEETS_ID:-1zwyHaspgLVjE5Xax0c9riylI6CBirf12v98k6mgp2c8}"

cd "$(dirname "$0")/.."

required_bundle_files=(
  "backend/knowledge/latest/corpus.jsonl"
  "backend/knowledge/latest/embeddings.jsonl"
  "backend/knowledge/latest/metadata_manifest.json"
  "backend/knowledge/latest/prompt_policy.md"
  "backend/knowledge/latest/faq_exact_answers.py"
  "backend/knowledge/latest/content_version.json"
)

for file in "${required_bundle_files[@]}"; do
  if [[ ! -f "$file" ]]; then
    echo "Missing imported RAG bundle file: $file" >&2
    echo "Sync or import rag-usecase-0 into backend/knowledge/latest before deploying." >&2
    exit 1
  fi
done

gcloud config set project "$PROJECT_ID"

gcloud run deploy "$SERVICE_NAME" \
  --source . \
  --project "$PROJECT_ID" \
  --region "$REGION" \
  --service-account "$SERVICE_ACCOUNT" \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 300 \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=$PROJECT_ID,GOOGLE_CLOUD_LOCATION=$REGION,GOOGLE_GENAI_USE_VERTEXAI=true,STORAGE_BACKEND=csv,DATA_DIR=/tmp/usecase0-v2-data,GOOGLE_SHEETS_ID=$GOOGLE_SHEETS_ID,EMBEDDING_MODEL_NAME=text-embedding-005"

SERVICE_URL="$(gcloud run services describe "$SERVICE_NAME" --project "$PROJECT_ID" --region "$REGION" --format='value(status.url)')"
echo "Deployed URL: $SERVICE_URL"
echo "Smoke test: scripts/smoke_deployed_cloud_run.sh $SERVICE_URL"
