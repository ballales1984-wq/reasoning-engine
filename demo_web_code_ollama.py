#!/usr/bin/env python3
"""
Demo Web + Coding + Ollama — Tre nuove funzionalità.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.web_tool import WebTool
from engine.code_tool import CodeTool
from engine.ollama_tool import OllamaTool


def main():
    print("=" * 60)
    print("🌐 Web + 💻 Coding + 🤖 Ollama")
    print("=" * 60)
    print()
    
    # === WEB TOOL ===
    print("🌐 WEB TOOL — Ricerca online")
    print("-" * 40)
    
    web = WebTool()
    
    # Ricerca
    result = web.search("Python programming language")
    if result['success']:
        print(f"  Query: {result['query']}")
        print(f"  Risultati: {result['count']}")
        for r in result['results'][:2]:
            print(f"    • {r.get('content', '')[:100]}...")
    else:
        print(f"  Errore: {result['error']}")
    
    print()
    
    # === CODE TOOL ===
    print("💻 CODE TOOL — Coding")
    print("-" * 40)
    
    code = CodeTool()
    
    # Esegui codice
    result = code.execute('print("Hello from ReasoningEngine!")')
    print(f"  Esecuzione: {'✅' if result['success'] else '❌'}")
    print(f"  Output: {result.get('output', '').strip()}")
    
    # Analizza codice
    test_code = '''
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

class Calculator:
    def add(self, a, b):
        return a + b
'''
    analysis = code.analyze(test_code)
    print(f"  Funzioni trovate: {len(analysis['functions'])}")
    print(f"  Classi trovate: {len(analysis['classes'])}")
    print(f"  Righe: {analysis['lines']}")
    
    # Genera codice
    generated = code.generate("funzione che calcola il fattoriale")
    print(f"  Codice generato: {len(generated['code'])} caratteri")
    
    # Debug
    debug = code.debug("print(x)", "NameError: name 'x' is not defined")
    print(f"  Suggerimenti debug: {debug['count']}")
    for s in debug['suggestions']:
        print(f"    • {s}")
    
    print()
    
    # === OLLAMA TOOL ===
    print("🤖 OLLAMA TOOL — LLM Locale")
    print("-" * 40)
    
    ollama = OllamaTool()
    
    if ollama.is_available():
        print("  ✅ Ollama disponibile!")
        
        # Lista modelli
        models = ollama.list_models()
        if models['success']:
            print(f"  Modelli: {models['count']}")
            for m in models['models'][:3]:
                print(f"    • {m['name']}")
        
        # Genera risposta
        result = ollama.generate("Cosa è Python in una frase?")
        if result['success']:
            print(f"  Risposta: {result['response'][:200]}")
    
    else:
        print("  ⚠️ Ollama non disponibile")
        print("  Per usarlo:")
        print("    1. Installa Ollama: curl -fsSL https://ollama.com/install.sh | sh")
        print("    2. Scarica un modello: ollama pull llama3.2")
        print("    3. Avvia: ollama serve")
    
    print()
    
    # === RIEPILOGO ===
    print("=" * 60)
    print("🎯 NUOVE FUNZIONALITÀ:")
    print()
    print("  🌐 Web Tool")
    print("    • Ricerca online (DuckDuckGo)")
    print("    • Lettura pagine web")
    print("    • Estrazione informazioni")
    print()
    print("  💻 Code Tool")
    print("    • Esecuzione codice Python")
    print("    • Analisi statica")
    print("    • Generazione codice")
    print("    • Debug suggerimenti")
    print()
    print("  🤖 Ollama Tool")
    print("    • LLM locale (Llama, Mistral, etc.)")
    print("    • Chat conversazionale")
    print("    • Generazione testo")
    print("    • Embedding")
    print("    • Download modelli")
    print("=" * 60)


if __name__ == "__main__":
    main()
