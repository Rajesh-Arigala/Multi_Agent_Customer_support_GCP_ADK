from __future__ import annotations

import re
from typing import Any

from support_agent.schemas import AgentResponse
from support_agent.tools import SupportTools, extract_ticket_id


URGENT_WORDS = {"urgent", "critical", "angry", "frustrated", "broken", "down", "immediately", "human", "escalate"}
CREATE_WORDS = {"create", "open", "raise", "file", "ticket", "issue", "problem", "bug", "error"}
STATUS_WORDS = {"status", "check", "lookup", "track", "progress"}
UPDATE_WORDS = {"resolved", "close", "closed", "fix", "fixed", "update"}


class SupportOrchestrator:
    """ADK-inspired deterministic router for the Render baseline demo."""

    def __init__(self, tools: SupportTools | None = None):
        self.tools = tools or SupportTools()
        self.sessions: dict[str, list[dict[str, str]]] = {}

    def handle_message(self, message: str, user_id: str = "guest", session_id: str = "guest") -> dict[str, Any]:
        normalized = message.lower()
        self._remember(session_id, "user", message)

        if self._has_any(normalized, URGENT_WORDS):
            response = self._handle_escalation(message, user_id)
        elif extract_ticket_id(message) and self._has_any(normalized, UPDATE_WORDS):
            response = self._handle_update(message)
        elif extract_ticket_id(message) or self._has_any(normalized, STATUS_WORDS):
            response = self._handle_status(message)
        elif self._has_any(normalized, CREATE_WORDS):
            response = self._handle_ticket(message, user_id)
        else:
            response = self._handle_triage(message)

        self._remember(session_id, "assistant", response["message"])
        response["session"] = {"id": session_id, "turns": len(self.sessions.get(session_id, []))}
        return response

    def _handle_triage(self, message: str) -> dict[str, Any]:
        result = self.tools.get_faq_answer(message)
        if result["status"] == "success":
            return AgentResponse(
                status="success",
                agent="triage_agent",
                message=result["answer"],
                data=result,
            ).to_dict()
        return AgentResponse(
            status="not_found",
            agent="web_search_agent",
            message=result["message"],
            data={"fallback": "web_search_placeholder", **result},
        ).to_dict()

    def _handle_ticket(self, message: str, user_id: str) -> dict[str, Any]:
        priority = classify_priority(message)
        result = self.tools.create_ticket(user_id=user_id, issue=message, priority=priority)
        ticket_id = result.get("ticket_id")
        return AgentResponse(
            status=result["status"],
            agent="ticket_agent",
            message=f"I routed this to ticket_agent and created {ticket_id}. Priority is {priority}.",
            data=result,
        ).to_dict()

    def _handle_status(self, message: str) -> dict[str, Any]:
        ticket_id = extract_ticket_id(message)
        if not ticket_id:
            return AgentResponse(
                status="error",
                agent="ticket_agent",
                message="Please include a ticket ID like TKT-0001 so I can check it.",
                data={},
            ).to_dict()
        result = self.tools.check_ticket_status(ticket_id)
        if result["status"] != "success":
            return AgentResponse("error", "ticket_agent", result["message"], result).to_dict()
        ticket = result["ticket"]
        message_text = f"{ticket['id']} is {ticket['status']} with {ticket['priority']} priority."
        if ticket.get("resolution"):
            message_text += f" Resolution note: {ticket['resolution']}"
        return AgentResponse("success", "ticket_agent", message_text, result).to_dict()

    def _handle_update(self, message: str) -> dict[str, Any]:
        ticket_id = extract_ticket_id(message)
        status = "resolved" if re.search(r"\b(resolved|fixed|fix)\b", message.lower()) else "closed"
        result = self.tools.update_ticket(ticket_id, status, message)
        return AgentResponse(result["status"], "ticket_agent", result["message"], result).to_dict()

    def _handle_escalation(self, message: str, user_id: str) -> dict[str, Any]:
        ticket_id = extract_ticket_id(message)
        ticket_result = None
        if not ticket_id:
            priority = classify_priority(message)
            ticket_result = self.tools.create_ticket(user_id=user_id, issue=message, priority=priority)
            ticket_id = ticket_result.get("ticket_id")
        result = self.tools.escalate_ticket(ticket_id, reason=message, user_id=user_id)
        data = {"ticket": ticket_result, **result}
        return AgentResponse(
            status=result["status"],
            agent="escalation_agent",
            message=result["message"],
            data=data,
        ).to_dict()

    def _remember(self, session_id: str, role: str, content: str) -> None:
        history = self.sessions.setdefault(session_id, [])
        history.append({"role": role, "content": content})
        del history[:-20]

    @staticmethod
    def _has_any(text: str, words: set[str]) -> bool:
        return any(word in text for word in words)


def classify_priority(message: str) -> str:
    text = message.lower()
    if any(word in text for word in {"urgent", "critical", "down", "broken", "immediately", "escalate"}):
        return "high"
    if any(word in text for word in {"error", "bug", "issue", "problem", "cannot", "can't", "failed"}):
        return "medium"
    return "low"

