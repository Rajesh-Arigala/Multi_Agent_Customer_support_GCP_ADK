from flask import Flask, jsonify, render_template, request

from config import PORT

from support_agent.orchestrator import SupportOrchestrator


app = Flask(__name__)
orchestrator = SupportOrchestrator()


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/health")
def health():
    return jsonify({"status": "healthy", "service": "usecase-0-customer-support"})


@app.post("/api/chat")
def chat():
    payload = request.get_json(silent=True) or {}
    message = (payload.get("message") or "").strip()
    user_id = (payload.get("user_id") or "guest").strip() or "guest"
    session_id = (payload.get("session_id") or user_id).strip() or user_id

    if not message:
        return jsonify({"status": "error", "message": "Message is required."}), 400

    response = orchestrator.handle_message(
        message=message,
        user_id=user_id,
        session_id=session_id,
    )
    return jsonify(response)


@app.post("/api/tickets")
def create_ticket():
    payload = request.get_json(silent=True) or {}
    issue = (payload.get("issue") or "").strip()
    user_id = (payload.get("user_id") or "guest").strip() or "guest"
    priority = (payload.get("priority") or "medium").strip().lower()

    if not issue:
        return jsonify({"status": "error", "message": "Issue is required."}), 400

    result = orchestrator.tools.create_ticket(user_id=user_id, issue=issue, priority=priority)
    status = 201 if result["status"] == "success" else 400
    return jsonify(result), status


@app.get("/api/tickets/<ticket_id>")
def get_ticket(ticket_id):
    result = orchestrator.tools.check_ticket_status(ticket_id)
    status = 200 if result["status"] == "success" else 404
    return jsonify(result), status


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, debug=True)

