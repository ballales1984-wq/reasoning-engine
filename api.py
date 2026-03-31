"""
ReasoningEngine API — Web server REST senza dipendenze esterne.

Endpoints:
  POST /reason      — Ragiona su una domanda
  POST /learn       — Insegna un concetto
  POST /learn/rule  — Insegna una regola
  GET  /knowledge   — Lista tutti i concetti
  GET  /knowledge/:name — Dettaglio concetto
  GET  /rules       — Lista tutte le regole
  POST /save        — Salva lo stato
  POST /load        — Carica lo stato
  GET  /health      — Health check

Avvio:
  python3 api.py                    # porta 8080
  python3 api.py --port 3000        # porta custom
  python3 api.py --llm-key sk-xxx   # con LLM
"""

import json
import sys
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Aggiungi il progetto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine import ReasoningEngine


# ============================================================
# ENGINE SINGLETON
# ============================================================

_engine = None

def get_engine(llm_key=None):
    global _engine
    if _engine is None:
        _engine = ReasoningEngine(llm_api_key=llm_key)
    return _engine


# ============================================================
# API HANDLER
# ============================================================

class APIHandler(BaseHTTPRequestHandler):
    """Handler per le richieste HTTP."""

    def log_message(self, format, *args):
        """Log compatto."""
        print(f"  {args[0]}")

    def _cors_headers(self):
        """Headers CORS per accesso da browser."""
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json_response(self, data, status=200):
        """Invia una risposta JSON."""
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self._cors_headers()
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8"))

    def _error(self, message, status=400):
        """Invia un errore."""
        self._json_response({"error": message}, status)

    def _read_body(self):
        """Legge il body della richiesta come JSON."""
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        body = self.rfile.read(length)
        return json.loads(body.decode("utf-8"))

    def do_OPTIONS(self):
        """Gestisce preflight CORS."""
        self.send_response(200)
        self._cors_headers()
        self.end_headers()

    def do_GET(self):
        """Gestisce le richieste GET."""
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")
        engine = get_engine()

        # Serve dashboard HTML
        if path in ("/", "/index.html", ""):
            dashboard_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dashboard.html")
            if os.path.exists(dashboard_path):
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self._cors_headers()
                self.end_headers()
                with open(dashboard_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self._error("Dashboard non trovata", 404)
            return

        if path == "/health":
            info = engine.what_do_you_know()
            self._json_response({
                "status": "ok",
                "concepts": info["stats"]["total_concepts"],
                "rules": info["stats"]["total_rules"],
            })

        elif path == "/knowledge":
            concepts = engine.knowledge.list_all()
            self._json_response({"concepts": concepts, "total": len(concepts)})

        elif path.startswith("/knowledge/"):
            name = path.split("/knowledge/", 1)[1]
            concept = engine.knowledge.get(name)
            if concept:
                self._json_response(concept.to_dict())
            else:
                self._error(f"Concetto '{name}' non trovato", 404)

        elif path == "/rules":
            rules = engine.rules.list_all()
            self._json_response({"rules": rules, "total": len(rules)})

        else:
            self._error("Endpoint non trovato", 404)

    def do_POST(self):
        """Gestisce le richieste POST."""
        parsed = urlparse(self.path)
        path = parsed.path.rstrip("/")

        try:
            body = self._read_body()
        except json.JSONDecodeError:
            self._error("Body non valido (JSON richiesto)")
            return

        engine = get_engine()

        # POST /reason
        if path == "/reason":
            question = body.get("question", "")
            use_llm = body.get("use_llm", False)

            if not question:
                self._error("'question' è obbligatorio")
                return

            result = engine.reason(question, use_llm=use_llm)
            self._json_response(result)

        # POST /learn
        elif path == "/learn":
            concept = body.get("concept", "")
            examples = body.get("examples", [])
            description = body.get("description", None)
            category = body.get("category", "general")

            if not concept:
                self._error("'concept' è obbligatorio")
                return

            engine.learn(concept, examples, description, category)
            self._json_response({
                "status": "ok",
                "message": f"Ho imparato: {concept}"
            })

        # POST /learn/rule
        elif path == "/learn/rule":
            name = body.get("name", "")
            description = body.get("description", "")

            if not name:
                self._error("'name' è obbligatorio")
                return

            # Le regole custom sono memorizzate come concetti speciali
            engine.knowledge.add(f"_rule_{name}", description=description, category="_custom_rule")
            self._json_response({
                "status": "ok",
                "message": f"Regola registrata: {name}"
            })

        # POST /connect
        elif path == "/connect":
            source = body.get("source", "")
            relation = body.get("relation", "")
            target = body.get("target", "")

            if not all([source, relation, target]):
                self._error("'source', 'relation', 'target' sono obbligatori")
                return

            engine.knowledge.add(source)
            engine.knowledge.add(target)
            engine.knowledge.connect(source, relation, target)
            self._json_response({
                "status": "ok",
                "message": f"Collegato: {source} → {relation} → {target}"
            })

        # POST /save
        elif path == "/save":
            name = body.get("name", "default")
            directory = body.get("directory", None)
            filepath = engine.save(name, directory)
            self._json_response({"status": "ok", "path": filepath})

        # POST /load
        elif path == "/load":
            name = body.get("name", "default")
            directory = body.get("directory", None)
            success = engine.load(name, directory)
            if success:
                self._json_response({"status": "ok", "message": f"Caricato: {name}"})
            else:
                self._error(f"Salvataggio '{name}' non trovato", 404)

        else:
            self._error("Endpoint non trovato", 404)


# ============================================================
# MAIN
# ============================================================

def main():
    import argparse

    parser = argparse.ArgumentParser(description="ReasoningEngine API")
    parser.add_argument("--port", type=int, default=8080, help="Porta (default: 8080)")
    parser.add_argument("--host", default="0.0.0.0", help="Host (default: 0.0.0.0)")
    parser.add_argument("--llm-key", default=None, help="OpenAI API key (opzionale)")
    args = parser.parse_args()

    # Inizializza engine
    engine = get_engine(args.llm_key)

    # Avvia server
    server = HTTPServer((args.host, args.port), APIHandler)

    info = engine.what_do_you_know()
    print("=" * 50)
    print("🧠 ReasoningEngine API")
    print("=" * 50)
    print(f"  Host: {args.host}:{args.port}")
    print(f"  Concetti: {info['stats']['total_concepts']}")
    print(f"  Regole: {info['stats']['total_rules']}")
    print(f"  LLM: {'✅ configurato' if args.llm_key else '❌ non configurato'}")
    print(f"\n  Endpoints:")
    print(f"    POST /reason       — Ragiona su una domanda")
    print(f"    POST /learn        — Insegna un concetto")
    print(f"    POST /connect      — Collega due concetti")
    print(f"    GET  /knowledge    — Lista concetti")
    print(f"    GET  /rules        — Lista regole")
    print(f"    POST /save         — Salva stato")
    print(f"    POST /load         — Carica stato")
    print(f"    GET  /health       — Health check")
    print(f"\n  Esempio:")
    print(f"    curl -X POST http://localhost:{args.port}/reason \\")
    print(f"      -H 'Content-Type: application/json' \\")
    print(f"      -d '{{\"question\": \"quanto fa 15 + 27?\"}}'")
    print("=" * 50)
    print(f"\n🚀 Server in ascolto su {args.host}:{args.port}...\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n👋 Server fermato.")
        server.server_close()


if __name__ == "__main__":
    main()
