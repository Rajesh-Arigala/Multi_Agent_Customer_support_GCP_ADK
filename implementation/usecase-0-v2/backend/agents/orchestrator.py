from typing import Any

from backend.models import AgentResponse
from backend.services.audit import AuditLogService
from backend.services.memory import MemoryService
from backend.tools.appointment_tools import AppointmentTools, extract_appointment_details, missing_appointment_fields
from backend.tools.escalation_tools import EscalationTools
from backend.tools.faq_tools import FaqTools
from backend.tools.ticket_tools import TicketTools
from backend.tools.web_search_tools import WebSearchTools


URGENT_WORDS = {"urgent", "critical", "angry", "frustrated", "broken", "down", "immediately", "human", "escalate"}
CREATE_WORDS = {"create", "open", "raise", "file", "ticket", "issue", "problem", "bug", "error"}
STATUS_WORDS = {"status", "check", "lookup", "track", "progress"}
UPDATE_WORDS = {"resolved", "close", "closed", "fix", "fixed", "update"}
APPOINTMENT_WORDS = {
    "appointment",
    "book",
    "booking",
    "callback",
    "call back",
    "consultation",
    "consult",
    "meet doctor",
    "video consultation",
    "visit",
}
CANCEL_WORDS = {"cancel", "cancelled"}


class SupportOrchestrator:
    def __init__(
        self,
        faq_tools: FaqTools,
        appointment_tools: AppointmentTools,
        ticket_tools: TicketTools,
        escalation_tools: EscalationTools,
        web_search_tools: WebSearchTools,
        memory_service: MemoryService,
        audit_log: AuditLogService,
    ):
        self.faq_tools = faq_tools
        self.appointment_tools = appointment_tools
        self.ticket_tools = ticket_tools
        self.escalation_tools = escalation_tools
        self.web_search_tools = web_search_tools
        self.memory_service = memory_service
        self.audit_log = audit_log

    def handle_message(self, message: str, user_id: str = "guest", session_id: str = "default") -> dict[str, Any]:
        normalized = message.lower()
        memories = self.memory_service.preload_memory(user_id)
        self.memory_service.save_session_turn(session_id, user_id, "user", message)

        appointment_id = self.appointment_tools.extract_appointment_id(message)

        if _has_any(normalized, URGENT_WORDS):
            response = self._handle_escalation(message, user_id, session_id)
        elif appointment_id and _has_any(normalized, CANCEL_WORDS):
            response = self._handle_appointment_cancel(message, user_id, session_id)
        elif appointment_id and _has_any(normalized, UPDATE_WORDS):
            response = self._handle_appointment_update(message, user_id, session_id)
        elif appointment_id or (_has_any(normalized, STATUS_WORDS) and "appointment" in normalized):
            response = self._handle_appointment_status(message, user_id, session_id)
        elif _has_any(normalized, APPOINTMENT_WORDS):
            response = self._handle_appointment_create(message, user_id, session_id)
        elif self.ticket_tools.extract_ticket_id(message) and _has_any(normalized, UPDATE_WORDS):
            response = self._handle_ticket_update(message, user_id, session_id)
        elif self.ticket_tools.extract_ticket_id(message) or _has_any(normalized, STATUS_WORDS):
            response = self._handle_ticket_status(message, user_id, session_id)
        elif _has_any(normalized, CREATE_WORDS):
            response = self._handle_ticket_create(message, user_id, session_id)
        else:
            response = self._handle_triage(message, user_id, session_id)

        self.memory_service.save_session_turn(session_id, user_id, "assistant", response.message)
        saved_facts = self.memory_service.save_facts(user_id, extract_facts(message, response))
        payload = response.to_dict()
        payload["memory"] = {"loaded": memories, "saved": saved_facts}
        return payload

    def _handle_triage(self, message: str, user_id: str, session_id: str) -> AgentResponse:
        faq_result = self.faq_tools.retrieve_faq_answer(message)
        if faq_result["status"] == "success":
            self.audit_log.log_event(user_id, session_id, "faq_answered", "FAQ", faq_result.get("faq_id", ""), message)
            return AgentResponse("success", "triage_agent", faq_result["answer"], faq_result)

        web_result = self.web_search_tools.google_search(message)
        self.audit_log.log_event(user_id, session_id, "web_search_fallback", "WebSearch", "", message)
        return AgentResponse(web_result["status"], "web_search_agent", web_result["answer"], web_result)

    def _handle_appointment_create(self, message: str, user_id: str, session_id: str) -> AgentResponse:
        details = extract_appointment_details(message)
        result = self.appointment_tools.create_appointment(user_id, message, details)
        self.audit_log.log_event(
            user_id,
            session_id,
            "appointment_requested",
            "Appointments",
            result["appointment_id"],
            message,
        )
        return AgentResponse(
            result["status"],
            "appointment_agent",
            appointment_created_message(result),
            result,
        )

    def _handle_appointment_status(self, message: str, user_id: str, session_id: str) -> AgentResponse:
        appointment_id = self.appointment_tools.extract_appointment_id(message)
        if not appointment_id:
            return AgentResponse("error", "appointment_agent", "Please include an appointment ID like APT-1234ABCD.", {})
        result = self.appointment_tools.check_appointment_status(appointment_id)
        self.audit_log.log_event(user_id, session_id, "appointment_status_checked", "Appointments", appointment_id, message)
        if result["status"] != "success":
            return AgentResponse("error", "appointment_agent", result["message"], result)
        return AgentResponse("success", "appointment_agent", appointment_status_message(result["appointment"]), result)

    def _handle_appointment_update(self, message: str, user_id: str, session_id: str) -> AgentResponse:
        appointment_id = self.appointment_tools.extract_appointment_id(message)
        details = extract_appointment_details(message)
        result = self.appointment_tools.update_appointment(appointment_id, details)
        self.audit_log.log_event(user_id, session_id, "appointment_updated", "Appointments", appointment_id or "", message)
        if result["status"] != "success":
            return AgentResponse("error", "appointment_agent", result["message"], result)
        return AgentResponse("success", "appointment_agent", appointment_updated_message(result["appointment"]), result)

    def _handle_appointment_cancel(self, message: str, user_id: str, session_id: str) -> AgentResponse:
        appointment_id = self.appointment_tools.extract_appointment_id(message)
        result = self.appointment_tools.cancel_appointment(appointment_id, message)
        self.audit_log.log_event(user_id, session_id, "appointment_cancelled", "Appointments", appointment_id or "", message)
        if result["status"] != "success":
            return AgentResponse("error", "appointment_agent", result["message"], result)
        return AgentResponse("success", "appointment_agent", appointment_cancelled_message(result["appointment"]), result)

    def _handle_ticket_create(self, message: str, user_id: str, session_id: str) -> AgentResponse:
        result = self.ticket_tools.create_ticket(user_id, message, classify_priority(message))
        self.audit_log.log_event(user_id, session_id, "ticket_created", "Tickets", result["ticket_id"], message)
        return AgentResponse(
            result["status"],
            "ticket_agent",
            f"I routed this to ticket_agent and created {result['ticket_id']}. Priority is {result['ticket']['priority']}.",
            result,
        )

    def _handle_ticket_status(self, message: str, user_id: str, session_id: str) -> AgentResponse:
        ticket_id = self.ticket_tools.extract_ticket_id(message)
        if not ticket_id:
            return AgentResponse("error", "ticket_agent", "Please include a ticket ID like TKT-0001.", {})
        result = self.ticket_tools.check_ticket_status(ticket_id)
        self.audit_log.log_event(user_id, session_id, "ticket_status_checked", "Tickets", ticket_id, message)
        if result["status"] != "success":
            return AgentResponse("error", "ticket_agent", result["message"], result)
        ticket = result["ticket"]
        return AgentResponse(
            "success",
            "ticket_agent",
            f"{ticket['ticket_id']} is {ticket['status']} with {ticket['priority']} priority.",
            result,
        )

    def _handle_ticket_update(self, message: str, user_id: str, session_id: str) -> AgentResponse:
        ticket_id = self.ticket_tools.extract_ticket_id(message)
        status = "resolved" if any(word in message.lower() for word in {"resolved", "fixed", "fix"}) else "closed"
        result = self.ticket_tools.update_ticket(ticket_id, status, message)
        self.audit_log.log_event(user_id, session_id, "ticket_updated", "Tickets", ticket_id or "", message)
        return AgentResponse(result["status"], "ticket_agent", result["message"], result)

    def _handle_escalation(self, message: str, user_id: str, session_id: str) -> AgentResponse:
        ticket_id = self.ticket_tools.extract_ticket_id(message)
        ticket_result = None
        if not ticket_id:
            ticket_result = self.ticket_tools.create_ticket(user_id, message, "high")
            ticket_id = ticket_result["ticket_id"]

        result = self.escalation_tools.escalate_ticket(ticket_id, user_id, message)
        self.audit_log.log_event(user_id, session_id, "ticket_escalated", "Escalations", result.get("escalation_id", ""), message)
        result["ticket"] = ticket_result
        return AgentResponse(result["status"], "escalation_agent", result["message"], result)


def classify_priority(message: str) -> str:
    normalized = message.lower()
    if _has_any(normalized, {"urgent", "critical", "down", "broken", "immediately", "escalate"}):
        return "high"
    if _has_any(normalized, {"error", "bug", "issue", "problem", "cannot", "can't", "failed"}):
        return "medium"
    return "low"


def appointment_created_message(result: dict[str, Any]) -> str:
    appointment = result["appointment"]
    missing = result.get("missing_fields") or missing_appointment_fields(appointment)
    lines = [
        f"📅 Appointment request {appointment['appointment_id']} has been shared for registration desk review.",
        "🩺 Dr. Madhu Patil's Clinic team will confirm the time and details before the appointment is final.",
    ]
    if appointment.get("consultation_type") == "video_consultation":
        lines.append("🎥 For video consultation, the desk will confirm the slot and link after review.")
    if missing:
        lines.append("📝 Please share missing details when convenient: " + ", ".join(missing) + ".")
    return "\n".join(lines[:4])


def appointment_status_message(appointment: dict[str, Any]) -> str:
    return (
        f"📅 Appointment {appointment['appointment_id']} is currently {appointment.get('status', 'requested')}.\n"
        f"🩺 Service interest: {appointment.get('service_interest') or 'not specified'}.\n"
        "📞 The registration desk will confirm final timing with you."
    )


def appointment_updated_message(appointment: dict[str, Any]) -> str:
    return (
        f"📅 Appointment {appointment['appointment_id']} has been updated.\n"
        f"🩺 Current status: {appointment.get('status', 'requested')}.\n"
        "📞 The registration desk will use the latest details for follow-up."
    )


def appointment_cancelled_message(appointment: dict[str, Any]) -> str:
    return (
        f"📅 Appointment {appointment['appointment_id']} has been marked cancelled.\n"
        "🩺 Dr. Madhu Patil's Clinic team can help create a fresh request whenever needed."
    )


def extract_facts(message: str, response: AgentResponse) -> list[str]:
    facts = []
    data = response.data
    if data.get("ticket_id"):
        facts.append(f"Latest ticket is {data['ticket_id']}.")
    if data.get("appointment_id"):
        facts.append(f"Latest appointment request is {data['appointment_id']}.")
    if data.get("escalation_id"):
        facts.append(f"Latest escalation is {data['escalation_id']}.")
    if "my name is " in message.lower():
        name = message.lower().split("my name is ", 1)[1].split(".")[0].strip()
        if name:
            facts.append(f"User stated their name is {name}.")
    return facts


def _has_any(text: str, words: set[str]) -> bool:
    return any(word in text for word in words)
