#!/usr/bin/env python3
"""
Web Server per ReasoningEngine — Solo Chat.
"""

import http.server
import socketserver
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine import ReasoningEngine
from engine.ollama_tool import OllamaTool
from engine.finance_module import FinanceModule
from engine.datetime_tool import DateTimeTool

engine = ReasoningEngine()
ollama = OllamaTool(default_model='tinyllama')
finance = FinanceModule(engine.knowledge, engine.rules)
datetime_tool = DateTimeTool()

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
            font-family: system-ui, -apple-system, sans-serif;
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
            align-items: center;
            gap: 10px;
        }
        .header h1 {
            font-size: 1.2em;
            font-weight: 500;
        }
        .status {
            font-size: 0.8em;
            color: #8b949e;
        }
        .chat {
            flex: 1;
            overflow-y: auto;
            padding: 20px;
        }
        .message {
            margin-bottom: 15px;
            display: flex;
        }
        .message.user {
            justify-content: flex-end;
        }
        .message .bubble {
            max-width: 70%;
            padding: 12px 16px;
            border-radius: 18px;
            animation: fadeIn 0.2s;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(5px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .message.user .bubble {
            background: #238636;
            color: #fff;
            border-bottom-right-radius: 4px;
        }
        .message.bot .bubble {
            background: #21262d;
            border-bottom-left-radius: 4px;
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
        input::placeholder { color: #484f58; }
        button {
            padding: 12px 24px;
            border: none;
            border-radius: 20px;
            background: #238636;
            color: #fff;
            font-size: 1em;
            cursor: pointer;
            transition: background 0.2s;
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
        <div class="message bot">
            <div class="bubble">Ciao! Come posso aiutarti?</div>
        </div>
    </div>
    <div class="input-area">
        <input type="text" id="input" placeholder="Scrivi qui..." autofocus>
        <button onclick="send()">Invia</button>
    </div>
    <script>
        function addMsg(text, isUser) {
            const chat = document.getElementById('chat');
            const div = document.createElement('div');
            div.className = 'message ' + (isUser ? 'user' : 'bot');
            div.innerHTML = '<div class="bubble">' + text + '</div>';
            chat.appendChild(div);
            chat.scrollTop = chat.scrollHeight;
        }
        async function send() {
            const input = document.getElementById('input');
            const q = input.value.trim();
            if (!q) return;
            addMsg(q, true);
            input.value = '';
            document.getElementById('status').textContent = 'pensando...';
            try {
                const res = await fetch('/api/ask', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({question: q})
                });
                const data = await res.json();
                addMsg(data.answer || 'Non so rispondere', false);
            } catch(e) {
                addMsg('Errore: ' + e.message, false);
            }
            document.getElementById('status').textContent = 'pronto';
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
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        if self.path == '/api/ask':
            length = int(self.headers['Content-Length'])
            data = json.loads(self.rfile.read(length))
            q = data.get('question', '').lower()
            
            # Controlla se è una domanda su data/ora
            if any(word in q for word in ['giorno', 'data', 'ora', 'che giorno', 'che ore', 'calendario', 'domani', 'ieri']):
                if 'ora' in q or 'che ore' in q:
                    answer = f"Sono le {datetime_tool.time()}"
                elif 'domani' in q:
                    answer = f"Domani sarà {datetime_tool.add_days(1)}"
                elif 'ieri' in q:
                    answer = f"Ieri era {datetime_tool.add_days(-1)}"
                else:
                    answer = f"Oggi è {datetime_tool.today()}"
            
            else:
                # Usa l'engine normale
                result = engine.reason(data.get('question', ''))
                
                if result['answer'] and result['confidence'] > 0.5:
                    answer = str(result['answer'])
                elif ollama.is_available():
                    r = ollama.generate(data.get('question', ''))
                    answer = r.get('response', 'Non so rispondere')
                else:
                    answer = 'Non so rispondere'
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({'answer': answer}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass


if __name__ == '__main__':
    print(f'🌐 http://localhost:{PORT}')
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        httpd.serve_forever()
