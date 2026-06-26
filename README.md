# Customer Support AI Agent — Google ADK + Vertex AI Agent Engine

A production-grade multi-agent customer support system built with Google Agent Development Kit (ADK) and deployed to Vertex AI Agent Engine.

---

## Architecture

```
User
 │
 ▼
support_orchestrator  (LLM Agent)
 │   ├── PreloadMemoryTool       → loads past user facts from Memory Bank
 │   └── after_agent_callback   → saves session facts to Memory Bank
 │
 ├──► triage_agent          (LLM Agent)
 │        └── get_faq_answer       [Function Tool]
 │
 ├──► web_search_agent      (LLM Agent)
 │        └── google_search        [Built-in Tool]
 │
 ├──► ticket_agent          (LLM Agent)
 │        ├── create_ticket        [Function Tool]
 │        ├── check_ticket_status  [Function Tool]
 │        └── update_ticket        [Function Tool]
 │
 └──► escalation_agent      (LLM Agent)
          ├── fetch_user_info      [Third-Party Tool — JSONPlaceholder API]
          └── escalate_ticket      [Function Tool]
```

---

## Agent Routing Logic

```
User message
     │
     ▼
support_orchestrator decides:
     │
     ├── Common question?     → triage_agent (FAQ search)
     │                              └── not found? → web_search_agent
     │
     ├── Ticket request?      → ticket_agent (create / check / update)
     │
     └── Urgent / frustrated? → ticket_agent (create ticket first)
                                      └── escalation_agent (escalate ticket)
```

---

## Memory Architecture

```
Session 1:
  User: "Hi I'm John, billing issue"
  after_agent_callback fires
       └──► Vertex AI Memory Bank stores:
                "User's name is John"
                "User has a billing issue"

Session 2 (next day, brand new session):
  PreloadMemoryTool fires at start of turn
       └──► retrieves facts from Memory Bank
  Agent: "Welcome back John! Are you still having the billing issue?"
```

| Component | What it does |
|---|---|
| `PreloadMemoryTool` | Retrieves past facts at the start of every turn |
| `after_agent_callback` | Saves session to Memory Bank when conversation ends |
| `VertexAiMemoryBankService` | Vertex AI managed service — extracts and stores key facts automatically |

---

## Memory vs Sessions

| | Sessions | Memory Bank |
|---|---|---|
| Stores | Full conversation transcript | Key facts only |
| Scope | One session | Across all sessions forever |
| Example | Every message exchanged | "John has a billing issue" |
| Managed by | Vertex AI automatically | `after_agent_callback` |

---

## Tools Used

| Tool | Type | Purpose |
|---|---|---|
| `get_faq_answer` | Function Tool | Search FAQ knowledge base |
| `google_search` | Built-in Tool | Search the web |
| `create_ticket` | Function Tool | Create a support ticket |
| `check_ticket_status` | Function Tool | Look up a ticket |
| `update_ticket` | Function Tool | Update ticket status |
| `fetch_user_info` | Third-Party Tool | Call JSONPlaceholder CRM API |
| `escalate_ticket` | Function Tool | Escalate ticket to human agent |
| `PreloadMemoryTool` | Built-in Tool | Load past memories each turn |

> **Gemini API Rule:** `google_search` cannot be mixed with Function Tools in the same agent. That is why `web_search_agent` is a separate agent.

---

## Deployment

```
Local (Colab)                        Vertex AI Cloud
─────────────────                    ──────────────────────────────
AdkApp(agent=root_agent)  ──deploy──► Agent Engine container
                                           │
                                           ├── VertexAiSessionService  (Sessions tab)
                                           └── VertexAiMemoryBankService (Memories tab)
```

- **One deployment** in Part 9 — memory tools are baked into the agent before deploy
- `AdkApp` automatically uses `VertexAiMemoryBankService` when running on Vertex AI
- `AdkApp` uses `InMemoryMemoryService` when running locally (callback silently skips)

---

## Notebook Structure

| Part | What you build |
|---|---|
| 1 | Mock database (tickets + FAQ) |
| 2 | Function Tools |
| 3 | Third-Party Tool (CRM API) |
| 4 | LLM Agents (triage + web search) |
| 5 | Multi-Agent System + Memory config |
| 6 | Workflow Agent (SequentialAgent) |
| 7 | Custom Agent (priority classifier) |
| 8 | Local test with AdkApp |
| 9 | Deploy to Vertex AI Agent Engine |
| 10 | Create remote session |
| 11 | Query remote agent |
| 12 | Memory Bank demo (Session 1 → save → Session 2 recalls) |

---

## Prerequisites

- Google Cloud project with Vertex AI API enabled
- Google Cloud Storage bucket for staging
- Run on Google Colab
