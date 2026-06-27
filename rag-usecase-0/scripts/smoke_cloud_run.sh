#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-}"
if [[ -z "$BASE_URL" ]]; then
  echo "Usage: scripts/smoke_cloud_run.sh https://YOUR-CLOUD-RUN-URL" >&2
  exit 1
fi

python scripts/smoke_url.py "$BASE_URL"
