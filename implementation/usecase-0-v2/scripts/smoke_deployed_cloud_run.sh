#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${1:-}"
if [[ -z "$BASE_URL" ]]; then
  echo "Usage: $0 https://your-cloud-run-url" >&2
  exit 1
fi

python - "$BASE_URL" <<'PY'
import json
import sys
import urllib.error
import urllib.request

base_url = sys.argv[1].rstrip("/")


def request(method, path, payload=None):
    data = None
    headers = {}
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
        headers["Content-Type"] = "application/json"
    req = urllib.request.Request(base_url + path, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        raise AssertionError(f"{method} {path} failed with {exc.code}: {body}") from exc


health_status, health = request("GET", "/health")
assert health_status == 200, health_status
assert health["status"] == "ok", health
print("health ok")

metadata_status, metadata = request("GET", "/metadata/status")
assert metadata_status == 200, metadata_status
assert metadata["status"] == "ok", metadata
assert metadata["knowledge_source"] == "imported_bundle", metadata
assert metadata["corpus_exists"] is True, metadata
assert metadata["embeddings_exists"] is True, metadata
print("metadata ok", metadata.get("document_count"))

retrieval_status, retrieval_smoke = request("GET", "/retrieval/smoke")
assert retrieval_status == 200, retrieval_status
assert retrieval_smoke["status"] == "ok", retrieval_smoke
assert len(retrieval_smoke["results"]) == 3, retrieval_smoke
print("retrieval smoke ok")

chat_status, chat = request(
    "POST",
    "/chat",
    {
        "message": "Can Dr Madhu help with PCOS and endometriosis?",
        "user_id": "guest",
        "session_id": "deployed-smoke",
    },
)
assert chat_status == 200, chat_status
answer = chat.get("message", "")
retrieval = chat.get("data", {}).get("retrieval", {})
assert "Dr. Madhu Patil" in answer, answer
assert "Dr. Madhu Patil's Clinic" in answer or "Dr. Madhu Patil\u2019s Clinic" in answer, answer
assert len([line for line in answer.splitlines() if line.strip()]) <= 4, answer
assert "Question:" not in answer and "Answer:" not in answer and "Context:" not in answer, answer
assert retrieval.get("score") is not None, retrieval
assert retrieval.get("doc_id"), retrieval
print("chat ok", retrieval.get("doc_id"), retrieval.get("score"))
PY
