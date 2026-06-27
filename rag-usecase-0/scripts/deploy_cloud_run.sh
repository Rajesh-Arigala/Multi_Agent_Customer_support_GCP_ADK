#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${PROJECT_ID:-multi-agent-adk-1}"
REGION="${REGION:-us-central1}"
SERVICE_NAME="${SERVICE_NAME:-rag-usecase-0}"
REPOSITORY="${REPOSITORY:-rag-usecase-0}"
SERVICE_ACCOUNT="${SERVICE_ACCOUNT:-multi-agent-backend-sa@multi-agent-adk-1.iam.gserviceaccount.com}"
IMAGE="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPOSITORY}/${SERVICE_NAME}:latest"

printf 'project=%s
region=%s
service=%s
image=%s
' "$PROJECT_ID" "$REGION" "$SERVICE_NAME" "$IMAGE"

gcloud config set project "$PROJECT_ID"
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com aiplatform.googleapis.com

gcloud artifacts repositories describe "$REPOSITORY" --location="$REGION" >/dev/null 2>&1 ||   gcloud artifacts repositories create "$REPOSITORY" --repository-format=docker --location="$REGION" --description="RAG usecase 0 demo images"

gcloud builds submit --tag "$IMAGE" .

gcloud run deploy "$SERVICE_NAME"   --image "$IMAGE"   --region "$REGION"   --platform managed   --service-account "$SERVICE_ACCOUNT"   --allow-unauthenticated   --memory 1Gi   --cpu 1   --timeout 300   --set-env-vars "RAG_USE_VERTEX=true,GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_LOCATION=${REGION},EMBEDDING_MODEL_NAME=text-embedding-005,RAG_EMBEDDINGS_PATH=/tmp/drmadhupatil_vertex_embeddings.jsonl"

URL="$(gcloud run services describe "$SERVICE_NAME" --region "$REGION" --format='value(status.url)')"
printf '
Cloud Run URL:
%s

Review URL:
%s/review
' "$URL" "$URL"
