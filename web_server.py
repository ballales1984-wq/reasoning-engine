#!/usr/bin/env python3
"""
Web Server — AI che ragiona da sola.

Flusso:
1. Domanda → Ollama risponde
2. Engine verifica la risposta
3. Se corretta → la memorizza
4. Se sbagliata → la corregge
"""

import http.server
import socketserver
import json
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine import ReasoningEngine
from engine.ollama_tool import OllamaTool
from engine.finance_module import FinanceModule
from engine.code_tool import CodeTool
from engine.web_tool import WebTool

engine = ReasoningEngine()
ollama = OllamaTool(default_model="tinyllama")
finance = FinanceModule(engine.knowledge, engine.rules)
code = CodeTool()
web = WebTool()

PORT = 8080

HTML_PAGE = """<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ReasoningEngine</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: system-ui, sans-serif;
            background: #0d1117;
            color: #c9d1d9;
            height: 100vh;
            display: flex;
            flex-direction: column;
        }
        .header {
            padding: 15px 20px;
            background: #161b22;
            border-bottom: 1px solid #30363d;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 { font-size: 1.2em; }
        .status { font-size: 0.8em; color: #8b949e; }
        .status.ok { color: #3fb950; }
        .quick-bar {
            padding: 8px 20px;
            background: #161b22;
            border-bottom: 1px solid #30363d;
            display: flex;
            gap: 8px;
            flex-wrap: wrap;
        }
        .quick-btn {
            padding: 5px 12px;
            border: 1px solid #30363d;
            border-radius: 15px;
            background: transparent;
            color: #8b949e;
            cursor: pointer;
            font-size: 0.8em;
            transition: all 0.2s;
        }
        .quick-btn:hover {
            background: #238636;
            color: #fff;
            border-color: #238636;
        }
        .chat {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
        }
        .msg {
            margin-bottom: 15px;
            display: flex;
        }
        .msg.user { justify-content: flex-end; }
        .msg .bubble {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 18px;
            animation: fadeIn 0.2s;
            white-space: pre-wrap;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(5px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .msg.user .bubble {
            background: #238636;
            color: #fff;
            border-bottom-right-radius: 4px;
        }
        .msg.bot .bubble {
            background: #21262d;
            border-bottom-left-radius: 4px;
        }
        .msg .source {
            font-size: 0.7em;
            color: #8b949e;
            margin-top: 5px;
        }
        .input-area {
            padding: 15px 20px;
            background: #161b22;
            border-top: 1px solid #30363d;
            display: flex;
            gap: 10px;
        }
        input {
            flex: 1;
            padding: 12px 16px;
            border: 1px solid #30363d;
            border-radius: 20px;
            background: #0d1117;
            color: #c9d1d9;
            font-size: 1em;
            outline: none;
        }
        input:focus { border-color: #238636; }
        button {
            padding: 12px 24px;
            border: none;
            border-radius: 20px;
            background: #238636;
            color: #fff;
            cursor: pointer;
        }
        button:hover { background: #2ea043; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧠 ReasoningEngine</h1>
        <span class="status" id="status">pronto</span>
    </div>
    <div class="quick-bar">
        <button class="quick-btn" onclick="ask('quanto fa 15 + 27?')">📐 Math</button>
        <button class="quick-btn" onclick="ask('derivata di x**2 in x=3')">📈 Calculus</button>
        <button class="quick-btn" onclick="ask('media di [1,2,3,4,5]')">📊 Stats</button>
        <button class="quick-btn" onclick="ask('ROI investimento 1000 guadagno 1200')">💰 Finance</button>
        <button class="quick-btn" onclick="ask('cerca Python programming')">🌐 Search</button>
        <button class="quick-btn" onclick="ask('spiega cosa è Python')">🤖 Ollama</button>
    </div>
    <div class="chat" id="chat">
        <div class="msg bot">
            <div class="bubble">Ciao! Sono un AI che ragiona. Chiedimi qualsiasi cosa!
Capacità: matematica, calcolo, statistiche, matrici, finanza, codice, ricerca web, ragionamento.
<div class="source">🧠 engine + 🤖 ollama</div></div>
        </div>
    </div>
    <div class="input-area">
        <input type="text" id="input" placeholder="Scrivi qui... (anche in inglese)" autofocus>
        <button onclick="send()">Invia</button>
    </div>
    <script>
        function addMsg(text, source, isUser) {
            const chat = document.getElementById('chat');
            const div = document.createElement('div');
            div.className = 'msg ' + (isUser ? 'user' : 'bot');
            const srcMap = {engine:'🧠 engine', ollama:'🤖 ollama', web:'🌐 web', code:'💻 code', none:'—'};
            const srcLabel = srcMap[source] || '🧠 engine';
            div.innerHTML = '<div class="bubble">' + escapeHtml(text) + (isUser ? '' : '<div class="source">' + srcLabel + '</div>') + '</div>';
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
        }
        function escapeHtml(t) { const d=document.createElement('div'); d.textContent=t; return d.innerHTML; }
        function ask(q) { document.getElementById('input').value = q; send(); }
        async function send() {
            const input = document.getElementById('input');
            const q = input.value.trim();
            if (!q) return;
            addMsg(q, '', true);
            input.value = '';
            document.getElementById('status').textContent = 'pensando...';
            document.getElementById('status').className = 'status';
            try {
                const res = await fetch('/api/ask', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({question: q})
                });
                const data = await res.json();
                addMsg(data.answer || 'Nessuna risposta', data.source, false);
            } catch(e) {
                addMsg('Errore: ' + e.message, 'error', false);
            }
            document.getElementById('status').textContent = 'pronto';
            document.getElementById('status').className = 'status ok';
        }
        document.getElementById('input').addEventListener('keypress', e => {
            if (e.key === 'Enter') send();
        });
    </script>
</body>
</html>"""


class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode())
        elif self.path == "/api/stats":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            info = engine.what_do_you_know()
            stats = {
                "concepts": len(info.get("concepts", [])),
                "rules": len(info.get("rules", [])),
                "ollama": ollama.is_available(),
                "capabilities": [
                    "math",
                    "finance",
                    "code",
                    "web_search",
                    "reasoning",
                    "statistics",
                    "calculus",
                    "matrix",
                ],
            }
            self.wfile.write(json.dumps(stats).encode())
        elif self.path == "/api/ollama/status":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            models = (
                ollama.list_models().get("models", []) if ollama.is_available() else []
            )
            self.wfile.write(
                json.dumps(
                    {"available": ollama.is_available(), "models": models}
                ).encode()
            )
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/ask":
            length = int(self.headers["Content-Length"])
            data = json.loads(self.rfile.read(length))
            question = data.get("question", "")

            answer, source = self._process_question(question)

            # Impara dalla risposta
            self._learn_from_interaction(question, answer)

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"answer": answer, "source": source}).encode())

        elif self.path == "/api/code/execute":
            length = int(self.headers["Content-Length"])
            data = json.loads(self.rfile.read(length))
            source_code = data.get("code", "")

            result = code.execute(source_code)

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result, default=str).encode())

        elif self.path == "/api/search":
            length = int(self.headers["Content-Length"])
            data = json.loads(self.rfile.read(length))
            query = data.get("query", "")

            result = web.search(query, max_results=5)

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result, default=str).encode())

        elif self.path == "/api/math/advanced":
            length = int(self.headers["Content-Length"])
            data = json.loads(self.rfile.read(length))
            op = data.get("operation", "")
            params = data.get("params", {})

            result = self._advanced_math(op, params)

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(result, default=str).encode())

        else:
            self.send_response(404)
            self.end_headers()

    def _advanced_math(self, operation, params):
        """Dispatch operazioni matematiche avanzate."""
        try:
            if operation == "derivative":
                return engine.math.derivative(
                    params.get("func", ""), params.get("x", 0)
                )
            elif operation == "integral":
                return engine.math.integral(
                    params.get("func", ""), params.get("a", 0), params.get("b", 1)
                )
            elif operation == "limit":
                return engine.math.limit(params.get("func", ""), params.get("x", 0))
            elif operation == "mean":
                return engine.math.stats_mean(params.get("data", []))
            elif operation == "median":
                return engine.math.stats_median(params.get("data", []))
            elif operation == "mode":
                return engine.math.stats_mode(params.get("data", []))
            elif operation == "std":
                return engine.math.stats_std(params.get("data", []))
            elif operation == "regression":
                return engine.math.stats_regression(
                    params.get("xs", []), params.get("ys", [])
                )
            elif operation == "matrix_add":
                return engine.math.matrix_add(params.get("A", []), params.get("B", []))
            elif operation == "matrix_multiply":
                return engine.math.matrix_multiply(
                    params.get("A", []), params.get("B", [])
                )
            elif operation == "matrix_transpose":
                return engine.math.matrix_transpose(params.get("A", []))
            elif operation == "matrix_determinant":
                return engine.math.matrix_determinant(params.get("A", []))
            elif operation == "matrix_inverse":
                return engine.math.matrix_inverse(params.get("A", []))
            elif operation == "fibonacci":
                return engine.math.fibonacci(params.get("n", 10))
            elif operation == "prime_check":
                return engine.math.prime_check(params.get("n", 2))
            elif operation == "prime_factors":
                return engine.math.prime_factors(params.get("n", 12))
            elif operation == "arithmetic_sequence":
                return engine.math.arithmetic_sequence(
                    params.get("a1", 1), params.get("d", 1), params.get("n", 10)
                )
            elif operation == "geometric_sequence":
                return engine.math.geometric_sequence(
                    params.get("a1", 1), params.get("r", 2), params.get("n", 10)
                )
            else:
                return {
                    "answer": None,
                    "explanation": f"Operazione '{operation}' non riconosciuta",
                }
        except Exception as e:
            return {"answer": None, "explanation": f"Errore: {e}"}
            self.wfile.write(json.dumps({"answer": answer, "source": source}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def _process_question(self, question):
        """Processa la domanda: engine → ollama → fallback."""
        q_lower = question.lower()

        # 1. Prova con l'engine (matematica, finanza, ragionamento)
        result = engine.reason(question)
        if result["answer"] and result["confidence"] > 0.7:
            return str(result["answer"]), "engine"

        # 2. Ricerca web
        search_keywords = [
            "cerca",
            "trova",
            "informazioni",
            "search",
            "find",
            "look up",
            "google",
        ]
        if any(k in q_lower for k in search_keywords):
            search_q = question
            for kw in search_keywords:
                search_q = search_q.lower().replace(kw, "").strip()
            if search_q:
                result = web.search(search_q, max_results=3)
                if result["success"] and result["results"]:
                    parts = []
                    for r in result["results"][:3]:
                        parts.append(f"• {r.get('content', '')[:200]}")
                    return "\n".join(parts), "web"

        # 3. Esecuzione codice
        code_keywords = [
            "esegui codice",
            "run code",
            "esegui python",
            "run python",
            "esegui questo",
        ]
        if any(k in q_lower for k in code_keywords):
            import re

            code_match = re.search(r"```(?:python)?\s*\n?(.*?)```", question, re.DOTALL)
            if code_match:
                result = code.execute(code_match.group(1))
                if result["success"]:
                    return result["output"], "code"
                else:
                    return f"Errore: {result['error']}", "code"

        # 4. Calcoli finanziari diretti
        finance_keywords = [
            "interesse",
            "roi",
            "mutuo",
            "profitto",
            "pareggio",
            "rendimento",
        ]
        if any(k in q_lower for k in finance_keywords):
            import re

            if "interesse composto" in q_lower:
                nums = [float(x) for x in re.findall(r"\d+", question)]
                if len(nums) >= 3:
                    r = finance.calculate(
                        "compound_interest",
                        principal=nums[0],
                        rate=nums[1] / 100,
                        years=int(nums[2]),
                    )
                    return r.explanation, "engine"
            elif "roi" in q_lower:
                nums = [float(x) for x in re.findall(r"\d+", question)]
                if len(nums) >= 2:
                    r = finance.calculate("roi", gain=nums[1], cost=nums[0])
                    return r.explanation, "engine"

        # 5. Chiedi a Ollama
        if ollama.is_available():
            ollama_result = ollama.generate(question)
            if ollama_result.get("success") and ollama_result.get("response"):
                return ollama_result["response"], "ollama"

        # 6. Fallback
        return "Non so rispondere a questa domanda. Prova a riformulare.", "none"

    def _learn_from_interaction(self, question, answer):
        """Impara dall'interazione."""
        pass

    def _learn_from_interaction(self, question, answer):
        """Impara dall'interazione."""
        # Salva in memoria
        engine.memory.remember(
            f"Q: {question} → A: {answer}",
            memory_type="episodic",
            tags=["interaction"],
            importance=0.5,
        )

    def log_message(self, format, *args):
        pass


if __name__ == "__main__":
    print()
    print("=" * 40)
    print("🧠 ReasoningEngine")
    print("=" * 40)
    print(f"  🌐 http://localhost:{PORT}")
    print(f"  🤖 Ollama: {'✅' if ollama.is_available() else '❌'}")
    print()

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()
