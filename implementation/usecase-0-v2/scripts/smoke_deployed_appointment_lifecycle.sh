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
session_id = "deployed-appointment-lifecycle-smoke"


def request(payload):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        base_url + "/chat",
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as response:
            return response.status, json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8")
        raise AssertionError(f"POST /chat failed with {exc.code}: {body}") from exc


create_status, created = request(
    {
        "message": "I want to book a video consultation for PCOS tomorrow morning. My name is Anjali and phone is 9876543210.",
        "user_id": "guest",
        "session_id": session_id,
    }
)
assert create_status == 200, create_status
assert created["agent"] == "appointment_agent", created
appointment = created["data"]["appointment"]
appointment_id = created["data"]["appointment_id"]
assert appointment_id.startswith("APT-"), appointment_id
assert appointment["status"] == "requested", appointment
assert appointment["consultation_type"] == "video_consultation", appointment
assert appointment["service_interest"] == "PCOS-related consultation", appointment
print("appointment create ok", appointment_id)

status_code, status_payload = request(
    {
        "message": f"Check appointment {appointment_id}",
        "user_id": "guest",
        "session_id": session_id,
    }
)
assert status_code == 200, status_code
assert status_payload["agent"] == "appointment_agent", status_payload
checked = status_payload["data"]["appointment"]
assert checked["appointment_id"] == appointment_id, checked
assert checked["status"] == "requested", checked
print("appointment status ok", appointment_id)
PY
