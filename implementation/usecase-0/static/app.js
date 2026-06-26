const messages = document.querySelector("#messages");
const form = document.querySelector("#chat-form");
const input = document.querySelector("#message-input");
const health = document.querySelector("#health");
const sessionId = crypto.randomUUID();

function addMessage(role, text, meta = "") {
  const item = document.createElement("article");
  item.className = `message ${role}`;
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  bubble.textContent = text;
  item.appendChild(bubble);
  if (meta) {
    const note = document.createElement("p");
    note.className = "meta";
    note.textContent = meta;
    item.appendChild(note);
  }
  messages.appendChild(item);
  messages.scrollTop = messages.scrollHeight;
}

async function sendMessage(text) {
  addMessage("user", text);
  input.value = "";
  input.disabled = true;
  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({message: text, user_id: "student_001", session_id: sessionId})
    });
    const payload = await response.json();
    if (!response.ok) {
      throw new Error(payload.message || "Request failed");
    }
    addMessage("agent", payload.message, `Routed to ${payload.agent}`);
  } catch (error) {
    addMessage("agent", error.message);
  } finally {
    input.disabled = false;
    input.focus();
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const text = input.value.trim();
  if (text) {
    sendMessage(text);
  }
});

document.querySelectorAll("[data-sample]").forEach((button) => {
  button.addEventListener("click", () => sendMessage(button.dataset.sample));
});

async function checkHealth() {
  try {
    const response = await fetch("/health");
    const payload = await response.json();
    health.textContent = payload.status === "healthy" ? "Healthy" : "Degraded";
    health.className = payload.status === "healthy" ? "health ok" : "health";
  } catch {
    health.textContent = "Offline";
    health.className = "health bad";
  }
}

addMessage("agent", "Hi, I can answer FAQ questions, create or check tickets, and escalate urgent issues.", "Routed to support_orchestrator");
checkHealth();
