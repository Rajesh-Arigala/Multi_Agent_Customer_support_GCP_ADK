const form = document.querySelector("#chatForm");
const input = document.querySelector("#messageInput");
const messages = document.querySelector("#messages");
const sendButton = document.querySelector("#sendButton");
const serviceStatus = document.querySelector("#serviceStatus");
const sourceStrip = document.querySelector("#sourceStrip");
const sourceTitle = document.querySelector("#sourceTitle");
const sourceScore = document.querySelector("#sourceScore");

const sessionId = `web-${Date.now().toString(36)}`;

async function refreshHealth() {
  try {
    const response = await fetch("/health");
    if (!response.ok) throw new Error("health check failed");
    serviceStatus.textContent = "Online";
    serviceStatus.classList.add("ok");
  } catch {
    serviceStatus.textContent = "Offline";
    serviceStatus.classList.remove("ok");
  }
}

function addMessage(role, text) {
  const article = document.createElement("article");
  article.className = `message ${role}`;
  const bubble = document.createElement("div");
  bubble.className = "bubble";
  const paragraph = document.createElement("p");
  renderMessageText(paragraph, text);
  bubble.appendChild(paragraph);
  article.appendChild(bubble);
  messages.appendChild(article);
  messages.scrollTop = messages.scrollHeight;
  return paragraph;
}

function renderMessageText(target, text) {
  target.replaceChildren();
  const lines = String(text || "").split("\n");
  lines.forEach((line, lineIndex) => {
    if (lineIndex > 0) target.appendChild(document.createElement("br"));
    appendInlineFormatting(target, line);
  });
}

function appendInlineFormatting(target, text) {
  const pattern = /(\*\*[^*]+\*\*|__[^_]+__)/g;
  let cursor = 0;
  for (const match of text.matchAll(pattern)) {
    if (match.index > cursor) {
      target.appendChild(document.createTextNode(text.slice(cursor, match.index)));
    }

    const token = match[0];
    const element = document.createElement(token.startsWith("**") ? "strong" : "u");
    element.textContent = token.slice(2, -2);
    target.appendChild(element);
    cursor = match.index + token.length;
  }

  if (cursor < text.length) {
    target.appendChild(document.createTextNode(text.slice(cursor)));
  }
}

function updateSource(retrieval) {
  if (!retrieval || !retrieval.title) {
    sourceStrip.hidden = true;
    return;
  }
  const score = typeof retrieval.score === "number" ? retrieval.score.toFixed(3) : retrieval.score || "n/a";
  sourceTitle.textContent = retrieval.title;
  sourceScore.textContent = `Grounding ${score}`;
  sourceStrip.hidden = false;
}

function autosize() {
  input.style.height = "auto";
  input.style.height = `${Math.min(input.scrollHeight, 138)}px`;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const message = input.value.trim();
  if (!message) return;

  addMessage("user", message);
  input.value = "";
  autosize();
  sendButton.disabled = true;
  const pending = addMessage("assistant", "Checking the clinic knowledge base...");

  try {
    const response = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, user_id: "web-guest", session_id: sessionId }),
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.detail || "Chat request failed");
    renderMessageText(pending, payload.message || "I could not prepare an answer for that.");
    updateSource(payload.data && payload.data.retrieval);
  } catch (error) {
    renderMessageText(pending, `Sorry, the assistant could not respond: ${error.message}`);
    updateSource(null);
  } finally {
    sendButton.disabled = false;
    input.focus();
  }
});

input.addEventListener("input", autosize);
refreshHealth();
