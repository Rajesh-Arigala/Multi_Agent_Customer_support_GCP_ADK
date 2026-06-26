import re
from typing import Any

from backend.services.ids import new_id, utc_now
from backend.storage import StorageService


VALID_STATUSES = {"open", "in_progress", "resolved", "closed", "escalated"}


class TicketTools:
    def __init__(self, store: StorageService):
        self.store = store

    def create_ticket(self, user_id: str, issue: str, priority: str = "medium") -> dict[str, Any]:
        ticket_id = new_id("TKT")
        row = {
            "ticket_id": ticket_id,
            "user_id": user_id,
            "issue": issue,
            "priority": priority,
            "status": "open",
            "resolution": "",
            "created_at": utc_now(),
            "updated_at": utc_now(),
        }
        self.store.append_row("tickets", row)
        return {"status": "success", "ticket_id": ticket_id, "message": f"Ticket {ticket_id} created.", "ticket": row}

    def check_ticket_status(self, ticket_id: str) -> dict[str, Any]:
        ticket = self.store.find_by_id("tickets", "ticket_id", ticket_id)
        if not ticket:
            return {"status": "error", "message": f"Ticket {ticket_id} not found."}
        return {"status": "success", "ticket": ticket}

    def update_ticket(self, ticket_id: str | None, status: str, resolution: str = "") -> dict[str, Any]:
        if not ticket_id:
            return {"status": "error", "message": "Ticket ID is required."}
        if status not in VALID_STATUSES:
            return {"status": "error", "message": f"Unsupported ticket status: {status}."}
        updated = self.store.update_by_id(
            "tickets",
            "ticket_id",
            ticket_id,
            {"status": status, "resolution": resolution, "updated_at": utc_now()},
        )
        if not updated:
            return {"status": "error", "message": f"Ticket {ticket_id} not found."}
        return {"status": "success", "message": f"Ticket {ticket_id} updated to {status}.", "ticket": updated}

    @staticmethod
    def extract_ticket_id(text: str) -> str | None:
        match = re.search(r"\bTKT-[A-Z0-9]{8}\b", text.upper())
        return match.group(0) if match else None

