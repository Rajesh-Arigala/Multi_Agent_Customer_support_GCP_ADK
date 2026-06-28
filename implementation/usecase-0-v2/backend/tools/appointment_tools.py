import re
from typing import Any

from backend.services.ids import new_id, utc_now
from backend.storage import StorageService


APPOINTMENT_STATUSES = {
    "requested",
    "desk_review",
    "confirmed",
    "rescheduled",
    "cancelled",
    "completed",
    "no_show",
}


class AppointmentTools:
    def __init__(self, store: StorageService):
        self.store = store

    def create_appointment(self, user_id: str, message: str, details: dict[str, str] | None = None) -> dict[str, Any]:
        details = details or extract_appointment_details(message)
        appointment_id = new_id("APT")
        now = utc_now()
        row = {
            "appointment_id": appointment_id,
            "user_id": user_id,
            "name": details.get("name", ""),
            "phone": details.get("phone", ""),
            "preferred_language": details.get("preferred_language", ""),
            "service_interest": details.get("service_interest", ""),
            "consultation_type": details.get("consultation_type", "in_person"),
            "preferred_location": details.get("preferred_location", ""),
            "preferred_date": details.get("preferred_date", ""),
            "preferred_time_window": details.get("preferred_time_window", ""),
            "reason_for_visit": details.get("reason_for_visit", message),
            "status": "requested",
            "desk_notified": "placeholder",
            "user_notified": "placeholder",
            "created_at": now,
            "updated_at": now,
        }
        self.store.append_row("appointments", row)
        self._upsert_user(user_id, row)
        self._create_lead(user_id, row)
        return {
            "status": "success",
            "appointment_id": appointment_id,
            "appointment": row,
            "missing_fields": missing_appointment_fields(row),
            "message": f"Appointment request {appointment_id} created.",
        }

    def check_appointment_status(self, appointment_id: str) -> dict[str, Any]:
        appointment = self.store.find_by_id("appointments", "appointment_id", appointment_id)
        if not appointment:
            return {"status": "error", "message": f"Appointment {appointment_id} not found."}
        return {"status": "success", "appointment": appointment}

    def update_appointment(self, appointment_id: str | None, updates: dict[str, str]) -> dict[str, Any]:
        if not appointment_id:
            return {"status": "error", "message": "Appointment ID is required."}
        if "status" in updates and updates["status"] not in APPOINTMENT_STATUSES:
            return {"status": "error", "message": f"Unsupported appointment status: {updates['status']}."}
        payload = {key: value for key, value in updates.items() if value}
        payload["updated_at"] = utc_now()
        updated = self.store.update_by_id("appointments", "appointment_id", appointment_id, payload)
        if not updated:
            return {"status": "error", "message": f"Appointment {appointment_id} not found."}
        return {"status": "success", "appointment": updated, "message": f"Appointment {appointment_id} updated."}

    def cancel_appointment(self, appointment_id: str | None, reason: str = "") -> dict[str, Any]:
        return self.update_appointment(
            appointment_id,
            {"status": "cancelled", "reason_for_visit": reason},
        )

    def _upsert_user(self, user_id: str, appointment: dict[str, str]) -> None:
        if not appointment.get("phone") and not appointment.get("name"):
            return
        existing = self.store.find_by_id("users", "user_id", user_id)
        updates = {
            "name": appointment.get("name", ""),
            "phone": appointment.get("phone", ""),
            "preferred_language": appointment.get("preferred_language", ""),
            "last_seen_at": utc_now(),
        }
        if existing:
            self.store.update_by_id("users", "user_id", user_id, updates)
        else:
            self.store.append_row(
                "users",
                {
                    "user_id": user_id,
                    **updates,
                    "preferred_script": "",
                    "created_at": utc_now(),
                    "notes": "Created from appointment request.",
                },
            )

    def _create_lead(self, user_id: str, appointment: dict[str, str]) -> None:
        self.store.append_row(
            "leads",
            {
                "lead_id": new_id("LED"),
                "user_id": user_id,
                "name": appointment.get("name", ""),
                "phone": appointment.get("phone", ""),
                "service_interest": appointment.get("service_interest", ""),
                "source": "appointment_agent",
                "status": "new",
                "created_at": utc_now(),
                "notes": f"Appointment request {appointment.get('appointment_id', '')}",
            },
        )

    @staticmethod
    def extract_appointment_id(text: str) -> str | None:
        match = re.search(r"\bAPT-[A-Z0-9]{8}\b", text.upper())
        return match.group(0) if match else None


def extract_appointment_details(message: str) -> dict[str, str]:
    normalized = message.lower()
    return {
        "name": extract_name(message),
        "phone": extract_phone(message),
        "preferred_language": extract_language(normalized),
        "service_interest": extract_service_interest(normalized),
        "consultation_type": extract_consultation_type(normalized),
        "preferred_location": extract_location(message),
        "preferred_date": extract_date_hint(normalized),
        "preferred_time_window": extract_time_hint(normalized),
        "reason_for_visit": message,
    }


def missing_appointment_fields(appointment: dict[str, str]) -> list[str]:
    required = [
        "name",
        "phone",
        "service_interest",
        "consultation_type",
        "preferred_date",
        "preferred_time_window",
    ]
    return [field for field in required if not appointment.get(field)]


def extract_name(message: str) -> str:
    match = re.search(r"\b(?:my name is|name is|i am|i'm)\s+([A-Za-z][A-Za-z .'-]{1,60})", message, re.IGNORECASE)
    if not match:
        return ""
    value = re.split(r"\b(?:phone|mobile|number|for|and|,|\.)\b", match.group(1), maxsplit=1, flags=re.IGNORECASE)[0]
    return value.strip()


def extract_phone(message: str) -> str:
    match = re.search(r"(?:\+91[-\s]?)?[6-9]\d{9}", message)
    return match.group(0).replace(" ", "").replace("-", "") if match else ""


def extract_language(normalized: str) -> str:
    if "telugu" in normalized:
        return "telugu"
    if "hindi" in normalized:
        return "hindi"
    if "english" in normalized:
        return "english"
    return ""


def extract_service_interest(normalized: str) -> str:
    services = [
        ("endometriosis", "Endometriosis-related consultation"),
        ("pcos", "PCOS-related consultation"),
        ("ivf", "IVF consultation"),
        ("icsi", "ICSI consultation"),
        ("iui", "IUI consultation"),
        ("fertility preservation", "Fertility preservation"),
        ("male infertility", "Male infertility discussion"),
        ("gynecology", "Gynecology consultation"),
    ]
    matches = [label for keyword, label in services if keyword in normalized]
    return "; ".join(matches)


def extract_consultation_type(normalized: str) -> str:
    if "video" in normalized:
        return "video_consultation"
    if "phone" in normalized or "call" in normalized:
        return "phone_call"
    return "in_person"


def extract_location(message: str) -> str:
    match = re.search(r"\b(?:at|in|location)\s+([A-Za-z][A-Za-z .'-]{1,40})", message, re.IGNORECASE)
    return match.group(1).strip(" .") if match else ""


def extract_date_hint(normalized: str) -> str:
    for hint in ["today", "tomorrow", "this week", "next week", "weekend"]:
        if hint in normalized:
            return hint
    match = re.search(r"\b(?:mon|tue|wed|thu|fri|sat|sun)(?:day)?\b", normalized)
    return match.group(0) if match else ""


def extract_time_hint(normalized: str) -> str:
    for hint in ["morning", "afternoon", "evening", "night"]:
        if hint in normalized:
            return hint
    match = re.search(r"\b\d{1,2}(?::\d{2})?\s?(?:am|pm)\b", normalized)
    return match.group(0) if match else ""
