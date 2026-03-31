#!/usr/bin/env python3
"""
ReasoningEngine — Entry point per exe.

Usa: python main.py [opzione]
Opzioni:
  --demo      Demo completa
  --test      Esegui tutti i test
  --math      Demo matematica
  --finance   Demo finanza
  --prompt    Demo prompt engineering
  --web       Demo web + coding + ollama
  --interactive  Modalità interattiva
"""

import sys
import os

# Aggiungi il path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine import ReasoningEngine
from engine.prompt_engineering import PromptBuilder, PromptOptimizer


def demo_complete():
    """Demo completa."""
    engine = ReasoningEngine()
    builder = PromptBuilder(engine)
    
    print("=" * 50)
    print("🚀 REASONING ENGINE — DEMO COMPLETA")
    print("=" * 50)
    
    # Matematica
    print("\n📐 MATEMATICA")
    r = engine.reason('quanto fa 15 + 27?')
    print(f"  15 + 27 = {r['answer']}")
    
    r = engine.math.solve('area cerchio raggio 5')
    print(f"  Area cerchio (r=5) = {r['answer']:.2f}")
    
    # Deduzione
    print("\n🧠 DEDUZIONE")
    engine.learn('mammifero', examples=[], description='animale', category='biologia')
    engine.learn('animale', examples=[], description='essere vivente', category='biologia')
    engine.learn('gatto', examples=['miao'], description='mammifero', category='biologia')
    engine.knowledge.connect('gatto', 'è_un_tipo_di', 'mammifero')
    engine.knowledge.connect('mammifero', 'è_un_tipo_di', 'animale')
    r = engine.deductive.deduce('gatto')
    print(f"  Gatto → {r.conclusion}")
    
    # Prompt
    print("\n📝 PROMPT BUILDER")
    p = builder.build('Spiega il machine learning', style='semplice')
    print(f"  Prompt: {len(p.prompt)} caratteri")
    
    print("\n" + "=" * 50)
    print("✅ DEMO COMPLETATA!")
    print("=" * 50)


def run_tests():
    """Esegui tutti i test."""
    from test_all import main as test_main
    test_main()


def demo_math():
    """Demo matematica."""
    from demo_math import main as math_main
    math_main()


def demo_finance():
    """Demo finanza."""
    from demo_finance import main as finance_main
    finance_main()


def demo_prompt():
    """Demo prompt engineering."""
    from demo_prompt_engineering import main as prompt_main
    prompt_main()


def demo_web():
    """Demo web + coding + ollama."""
    from demo_web_code_ollama import main as web_main
    web_main()


def interactive():
    """Modalità interattiva."""
    engine = ReasoningEngine()
    builder = PromptBuilder(engine)
    
    print("=" * 50)
    print("🧠 REASONING ENGINE — Modalità Interattiva")
    print("=" * 50)
    print("Comandi:")
    print("  [domanda]     - Fai una domanda")
    print("  :math [expr]  - Calcolo matematico")
    print("  :prompt [task]- Genera prompt")
    print("  :learn [x]    - Insegna concetto")
    print("  :quit         - Esci")
    print()
    
    while True:
        try:
            user_input = input("Tu> ").strip()
            
            if not user_input:
                continue
            
            if user_input == ":quit":
                print("Arrivederci!")
                break
            
            elif user_input.startswith(":math "):
                expr = user_input[6:]
                result = engine.math.solve(expr)
                print(f"  → {result['explanation']}")
            
            elif user_input.startswith(":prompt "):
                task = user_input[8:]
                p = builder.build(task)
                print(f"  → Prompt ({len(p.prompt)} char):")
                print(f"  {p.prompt[:200]}...")
            
            elif user_input.startswith(":learn "):
                concept = user_input[7:]
                engine.learn(concept, examples=[], description=concept)
                print(f"  → Imparato: {concept}")
            
            else:
                result = engine.reason(user_input)
                if result['answer']:
                    print(f"  → {result['answer']}")
                else:
                    print(f"  → Non so rispondere a questa domanda")
        
        except KeyboardInterrupt:
            print("\nArrivederci!")
            break
        except Exception as e:
            print(f"  Errore: {e}")


def main():
    """Entry point principale."""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "--demo":
            demo_complete()
        elif command == "--test":
            run_tests()
        elif command == "--math":
            demo_math()
        elif command == "--finance":
            demo_finance()
        elif command == "--prompt":
            demo_prompt()
        elif command == "--web":
            demo_web()
        elif command == "--interactive":
            interactive()
        else:
            print(f"Comando sconosciuto: {command}")
            print("Usa: --demo, --test, --math, --finance, --prompt, --web, --interactive")
    else:
        # Default: demo
        demo_complete()


if __name__ == "__main__":
    main()
