from __future__ import annotations

from backend.api.app import create_app


def main() -> None:
    try:
        from fastapi.testclient import TestClient
    except ImportError as exc:
        raise SystemExit("FastAPI test client is not installed. Run: pip install -r requirements-api.txt") from exc

    client = TestClient(create_app())
    session_id = "appointment-lifecycle-smoke"

    created = client.post(
        "/chat",
        json={
            "message": "I want to book a video consultation for PCOS tomorrow morning. My name is Anjali and phone is 9876543210.",
            "user_id": "guest",
            "session_id": session_id,
        },
    )
    created_payload = created.json()
    appointment_id = created_payload["data"]["appointment_id"]
    print("create", created.status_code, created_payload["agent"], appointment_id, created_payload["data"]["appointment"]["status"])

    status = client.post(
        "/chat",
        json={"message": f"Check appointment {appointment_id}", "user_id": "guest", "session_id": session_id},
    )
    status_payload = status.json()
    print("status", status.status_code, status_payload["agent"], status_payload["data"]["appointment"]["status"])

    updated = client.post(
        "/chat",
        json={"message": f"Update {appointment_id} to next week evening", "user_id": "guest", "session_id": session_id},
    )
    updated_payload = updated.json()
    print("update", updated.status_code, updated_payload["agent"], updated_payload["data"]["appointment"]["appointment_id"])

    cancelled = client.post(
        "/chat",
        json={"message": f"Cancel appointment {appointment_id}", "user_id": "guest", "session_id": session_id},
    )
    cancelled_payload = cancelled.json()
    print("cancel", cancelled.status_code, cancelled_payload["agent"], cancelled_payload["data"]["appointment"]["status"])


if __name__ == "__main__":
    main()
