#!/usr/bin/env python3
"""
Web Server per ReasoningEngine.

Avvia un'interfaccia web su http://localhost:8080
"""

import http.server
import socketserver
import json
import os
import sys
import urllib.parse

# Aggiungi il path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine import ReasoningEngine
from engine.ollama_tool import OllamaTool
from engine.finance_module import FinanceModule
from engine.prompt_engineering import PromptBuilder

# Inizializza engine
engine = ReasoningEngine()
ollama = OllamaTool(default_model='tinyllama')
finance = FinanceModule(engine.knowledge, engine.rules)
builder = PromptBuilder(engine)

PORT = 8080

HTML_PAGE = """
<!DOCTYPE html>
<html lang="it">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🧠 ReasoningEngine</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #fff;
            min-height: 100vh;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
        .header {
            text-align: center;
            padding: 40px 0;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(90deg, #00d2ff, #3a7bd5);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .header p {
            color: #888;
            font-size: 1.1em;
        }
        .chat-box {
            background: rgba(255,255,255,0.05);
            border-radius: 15px;
            padding: 20px;
            margin-bottom: 20px;
            min-height: 300px;
            max-height: 500px;
            overflow-y: auto;
        }
        .message {
            margin-bottom: 15px;
            padding: 10px 15px;
            border-radius: 10px;
            animation: fadeIn 0.3s;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .user-message {
            background: #3a7bd5;
            margin-left: 20%;
            text-align: right;
        }
        .bot-message {
            background: rgba(255,255,255,0.1);
            margin-right: 20%;
        }
        .input-area {
            display: flex;
            gap: 10px;
        }
        .input-area input {
            flex: 1;
            padding: 15px;
            border: none;
            border-radius: 10px;
            background: rgba(255,255,255,0.1);
            color: #fff;
            font-size: 1em;
            outline: none;
        }
        .input-area input::placeholder {
            color: #666;
        }
        .input-area button {
            padding: 15px 30px;
            border: none;
            border-radius: 10px;
            background: linear-gradient(90deg, #00d2ff, #3a7bd5);
            color: #fff;
            font-size: 1em;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .input-area button:hover {
            transform: scale(1.05);
        }
        .quick-buttons {
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
            margin-bottom: 20px;
        }
        .quick-btn {
            padding: 8px 15px;
            border: 1px solid #3a7bd5;
            border-radius: 20px;
            background: transparent;
            color: #3a7bd5;
            cursor: pointer;
            font-size: 0.9em;
            transition: all 0.2s;
        }
        .quick-btn:hover {
            background: #3a7bd5;
            color: #fff;
        }
        .status {
            text-align: center;
            color: #888;
            font-size: 0.9em;
            margin-top: 10px;
        }
        .ollama-status {
            display: inline-block;
            padding: 5px 10px;
            border-radius: 10px;
            font-size: 0.8em;
        }
        .ollama-ok { background: #2ecc71; color: #fff; }
        .ollama-off { background: #e74c3c; color: #fff; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🧠 ReasoningEngine</h1>
            <p>Un AI che ragiona come un umano</p>
            <div class="status">
                Ollama: <span id="ollama-status" class="ollama-status ollama-off">Verifica...</span>
            </div>
        </div>
        
        <div class="quick-buttons">
            <button class="quick-btn" onclick="ask('quanto fa 15 + 27?')">📐 Matematica</button>
            <button class="quick-btn" onclick="ask('area cerchio raggio 5')">📐 Geometria</button>
            <button class="quick-btn" onclick="ask('ROI investimento 1000 guadagno 1200')">💰 Finanza</button>
            <button class="quick-btn" onclick="ask('spiega cosa è Python')">🤖 Ollama</button>
            <button class="quick-btn" onclick="ask('genera prompt per machine learning')">📝 Prompt</button>
        </div>
        
        <div class="chat-box" id="chat-box">
            <div class="message bot-message">
                Ciao! Sono ReasoningEngine. Prova a chiedermi qualcosa! 🧠
            </div>
        </div>
        
        <div class="input-area">
            <input type="text" id="user-input" placeholder="Scrivi una domanda..." onkeypress="if(event.key==='Enter')send()">
            <button onclick="send()">Invia</button>
        </div>
    </div>
    
    <script>
        function addMessage(text, isUser) {
            const chatBox = document.getElementById('chat-box');
            const div = document.createElement('div');
            div.className = 'message ' + (isUser ? 'user-message' : 'bot-message');
            div.textContent = text;
            chatBox.appendChild(div);
            chatBox.scrollTop = chatBox.scrollHeight;
        }
        
        function ask(question) {
            document.getElementById('user-input').value = question;
            send();
        }
        
        async function send() {
            const input = document.getElementById('user-input');
            const question = input.value.trim();
            if (!question) return;
            
            addMessage(question, true);
            input.value = '';
            
            try {
                const response = await fetch('/api/ask', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ question: question })
                });
                
                const data = await response.json();
                addMessage(data.answer || data.response || 'Non so rispondere', false);
            } catch (e) {
                addMessage('Errore: ' + e.message, false);
            }
        }
        
        // Check Ollama status
        async function checkOllama() {
            try {
                const response = await fetch('/api/ollama/status');
                const data = await response.json();
                const status = document.getElementById('ollama-status');
                if (data.available) {
                    status.textContent = '✅ Attivo';
                    status.className = 'ollama-status ollama-ok';
                } else {
                    status.textContent = '❌ Non disponibile';
                    status.className = 'ollama-status ollama-off';
                }
            } catch (e) {
                document.getElementById('ollama-status').textContent = '❌ Errore';
            }
        }
        
        checkOllama();
    </script>
</body>
</html>
"""


class RequestHandler(http.server.SimpleHTTPRequestHandler):
    """Handler per le richieste HTTP."""
    
    def do_GET(self):
        """Gestisce le richieste GET."""
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html; charset=utf-8')
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode('utf-8'))
        
        elif self.path == '/api/ollama/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = json.dumps({
                "available": ollama.is_available(),
                "models": ollama.list_models().get('models', []) if ollama.is_available() else []
            })
            self.wfile.write(response.encode('utf-8'))
        
        elif self.path == '/api/stats':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            stats = engine.what_do_you_know()
            response = json.dumps({
                "concepts": len(stats.get('concepts', [])),
                "rules": len(stats.get('rules', [])),
                "memory": stats.get('memory_stats', {})
            })
            self.wfile.write(response.encode('utf-8'))
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_POST(self):
        """Gestisce le richieste POST."""
        if self.path == '/api/ask':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode('utf-8'))
            
            question = data.get('question', '')
            
            # Prova con l'engine
            result = engine.reason(question)
            
            if result['answer'] and result['confidence'] > 0.5:
                response = {
                    "answer": str(result['answer']),
                    "confidence": result['confidence'],
                    "source": "engine"
                }
            elif ollama.is_available():
                # Fallback a Ollama
                ollama_result = ollama.generate(question)
                response = {
                    "answer": ollama_result.get('response', 'Non so rispondere'),
                    "source": "ollama"
                }
            else:
                response = {
                    "answer": f"Non so rispondere a: {question}",
                    "source": "none"
                }
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(response).encode('utf-8'))
        
        else:
            self.send_response(404)
            self.end_headers()
    
    def log_message(self, format, *args):
        """Log delle richieste."""
        print(f"[{self.log_date_time_string()}] {format % args}")


def main():
    """Avvia il server web."""
    print()
    print("=" * 50)
    print("🧠 ReasoningEngine — Web Server")
    print("=" * 50)
    print()
    print(f"  🌐 Server avviato su http://localhost:{PORT}")
    print(f"  🤖 Ollama: {'✅ Disponibile' if ollama.is_available() else '❌ Non disponibile'}")
    print()
    print("  Premi Ctrl+C per fermare")
    print()
    
    with socketserver.TCPServer(("", PORT), RequestHandler) as httpd:
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n  Server fermato.")


if __name__ == "__main__":
    main()
