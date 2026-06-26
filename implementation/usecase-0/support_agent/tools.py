from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from support_agent.storage import JsonStore


VALID_PRIORITIES = {"low", "medium", "high"}
VALID_STATUSES = {"open", "in_progress", "resolved", "closed", "escalated"}


class SupportTools:
    def __init__(self, store: JsonStore | None = None):
        self.store = store or JsonStore()

    def get_faq_answer(self, topic: str) -> dict[str, Any]:
        faq = self.store.read("faq", [])
        normalized = topic.lower()
        for item in faq:
            keywords = [item.get("keyword", ""), *item.get("aliases", [])]
            if any(keyword.lower() in normalized for keyword in keywords):
                return {
                    "status": "success",
                    "answer": item["answer"],
                    "matched_keyword": item["keyword"],
                }
        return {
            "status": "not_found",
            "message": "I could not find this in the FAQ. I can create a ticket or hand this to a human support agent.",
        }

    def create_ticket(self, user_id: str, issue: str, priority: str = "medium") -> dict[str, Any]:
        priority = priority if priority in VALID_PRIORITIES else "medium"

        def updater(tickets: dict[str, Any]) -> dict[str, Any]:
            next_number = tickets.get("_counter", 1)
            ticket_id = f"TKT-{next_number:04d}"
            tickets["_counter"] = next_number + 1
            tickets.setdefault("items", {})[ticket_id] = {
                "id": ticket_id,
                "user_id": user_id,
                "issue": issue,
                "priority": priority,
                "status": "open",
                "resolution": None,
                "created_at": utc_now(),
                "updated_at": utc_now(),
            }
            return {
                "status": "success",
                "ticket_id": ticket_id,
                "message": f"Ticket {ticket_id} created.",
                "ticket": tickets["items"][ticket_id],
            }

        return self.store.update("tickets", {"_counter": 1, "items": {}}, updater)

    def check_ticket_status(self, ticket_id: str) -> dict[str, Any]:
        tickets = self.store.read("tickets", {"_counter": 1, "items": {}})
        ticket = tickets.get("items", {}).get(ticket_id.upper())
        if not ticket:
            return {"status": "error", "message": f"Ticket {ticket_id} not found."}
        return {"status": "success", "ticket": ticket}

    def update_ticket(self, ticket_id: str, status: str, resolution: str = "") -> dict[str, Any]:
        ticket_id = ticket_id.upper()
        status = status.lower()
        if status not in VALID_STATUSES:
            return {"status": "error", "message": f"Unsupported ticket status: {status}."}

        def updater(tickets: dict[str, Any]) -> dict[str, Any]:
            ticket = tickets.get("items", {}).get(ticket_id)
            if not ticket:
                return {"status": "error", "message": f"Ticket {ticket_id} not found."}
            ticket["status"] = status
            ticket["resolution"] = resolution or ticket.get("resolution")
            ticket["updated_at"] = utc_now()
            return {"status": "success", "message": f"Ticket {ticket_id} updated to '{status}'.", "ticket": ticket}

        return self.store.update("tickets", {"_counter": 1, "items": {}}, updater)

    def fetch_user_info(self, user_id: str) -> dict[str, Any]:
        users = self.store.read("users", {})
        user = users.get(user_id) or users.get("guest")
        if not user:
            return {"status": "error", "message": "User not found in local CRM."}
        return {"status": "success", **user}

    def escalate_ticket(self, ticket_id: str, reason: str, user_id: str = "guest") -> dict[str, Any]:
        ticket_id = ticket_id.upper()
        ticket_result = self.update_ticket(ticket_id, "escalated", reason)
        if ticket_result["status"] != "success":
            return ticket_result

        user_result = self.fetch_user_info(user_id)
        escalation_id = f"ESC-{compact_timestamp()}"

        def updater(escalations: dict[str, Any]) -> dict[str, Any]:
            record = {
                "id": escalation_id,
                "ticket_id": ticket_id,
                "user_id": user_id,
                "reason": reason,
                "status": "open",
                "created_at": utc_now(),
                "contact": user_result if user_result.get("status") == "success" else None,
            }
            escalations.setdefault("items", {})[escalation_id] = record
            return {
                "status": "success",
                "escalation_id": escalation_id,
                "message": f"Ticket {ticket_id} escalated. A human support agent will contact you soon.",
                "escalation": record,
            }

        return self.store.update("escalations", {"items": {}}, updater)


def extract_ticket_id(text: str) -> str | None:
    match = re.search(r"\bTKT-\d{4,}\b", text.upper())
    return match.group(0) if match else None


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def compact_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S%f")

