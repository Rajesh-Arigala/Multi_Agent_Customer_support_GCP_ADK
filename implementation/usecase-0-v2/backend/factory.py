from backend.agents import SupportOrchestrator
from backend.services.audit import AuditLogService
from backend.services.memory import MemoryService
from backend.storage import StorageService
from backend.tools.appointment_tools import AppointmentTools
from backend.tools.escalation_tools import EscalationTools
from backend.tools.faq_tools import FaqTools
from backend.tools.ticket_tools import TicketTools
from backend.tools.user_tools import UserTools
from backend.tools.web_search_tools import WebSearchTools


def build_support_orchestrator(store: StorageService) -> SupportOrchestrator:
    audit_log = AuditLogService(store)
    ticket_tools = TicketTools(store)
    user_tools = UserTools(store)
    return SupportOrchestrator(
        faq_tools=FaqTools(store),
        appointment_tools=AppointmentTools(store),
        ticket_tools=ticket_tools,
        escalation_tools=EscalationTools(store, ticket_tools, user_tools),
        web_search_tools=WebSearchTools(),
        memory_service=MemoryService(store),
        audit_log=audit_log,
    )
