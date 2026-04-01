#!/usr/bin/env python3
"""
app.py -- FastAPI Web UI per ReasoningEngine.

Avvio: python app.py
Apri: http://localhost:8000

Dipendenze: pip install fastapi uvicorn
"""

import os
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from engine import ReasoningEngine

app = FastAPI(title="ReasoningEngine v2.0", version="2.0.0")
engine = ReasoningEngine()


HTML_PAGE = """<!DOCTYPE html>
<html lang="it">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>ReasoningEngine v2.0</title>
<style>
* { box-sizing: border-box; margin: 0; padding: 0; }
body { font-family: 'Segoe UI', system-ui, sans-serif; background: #0d1117; color: #c9d1d9; height: 100vh; display: flex; flex-direction: column; }
header { background: #161b22; padding: 16px 24px; border-bottom: 1px solid #30363d; display: flex; align-items: center; gap: 12px; }
header h1 { font-size: 18px; color: #58a6ff; }
header .badge { font-size: 11px; background: #238636; padding: 2px 8px; border-radius: 10px; }
#chat { flex: 1; overflow-y: auto; padding: 20px; display: flex; flex-direction: column; gap: 16px; }
.msg { max-width: 80%; padding: 12px 16px; border-radius: 12px; line-height: 1.5; font-size: 14px; }
.msg.user { align-self: flex-end; background: #1f6feb; color: #fff; border-bottom-right-radius: 4px; }
.msg.bot { align-self: flex-start; background: #21262d; border: 1px solid #30363d; border-bottom-left-radius: 4px; }
.msg .meta { font-size: 11px; color: #8b949e; margin-top: 6px; }
.msg.bot .meta { color: #58a6ff; }
.msg.bot .explanation { margin-top: 8px; padding-top: 8px; border-top: 1px solid #30363d; font-size: 12px; color: #8b949e; }
.msg.bot .steps { margin-top: 6px; font-size: 12px; }
.msg.bot .step { padding: 2px 0; }
#input-area { background: #161b22; border-top: 1px solid #30363d; padding: 16px 24px; display: flex; gap: 12px; }
#input-area input { flex: 1; background: #0d1117; border: 1px solid #30363d; color: #c9d1d9; padding: 12px 16px; border-radius: 8px; font-size: 14px; outline: none; }
#input-area input:focus { border-color: #58a6ff; }
#input-area button { background: #238636; color: #fff; border: none; padding: 12px 24px; border-radius: 8px; cursor: pointer; font-size: 14px; font-weight: 600; }
#input-area button:hover { background: #2ea043; }
#input-area button:disabled { background: #21262d; color: #484f58; cursor: not-allowed; }
.typing { display: inline-block; }
.typing span { animation: blink 1s infinite; }
@keyframes blink { 0%, 100% { opacity: 1; } 50% { opacity: 0.3; } }
</style>
</head>
<body>
<header>
  <h1>ReasoningEngine v2.0</h1>
  <span class="badge">FastAPI</span>
</header>
<div id="chat">
  <div class="msg bot">Ciao! Sono ReasoningEngine. Fai una domanda e ragionero per risponderti.<br><div class="meta">Motore multi-agent con deduzione, induzione e analogia.</div></div>
</div>
<div id="input-area">
  <input id="msg" type="text" placeholder="Scrivi una domanda..." autocomplete="off" />
  <button id="send" onclick="sendMsg()">Invia</button>
</div>
<script>
const chat = document.getElementById("chat");
const input = document.getElementById("msg");
const btn = document.getElementById("send");

input.addEventListener("keydown", e => { if (e.key === "Enter") sendMsg(); });

async function sendMsg() {
  const text = input.value.trim();
  if (!text) return;
  input.value = "";
  btn.disabled = true;

  addMsg(text, "user");
  const typing = addMsg('<span class="typing"><span>...</span></span>', "bot");

  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({message: text})
    });
    const data = await res.json();
    typing.remove();
    renderBotMsg(data);
  } catch (e) {
    typing.remove();
    addMsg("Errore di connessione: " + e.message, "bot");
  }
  btn.disabled = false;
  input.focus();
}

function addMsg(html, cls) {
  const div = document.createElement("div");
  div.className = "msg " + cls;
  div.innerHTML = html;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
  return div;
}

function renderBotMsg(data) {
  let html = data.answer || "Non ho trovato una risposta.";

  if (data.steps && data.steps.length > 0) {
    html += '<div class="steps">';
    data.steps.forEach(s => {
      html += `<div class="step">- ${s.description}</div>`;
    });
    html += '</div>';
  }

  html += `<div class="meta">Tipo: ${data.reasoning_type} | Confidenza: ${(data.confidence * 100).toFixed(0)}% | Verificato: ${data.verified ? "Si" : "No"}</div>`;

  if (data.explanation) {
    html += `<div class="explanation">${data.explanation}</div>`;
  }

  addMsg(html, "bot");
}
</script>
</body>
</html>"""


@app.get("/", response_class=HTMLResponse)
async def home():
    return HTML_PAGE


@app.post("/api/chat")
async def chat_api(request: Request):
    body = await request.json()
    message = body.get("message", "")
    if not message:
        return JSONResponse({"error": "messaggio vuoto"}, status_code=400)

    result = engine.reason(message)

    steps_data = []
    if result.steps:
        for s in result.steps:
            steps_data.append(
                {
                    "type": s.type,
                    "description": s.description,
                    "channel": s.channel,
                }
            )

    return {
        "answer": result.answer,
        "confidence": result.confidence,
        "reasoning_type": result.reasoning_type,
        "verified": result.verified,
        "explanation": result.explanation,
        "steps": steps_data,
    }


@app.get("/api/knowledge")
async def knowledge_api():
    info = engine.what_do_you_know()
    return info


@app.post("/api/learn")
async def learn_api(request: Request):
    body = await request.json()
    concept = body.get("concept", "")
    examples = body.get("examples", [])
    description = body.get("description", "")
    category = body.get("category", "general")

    if not concept:
        return JSONResponse({"error": "concept richiesto"}, status_code=400)

    result = engine.learn(concept, examples, description, category)
    return {"result": result}


if __name__ == "__main__":
    print("[SERVER] Avvio ReasoningEngine su http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)
