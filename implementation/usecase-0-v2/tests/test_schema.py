from backend.storage.schema import DEFAULT_SHEET_TABS


def test_sheet_tab_mapping_uses_audit_logs():
    assert DEFAULT_SHEET_TABS["audit_logs"] == "AuditLogs"


def test_usecase_one_ready_tabs_are_mapped():
    assert DEFAULT_SHEET_TABS["appointments"] == "Appointments"
    assert DEFAULT_SHEET_TABS["emergency_tickets"] == "EmergencyTickets"
    assert DEFAULT_SHEET_TABS["leads"] == "Leads"

