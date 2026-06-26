# Usecase 0 - Generic Customer Support Agent

Render-deployable baseline customer support demo based on the ADK notebook logic in `adk_agentic_ai.ipynb`.

The notebook used ADK agents and in-memory data. This app keeps the same concepts while using a deterministic Flask implementation that can run without Google Cloud credentials:

- `support_orchestrator` routes every chat turn.
- `triage_agent` answers FAQ questions from JSON.
- `ticket_agent` creates, checks, and updates tickets.
- `escalation_agent` creates escalation records for urgent requests.
- `web_search_agent` is represented as a safe placeholder when FAQ has no match.

## Run Locally

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
flask --app app run --debug
```

Open `http://127.0.0.1:5000`.

## API

```bash
curl http://127.0.0.1:5000/health
```

```bash
curl -X POST http://127.0.0.1:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Create a ticket for my billing issue","user_id":"student_001"}'
```

Additional endpoints:

- `POST /api/tickets`
- `GET /api/tickets/<ticket_id>`

## Demo Prompts

- `How do I reset my password?`
- `Create a ticket for my billing issue.`
- `Check TKT-0001`
- `This is urgent. I am very frustrated.`
- `Something not in FAQ.`

## Deploy To Render

1. Push this folder to a Git repository.
2. In Render, create a new Blueprint from the repository.
3. Render will read `render.yaml`, install `requirements.txt`, and run `gunicorn app:app --bind 0.0.0.0:$PORT`.

The default JSON files are local app storage. For longer-lived production deployments, attach a Render disk or replace `JsonStore` with a managed database.

## Tests

```bash
pytest
```

The tests cover JSON persistence, support tools, orchestration, and the Flask chat API.
