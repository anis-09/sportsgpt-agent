/* SportsGPT — Frontend Logic */

let isWaiting = false;

const chatMessages = document.getElementById("chatMessages");
const messageInput = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const welcomeScreen = document.getElementById("welcomeScreen");
const sidebar = document.getElementById("sidebar");

document.addEventListener("DOMContentLoaded", () => {
    messageInput.focus();
    checkApiKey();

    messageInput.addEventListener("input", () => {
        messageInput.style.height = "auto";
        messageInput.style.height = Math.min(messageInput.scrollHeight, 120) + "px";
        sendBtn.disabled = messageInput.value.trim() === "";
    });

    messageInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
            e.preventDefault();
            if (!sendBtn.disabled && !isWaiting) sendMessage();
        }
    });
});

/* ── API Key Modal ── */
async function checkApiKey() {
    try {
        const res = await fetch("/api/check-key");
        const data = await res.json();
        if (!data.valid) showApiKeyModal();
    } catch (e) {
        console.error("Key check failed:", e);
    }
}

function showApiKeyModal() {
    document.getElementById("apiKeyModal").style.display = "flex";
    const input = document.getElementById("apiKeyInput");
    input.focus();
    input.addEventListener("keydown", (e) => {
        if (e.key === "Enter") saveApiKey();
    });
}

async function saveApiKey() {
    const key = document.getElementById("apiKeyInput").value.trim();
    if (!key) return;

    try {
        const res = await fetch("/api/set-key", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ key }),
        });
        const data = await res.json();
        if (data.success) {
            document.getElementById("apiKeyModal").style.display = "none";
        } else {
            alert("Invalid API key. Please try again.");
        }
    } catch (e) {
        alert("Error saving key. Please try again.");
    }
}

/* ── Send Message ── */
async function sendMessage() {
    const message = messageInput.value.trim();
    if (!message || isWaiting) return;

    if (welcomeScreen) welcomeScreen.style.display = "none";
    addMessage("user", message);
    messageInput.value = "";
    messageInput.style.height = "auto";
    sendBtn.disabled = true;
    showTyping();
    isWaiting = true;

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message }),
        });
        const data = await response.json();
        hideTyping();

        if (data.success) {
            addMessage("assistant", data.response, data.timestamp);
        } else {
            if (data.needs_key) {
                showApiKeyModal();
                addMessage("assistant", "🔑 Please set your Gemini API key first!", "", true);
            } else {
                addMessage("assistant", data.response || "Something went wrong!", "", true);
            }
        }
    } catch (error) {
        hideTyping();
        addMessage("assistant", "⚠️ Network error. Check connection and try again.", "", true);
    } finally {
        isWaiting = false;
    }
}

/* ── Add Message ── */
function addMessage(role, content, timestamp = "", isError = false) {
    const div = document.createElement("div");
    div.className = `message ${role}`;
    const avatar = role === "user" ? "👤" : "🏆";
    const time = timestamp || new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    const displayContent = role === "assistant" ? parseMarkdown(content) : escapeHtml(content);

    div.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
            <div class="message-bubble ${isError ? 'error-bubble' : ''}">${displayContent}</div>
            <div class="message-time">${time}</div>
        </div>`;
    chatMessages.appendChild(div);
    scrollToBottom();
}

/* ── Typing Indicator ── */
function showTyping() {
    const d = document.createElement("div");
    d.className = "typing-indicator"; d.id = "typingIndicator";
    d.innerHTML = `<div class="message-avatar" style="background:var(--bg-tertiary);border:1px solid var(--border-primary);">🏆</div>
        <div class="typing-dots"><div class="typing-dot"></div><div class="typing-dot"></div><div class="typing-dot"></div></div>`;
    chatMessages.appendChild(d);
    scrollToBottom();
}
function hideTyping() { const t = document.getElementById("typingIndicator"); if (t) t.remove(); }

/* ── Quick Actions ── */
function sendQuickQuery(btn) {
    messageInput.value = btn.getAttribute("data-query");
    sendBtn.disabled = false;
    sendMessage();
    if (window.innerWidth <= 768) toggleSidebar();
}
function sendSuggestion(el) {
    messageInput.value = el.getAttribute("data-query");
    sendBtn.disabled = false;
    sendMessage();
}

/* ── Clear ── */
async function clearConversation() {
    try { await fetch("/api/clear", { method: "POST" }); } catch (e) {}
    chatMessages.innerHTML = "";
    // Recreate welcome
    chatMessages.innerHTML = `
        <div class="welcome-screen" id="welcomeScreen">
            <div class="stadium-lights"><div class="light light-1"></div><div class="light light-2"></div><div class="light light-3"></div></div>
            <div class="welcome-badge"><div class="badge-ring"><span>🏆</span></div></div>
            <h2 class="welcome-title">Welcome to <span class="gradient-text">SportsGPT</span></h2>
            <p class="welcome-subtitle">Your Ultimate Sports Intelligence Agent</p>
            <div class="sport-categories">
                <div class="sport-cat" onclick="sendSuggestion(this)" data-query="Tell me the latest cricket world records and top batsmen"><div class="cat-icon">🏏</div><span>Cricket</span></div>
                <div class="sport-cat" onclick="sendSuggestion(this)" data-query="Tell me about the top football leagues and current champions"><div class="cat-icon">⚽</div><span>Football</span></div>
                <div class="sport-cat" onclick="sendSuggestion(this)" data-query="NBA current season highlights and top players stats"><div class="cat-icon">🏀</div><span>Basketball</span></div>
                <div class="sport-cat" onclick="sendSuggestion(this)" data-query="Grand Slam winners and current ATP/WTA rankings"><div class="cat-icon">🎾</div><span>Tennis</span></div>
                <div class="sport-cat" onclick="sendSuggestion(this)" data-query="Current F1 season standings and driver statistics"><div class="cat-icon">🏎️</div><span>Formula 1</span></div>
                <div class="sport-cat" onclick="sendSuggestion(this)" data-query="Olympic Games history, records and medal tallies"><div class="cat-icon">🥇</div><span>Olympics</span></div>
                <div class="sport-cat" onclick="sendSuggestion(this)" data-query="UFC and MMA current champions across all weight classes"><div class="cat-icon">🥊</div><span>MMA/UFC</span></div>
                <div class="sport-cat" onclick="sendSuggestion(this)" data-query="Pro Kabaddi League champions and best raiders of all time"><div class="cat-icon">🤼</div><span>Kabaddi</span></div>
            </div>
            <div class="welcome-divider"><span>or ask anything</span></div>
            <div class="welcome-suggestions">
                <button class="suggestion-chip" onclick="sendSuggestion(this)" data-query="Tell me about Virat Kohli's cricket records">🏏 Virat Kohli Records</button>
                <button class="suggestion-chip" onclick="sendSuggestion(this)" data-query="Who won the last FIFA World Cup?">⚽ FIFA World Cup</button>
                <button class="suggestion-chip" onclick="sendSuggestion(this)" data-query="LeBron vs Jordan - who is the GOAT?">🏀 LeBron vs Jordan</button>
                <button class="suggestion-chip" onclick="sendSuggestion(this)" data-query="India ka Olympic mein sabse achha performance kab raha?">🇮🇳 India Olympics</button>
            </div>
        </div>`;
    messageInput.focus();
}

/* ── Sidebar ── */
function toggleSidebar() {
    sidebar.classList.toggle("open");
    let overlay = document.querySelector(".sidebar-overlay");
    if (!overlay) { overlay = document.createElement("div"); overlay.className = "sidebar-overlay"; overlay.onclick = toggleSidebar; document.body.appendChild(overlay); }
    overlay.classList.toggle("active");
}

/* ── Utils ── */
function scrollToBottom() { requestAnimationFrame(() => { chatMessages.scrollTop = chatMessages.scrollHeight; }); }
function escapeHtml(t) { const d = document.createElement("div"); d.textContent = t; return d.innerHTML; }

/* ── Markdown Parser ── */
function parseMarkdown(text) {
    if (!text) return "";
    let html = escapeHtml(text);
    html = html.replace(/```(\w*)\n([\s\S]*?)```/g, (_, lang, code) => `<pre><code>${code.trim()}</code></pre>`);
    html = html.replace(/`([^`]+)`/g, "<code>$1</code>");
    html = html.replace(/^### (.+)$/gm, "<h3>$1</h3>");
    html = html.replace(/^## (.+)$/gm, "<h2>$1</h2>");
    html = html.replace(/^# (.+)$/gm, "<h1>$1</h1>");
    html = html.replace(/\*\*\*(.+?)\*\*\*/g, "<strong><em>$1</em></strong>");
    html = html.replace(/\*\*(.+?)\*\*/g, "<strong>$1</strong>");
    html = html.replace(/\*(.+?)\*/g, "<em>$1</em>");
    html = html.replace(/^&gt; (.+)$/gm, "<blockquote>$1</blockquote>");
    html = html.replace(/^---$/gm, "<hr>");
    html = parseTable(html);
    html = html.replace(/^[\-\*] (.+)$/gm, "<li>$1</li>");
    html = html.replace(/((?:<li>.*<\/li>\n?)+)/g, "<ul>$1</ul>");
    html = html.replace(/^\d+\. (.+)$/gm, "<li>$1</li>");
    html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" style="color:var(--text-accent);text-decoration:underline;">$1</a>');
    html = html.replace(/\n\n/g, "</p><p>");
    html = html.replace(/\n/g, "<br>");
    if (!html.startsWith("<h") && !html.startsWith("<ul") && !html.startsWith("<pre") && !html.startsWith("<table")) html = "<p>" + html + "</p>";
    html = html.replace(/<p><\/p>/g, "").replace(/<p><br><\/p>/g, "");
    return html;
}

function parseTable(text) {
    return text.replace(/(\|.+\|[\r\n]+\|[-| :]+\|[\r\n]+((?:\|.+\|[\r\n]*)+))/g, (match) => {
        const lines = match.trim().split("\n").filter(l => l.trim());
        if (lines.length < 3) return match;
        const hdr = lines[0].split("|").filter(c => c.trim()).map(c => c.trim());
        const rows = lines.slice(2);
        let t = "<table><thead><tr>" + hdr.map(c => `<th>${c}</th>`).join("") + "</tr></thead><tbody>";
        rows.forEach(r => { const cells = r.split("|").filter(c => c.trim()).map(c => c.trim()); t += "<tr>" + cells.map(c => `<td>${c}</td>`).join("") + "</tr>"; });
        return t + "</tbody></table>";
    });
}
