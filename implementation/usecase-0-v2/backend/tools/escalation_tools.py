from typing import Any

from backend.services.ids import new_id, utc_now
from backend.storage import StorageService
from backend.tools.ticket_tools import TicketTools
from backend.tools.user_tools import UserTools


class EscalationTools:
    def __init__(self, store: StorageService, ticket_tools: TicketTools, user_tools: UserTools):
        self.store = store
        self.ticket_tools = ticket_tools
        self.user_tools = user_tools

    def escalate_ticket(self, ticket_id: str, user_id: str, reason: str) -> dict[str, Any]:
        ticket_result = self.ticket_tools.update_ticket(ticket_id, "escalated", reason)
        if ticket_result["status"] != "success":
            return ticket_result

        user_result = self.user_tools.fetch_user_info(user_id)
        escalation_id = new_id("ESC")
        row = {
            "escalation_id": escalation_id,
            "ticket_id": ticket_id,
            "user_id": user_id,
            "reason": reason,
            "status": "open",
            "human_notified": "false",
            "created_at": utc_now(),
            "contact_name": user_result.get("user", {}).get("name", ""),
            "contact_email": user_result.get("user", {}).get("email", ""),
        }
        self.store.append_row("escalations", row)
        return {
            "status": "success",
            "escalation_id": escalation_id,
            "message": f"Ticket {ticket_id} escalated. A human support agent will contact you soon.",
            "escalation": row,
        }

