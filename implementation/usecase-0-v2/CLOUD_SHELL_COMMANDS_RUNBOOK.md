# Cloud Shell Commands Runbook - Usecase 0 v2

Last updated: 2026-06-28

This runbook is for someone operating the deployed doctor assistant demo from Google Cloud Shell. It is intentionally step-by-step.

Important: paste only command blocks into the terminal. Do not paste expected output, notes, prompts, or chat text.

## 1. Start In The Right Folder

```bash
cd ~/Multi_Agent_Customer_support_GCP_ADK/implementation/usecase-0-v2
source ../.venv/bin/activate
git pull
```

Expected:

```text
Already up to date.
```

or a normal fast-forward pull.

## 2. Select GCP Project And CLI Account

```bash
gcloud auth list
```

If no account is active, run:

```bash
gcloud auth login
gcloud config set account rajesh.arigala@redlegos.com
```

Then set the project:

```bash
gcloud config set project multi-agent-adk-1
```

## 3. Configure ADC For Vertex

Fresh Cloud Shell sessions may not have the right Application Default Credentials for Vertex query embeddings.

```bash
gcloud auth application-default login \
  --scopes=https://www.googleapis.com/auth/cloud-platform

gcloud auth application-default set-quota-project multi-agent-adk-1

export GOOGLE_CLOUD_PROJECT=multi-agent-adk-1
export GOOGLE_GENAI_USE_VERTEXAI=true
export GOOGLE_CLOUD_LOCATION=us-central1
ADC_DIR="$(gcloud info --format='value(config.paths.global_config_dir)')"
export GOOGLE_APPLICATION_CREDENTIALS="$ADC_DIR/application_default_credentials.json"

ls -la "$GOOGLE_APPLICATION_CREDENTIALS"
```

Expected:

```text
... application_default_credentials.json
```

If Vertex tests fail with `service account info is missing 'email' field`, repeat this section.

Do not add the Google Sheets scope to this user ADC command. Google may block the default ADC OAuth client for non-Cloud scopes such as Sheets.

## 3A. Configure ADC For Google Sheets With Service Account Impersonation

Use this section before running Google Sheets smoke checks or before using `STORAGE_BACKEND=google_sheets`.

The backend service account is:

```text
multi-agent-backend-sa@multi-agent-adk-1.iam.gserviceaccount.com
```

First make sure your user can impersonate the backend service account. If needed, an admin can grant:

```bash
gcloud iam service-accounts add-iam-policy-binding \
  multi-agent-backend-sa@multi-agent-adk-1.iam.gserviceaccount.com \
  --project multi-agent-adk-1 \
  --member=user:rajesh.arigala@redlegos.com \
  --role=roles/iam.serviceAccountTokenCreator
```

Then create ADC using service account impersonation:

```bash
unset GOOGLE_APPLICATION_CREDENTIALS

gcloud auth application-default login \
  --impersonate-service-account=multi-agent-backend-sa@multi-agent-adk-1.iam.gserviceaccount.com \
  --scopes=https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/spreadsheets

gcloud auth application-default set-quota-project multi-agent-adk-1

export GOOGLE_CLOUD_PROJECT=multi-agent-adk-1
export GOOGLE_GENAI_USE_VERTEXAI=true
export GOOGLE_CLOUD_LOCATION=us-central1
ADC_DIR="$(gcloud info --format='value(config.paths.global_config_dir)')"
export GOOGLE_APPLICATION_CREDENTIALS="$ADC_DIR/application_default_credentials.json"

ls -la "$GOOGLE_APPLICATION_CREDENTIALS"
```

If the browser says `This app is blocked`, stop using the user ADC flow with the Sheets scope and use this impersonation flow instead.

If impersonation is denied, grant `roles/iam.serviceAccountTokenCreator` as shown above.

The impersonated backend service account also needs permission to use the quota project for Google APIs:

```bash
gcloud projects add-iam-policy-binding multi-agent-adk-1 \
  --member=serviceAccount:multi-agent-backend-sa@multi-agent-adk-1.iam.gserviceaccount.com \
  --role=roles/serviceusage.serviceUsageConsumer
```

## 4. Verify Knowledge Bundle Exists

```bash
test -f backend/knowledge/latest/corpus.jsonl
test -f backend/knowledge/latest/embeddings.jsonl
test -f backend/knowledge/latest/metadata_manifest.json
```

No output means success.

## 5. Run Local Test Suite

```bash
PYTHONPATH=. python -m pytest -p no:cacheprovider
```

Expected current result after appointment lifecycle:

```text
38 passed
```

Older commits before appointment lifecycle may show:

```text
36 passed
```

## 6. Verify Vertex RAG Path

```bash
PYTHONPATH=. python scripts/smoke_agent_vertex_retrieval.py
```

Expected service hits:

```text
PCOS/endometriosis       WEB-DRMADHU-006  hybrid_vertex
IVF/ICSI                 WEB-DRMADHU-003  hybrid_vertex
fertility preservation   WEB-DRMADHU-005  hybrid_vertex
```

## 7. Verify FastAPI Locally Without Starting Server

```bash
PYTHONPATH=. python scripts/smoke_api_local.py
```

Expected:

```text
health 200 ok
metadata 200 ok 8
chat 200 triage_agent WEB-DRMADHU-006 hybrid_vertex
retrieval_smoke 200 3
```

## 8. Verify Appointment Lifecycle Locally

Run the script with Python, not as an executable:

```bash
PYTHONPATH=. python scripts/smoke_appointment_lifecycle.py
```

Expected:

```text
create 200 appointment_agent APT-... requested
status 200 appointment_agent requested
update 200 appointment_agent APT-...
cancel 200 appointment_agent cancelled
```

If you accidentally run `scripts/smoke_appointment_lifecycle.py` directly and see `Permission denied`, use the Python command above.

## 9. Check Live Google Sheets Schema

The Sheet ID is:

```text
1zwyHaspgLVjE5Xax0c9riylI6CBirf12v98k6mgp2c8
```

Run:

```bash
STORAGE_BACKEND=google_sheets \
PYTHONPATH=. python scripts/smoke_sheets_schema.py
```

Expected: each table prints `missing_headers none` or shows exactly what is missing.

Tables checked:

```text
appointments
emergency_tickets
leads
users
audit_logs
```

If you see `ACCESS_TOKEN_SCOPE_INSUFFICIENT`, rerun Section 3A.

If you see `Unable to parse range: Appointments!A:ZZ`, the Sheet tab is missing or named differently. List tabs:

```bash
STORAGE_BACKEND=google_sheets PYTHONPATH=. python - <<'PY'
from backend.api.runtime import build_runtime_store
store = build_runtime_store()
meta = store.service.spreadsheets().get(spreadsheetId=store.spreadsheet_id).execute()
for sheet in meta.get("sheets", []):
    print(sheet["properties"]["title"])
PY
```

Create missing operational tabs:

```bash
STORAGE_BACKEND=google_sheets PYTHONPATH=. python - <<'PY'
from backend.api.runtime import build_runtime_store

store = build_runtime_store()
required = [
    "FAQ",
    "Users",
    "Leads",
    "Tickets",
    "Appointments",
    "Escalations",
    "EmergencyTickets",
    "Sessions",
    "Memories",
    "AuditLogs",
]
meta = store.service.spreadsheets().get(spreadsheetId=store.spreadsheet_id).execute()
existing = {sheet["properties"]["title"] for sheet in meta.get("sheets", [])}
requests = [{"addSheet": {"properties": {"title": title}}} for title in required if title not in existing]
if requests:
    store.service.spreadsheets().batchUpdate(
        spreadsheetId=store.spreadsheet_id,
        body={"requests": requests},
    ).execute()
print("created", [request["addSheet"]["properties"]["title"] for request in requests])
PY
```

Known typo found during setup:

```text
Appoitments
```

This is not the tab used by the app. The app expects:

```text
Appointments
```

After missing tabs exist, seed headers:

```bash
STORAGE_BACKEND=google_sheets \
PYTHONPATH=. python scripts/seed_sheets_headers.py
```

Expected:

```text
appointments headers updated
emergency_tickets headers updated
leads headers updated
users headers updated
audit_logs headers ok
```

Then rerun:

```bash
STORAGE_BACKEND=google_sheets \
PYTHONPATH=. python scripts/smoke_sheets_schema.py
```

Expected:

```text
missing_headers none
```

## 10. Optional Local Uvicorn Server

Start server:

```bash
PYTHONPATH=. uvicorn backend.api.app:app --host 0.0.0.0 --port 8080
```

In another Cloud Shell tab:

```bash
curl http://localhost:8080/health
curl http://localhost:8080/metadata/status
curl http://localhost:8080/retrieval/smoke
curl -X POST http://localhost:8080/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Can Dr Madhu help with PCOS and endometriosis?","user_id":"guest","session_id":"manual-test"}'
```

Stop server with:

```text
Ctrl+C
```

Important route:

```text
/metadata/status is valid.
/metadata is not registered.
```

## 11. Deploy To Cloud Run

Deploy:

```bash
bash scripts/deploy_cloud_run.sh
```

The script deploys:

```text
service: doctor-assistant-usecase-0-v2
project: multi-agent-adk-1
region: us-central1
service account: multi-agent-backend-sa@multi-agent-adk-1.iam.gserviceaccount.com
```

If deploy says no active account:

```bash
gcloud auth login
gcloud config set account rajesh.arigala@redlegos.com
gcloud config set project multi-agent-adk-1
bash scripts/deploy_cloud_run.sh
```

## 12. Make Cloud Run Public For Demo

The org may block `allUsers` IAM binding. Use the Cloud Run invoker-check setting:

```bash
gcloud run services update doctor-assistant-usecase-0-v2 \
  --project multi-agent-adk-1 \
  --region us-central1 \
  --no-invoker-iam-check
```

If this works, no `allUsers` binding is needed.

If someone tries this and gets an org-policy error:

```bash
gcloud org-policies describe constraints/run.managed.requireInvokerIam \
  --project multi-agent-adk-1 \
  --effective
```

## 13. Get Deployed URL

```bash
SERVICE_URL="$(gcloud run services describe doctor-assistant-usecase-0-v2 \
  --project multi-agent-adk-1 \
  --region us-central1 \
  --format='value(status.url)')"

echo "$SERVICE_URL"
```

Known live URL from the first successful deploy:

```text
https://doctor-assistant-usecase-0-v2-jatcfdo4uq-uc.a.run.app
```

## 14. Smoke Deployed Service

```bash
bash scripts/smoke_deployed_cloud_run.sh "$SERVICE_URL"
```

Expected:

```text
health ok
metadata ok 8
retrieval smoke ok
chat ok WEB-DRMADHU-006 1.0
```

If smoke gets `403 Forbidden`, rerun Section 12.

## 15. Manual Deployed Endpoint Checks

```bash
curl "$SERVICE_URL/health"
curl "$SERVICE_URL/metadata/status"
curl "$SERVICE_URL/retrieval/smoke"
curl -X POST "$SERVICE_URL/chat" \
  -H "Content-Type: application/json" \
  -d '{"message":"Can Dr Madhu help with PCOS and endometriosis?","user_id":"guest","session_id":"deployed-smoke"}'
```

Open frontend:

```text
https://doctor-assistant-usecase-0-v2-jatcfdo4uq-uc.a.run.app/
```

## 16. Authenticated Smoke If Public Access Is Not Allowed

Use this only if the service must stay private:

```bash
TOKEN="$(gcloud auth print-identity-token)"

curl -H "Authorization: Bearer $TOKEN" "$SERVICE_URL/health"
```

For all endpoints:

```bash
TOKEN="$(gcloud auth print-identity-token)"

curl -H "Authorization: Bearer $TOKEN" "$SERVICE_URL/metadata/status"
curl -H "Authorization: Bearer $TOKEN" "$SERVICE_URL/retrieval/smoke"
curl -X POST "$SERVICE_URL/chat" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"message":"Can Dr Madhu help with PCOS and endometriosis?","user_id":"guest","session_id":"deployed-smoke"}'
```

## 17. Common Errors

### No Such File

Symptom:

```text
bash: scripts/deploy_cloud_run.sh: No such file or directory
```

Fix:

```bash
cd ~/Multi_Agent_Customer_support_GCP_ADK/implementation/usecase-0-v2
git pull
ls -la scripts/deploy_cloud_run.sh
```

### Permission Denied For Script

Symptom:

```text
scripts/smoke_appointment_lifecycle.py: Permission denied
```

Fix:

```bash
PYTHONPATH=. python scripts/smoke_appointment_lifecycle.py
```

### Vertex ADC Error

Symptom:

```text
service account info is missing 'email' field
```

Fix: rerun Section 3.

### Google Sheets Scope Error

Symptom:

```text
ACCESS_TOKEN_SCOPE_INSUFFICIENT
```

Fix: rerun Section 3A with service account impersonation.

### This App Is Blocked During ADC Login

Symptom:

```text
This app is blocked
```

Cause:

```text
The default ADC OAuth client can be blocked when requesting non-Cloud scopes such as Google Sheets.
```

Fix: use Section 3A service account impersonation. Do not continue with user ADC plus the Sheets scope.

Required scopes in Section 3A:

```text
cloud-platform
spreadsheets
```

### Cloud Run 403

Symptom:

```text
GET /health failed with 403
```

Fix: rerun Section 12.

### Org Policy Blocks allUsers

Symptom:

```text
One or more users named in the policy do not belong to a permitted customer
```

Fix: do not use `allUsers` IAM binding. Use:

```bash
gcloud run services update doctor-assistant-usecase-0-v2 \
  --project multi-agent-adk-1 \
  --region us-central1 \
  --no-invoker-iam-check
```

## 18. Current Architecture Verification Meaning

When all smoke checks pass, this is verified:

```text
Frontend
-> Cloud Run FastAPI
-> SupportOrchestrator
-> triage_agent
-> imported RAG bundle
-> Vertex hybrid retrieval
-> patient-friendly formatter
```

Appointment lifecycle is verified locally when:

```text
create/status/update/cancel -> appointment_agent -> Appointments
```

Emergency ticket flow is the next separate slice.
