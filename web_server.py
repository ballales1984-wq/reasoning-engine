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
from engine.datetime_tool import DateTimeTool

engine = ReasoningEngine()
ollama = OllamaTool(default_model='tinyllama')
finance = FinanceModule(engine.knowledge, engine.rules)
dt = DateTimeTool()

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
    <div class="chat" id="chat">
        <div class="msg bot">
            <div class="bubble">Ciao! Sono un AI che ragiona. Chiedimi qualsiasi cosa!<div class="source">🧠 engine + 🤖 ollama</div></div>
        </div>
    </div>
    <div class="input-area">
        <input type="text" id="input" placeholder="Scrivi qui..." autofocus>
        <button onclick="send()">Invia</button>
    </div>
    <script>
        function addMsg(text, source, isUser) {
            const chat = document.getElementById('chat');
            const div = document.createElement('div');
            div.className = 'msg ' + (isUser ? 'user' : 'bot');
            const srcLabel = source === 'engine' ? '🧠 engine' : source === 'ollama' ? '🤖 ollama' : '🧠 engine';
            div.innerHTML = '<div class="bubble">' + text + (isUser ? '' : '<div class="source">' + srcLabel + '</div>') + '</div>';
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
        }
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
                addMsg(data.answer, data.source, false);
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
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode())
        elif self.path == '/api/stats':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            info = engine.what_do_you_know()
            stats = {
                "concepts": len(info.get('concepts', [])),
                "rules": len(info.get('rules', [])),
                "ollama": ollama.is_available()
            }
            self.wfile.write(json.dumps(stats).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/api/ask':
            length = int(self.headers['Content-Length'])
            data = json.loads(self.rfile.read(length))
            question = data.get('question', '')
            
            answer, source = self._process_question(question)
            
            # Impara dalla risposta
            self._learn_from_interaction(question, answer)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                'answer': answer,
                'source': source
            }).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def _process_question(self, question):
        """Processa la domanda: engine → ollama → fallback."""
        q_lower = question.lower()
        
        # 1. Prova con l'engine (matematica, finanza, ragionamento)
        result = engine.reason(question)
        if result['answer'] and result['confidence'] > 0.7:
            return str(result['answer']), 'engine'
        
        # 2. Calcoli finanziari diretti
        finance_keywords = ['interesse', 'roi', 'mutuo', 'profitto', 'pareggio', 'rendimento']
        if any(k in q_lower for k in finance_keywords):
            # Prova a calcolare
            if 'interesse composto' in q_lower:
                import re
                nums = [float(x) for x in re.findall(r'\d+', question)]
                if len(nums) >= 3:
                    r = finance.calculate('compound_interest', principal=nums[0], rate=nums[1]/100, years=int(nums[2]))
                    return r.explanation, 'engine'
            elif 'roi' in q_lower:
                import re
                nums = [float(x) for x in re.findall(r'\d+', question)]
                if len(nums) >= 2:
                    r = finance.calculate('roi', gain=nums[1], cost=nums[0])
                    return r.explanation, 'engine'
        
        # 3. Data e ora
        if any(k in q_lower for k in ['giorno', 'data', 'ora', 'ore', 'domani', 'ieri', 'calendario']):
            if 'ora' in q_lower or 'ore' in q_lower:
                return f"Sono le {dt.time()}", 'engine'
            elif 'domani' in q_lower:
                return f"Domani sarà {dt.add_days(1)}", 'engine'
            elif 'ieri' in q_lower:
                return f"Ieri era {dt.add_days(-1)}", 'engine'
            else:
                return f"Oggi è {dt.today()}", 'engine'
        
        # 4. Chiedi a Ollama
        if ollama.is_available():
            ollama_result = ollama.generate(question)
            if ollama_result.get('success') and ollama_result.get('response'):
                return ollama_result['response'], 'ollama'
        
        # 5. Fallback
        return "Non so rispondere a questa domanda. Prova a riformulare.", 'none'
    
    def _learn_from_interaction(self, question, answer):
        """Impara dall'interazione."""
        # Salva in memoria
        engine.memory.remember(
            f"Q: {question} → A: {answer}",
            memory_type="episodic",
            tags=["interaction"],
            importance=0.5
        )
    
    def log_message(self, format, *args):
        pass


if __name__ == '__main__':
    print()
    print("=" * 40)
    print("🧠 ReasoningEngine")
    print("=" * 40)
    print(f"  🌐 http://localhost:{PORT}")
    print(f"  🤖 Ollama: {'✅' if ollama.is_available() else '❌'}")
    print()
    
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()
