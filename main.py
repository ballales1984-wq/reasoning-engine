#!/usr/bin/env python3
"""
ReasoningEngine — Applicazione completa con menu interattivo.

Auto-rileva Ollama installato e modelli disponibili.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine import ReasoningEngine
from engine.llm.ollama import OllamaTool
from engine.tools.finance import FinanceModule
from engine.llm.prompt_engineering import PromptBuilder, PromptOptimizer


def print_header():
    """Header dell'applicazione."""
    print()
    print("╔══════════════════════════════════════════════════╗")
    print("║        🧠 REASONING ENGINE v2.0                 ║")
    print("║        AI che ragiona come un umano             ║")
    print("╚══════════════════════════════════════════════════╝")
    print()


def detect_ollama():
    """Rileva Ollama e modelli disponibili."""
    ollama = OllamaTool()

    if not ollama.is_available():
        return None, []

    models_result = ollama.list_models()
    models = models_result.get("models", []) if models_result.get("success") else []

    return ollama, models


def menu_ollama(ollama, models):
    """Menu per gestione Ollama."""
    print()
    print("🤖 GESTIONE OLLAMA")
    print("-" * 40)

    if not ollama:
        print("  ⚠️ Ollama non trovato!")
        print()
        print("  Per installare Ollama:")
        print("    1. Vai su https://ollama.com")
        print("    2. Scarica e installa")
        print("    3. Avvia: ollama serve")
        print("    4. Scarica un modello: ollama pull tinyllama")
        return None

    print(f"  ✅ Ollama disponibile!")
    print(f"  Modelli trovati: {len(models)}")
    print()

    if not models:
        print("  Nessun modello trovato!")
        print("  Scarica un modello:")
        print("    ollama pull tinyllama    (637MB, leggero)")
        print("    ollama pull phi3:mini    (2.2GB, migliore)")
        print("    ollama pull llama3.2     (2GB, buono)")
        return None

    print("  Modelli disponibili:")
    for i, m in enumerate(models, 1):
        size_gb = m.get("size", 0) / 1e9
        print(f"    {i}. {m['name']} ({size_gb:.1f} GB)")

    print()
    scelta = input("  Scegli modello (numero) o INVIO per TinyLlama: ").strip()

    if scelta.isdigit() and 1 <= int(scelta) <= len(models):
        model_name = models[int(scelta) - 1]["name"]
    else:
        # Cerca TinyLlama o primo disponibile
        model_name = next(
            (m["name"] for m in models if "tinyllama" in m["name"].lower()),
            models[0]["name"],
        )

    print(f"  ✅ Modello selezionato: {model_name}")
    return model_name


def menu_chat(engine, ollama, model_name):
    """Menu chat interattiva."""
    print()
    print("💬 CHAT CON REASONING ENGINE")
    print("-" * 40)
    print("  Comandi:")
    print("    [testo]       - Fai una domanda")
    print("    :math [expr]  - Calcolo matematico")
    print("    :finance      - Calcolo finanziario")
    print("    :prompt [txt] - Genera prompt")
    print("    :learn [x]    - Insegna concetto")
    print("    :info         - Mostra statistiche")
    print("    :menu         - Torna al menu")
    print("    :quit         - Esci")
    print()

    finance = FinanceModule(engine.knowledge, engine.rules)
    builder = PromptBuilder(engine)

    while True:
        try:
            user_input = input("Tu> ").strip()

            if not user_input:
                continue

            if user_input == ":quit":
                print("Arrivederci! 👋")
                return "quit"

            if user_input == ":menu":
                return "menu"

            if user_input == ":info":
                info = engine.what_do_you_know()
                print(f"  📊 Concetti: {len(info['concepts'])}")
                print(f"  📊 Regole: {len(info['rules'])}")
                continue

            if user_input.startswith(":math "):
                expr = user_input[6:]
                result = engine.math.solve(expr)
                print(f"  → {result['explanation']}")
                continue

            if user_input.startswith(":finance"):
                print("  Calcoli finanziari:")
                print("    1. Interesse composto")
                print("    2. ROI")
                print("    3. Mutuo")
                scelta = input("  Scegli: ").strip()

                if scelta == "1":
                    p = float(input("  Capitale: "))
                    r = float(input("  Tasso (es. 0.07): "))
                    t = int(input("  Anni: "))
                    result = finance.calculate(
                        "compound_interest", principal=p, rate=r, years=t
                    )
                    print(f"  → {result.explanation}")
                elif scelta == "2":
                    g = float(input("  Guadagno: "))
                    c = float(input("  Costo: "))
                    result = finance.calculate("roi", gain=g, cost=c)
                    print(f"  → {result.explanation}")
                elif scelta == "3":
                    p = float(input("  Importo mutuo: "))
                    r = float(input("  Tasso mensile (es. 0.003): "))
                    m = int(input("  Mesi: "))
                    result = finance.calculate(
                        "mortgage_payment", principal=p, monthly_rate=r, months=m
                    )
                    print(f"  → {result.explanation}")
                continue

            if user_input.startswith(":prompt "):
                task = user_input[8:]
                p = builder.build(task)
                print(f"  → Prompt generato ({len(p.prompt)} char):")
                print(f"  {p.prompt[:300]}...")
                continue

            if user_input.startswith(":math "):
                expr = user_input[6:]
                # Prova prima la risoluzione simbolica
                if "x" in expr or "=" in expr:
                    result = engine.math.solve_symbolically(expr)
                    if result["success"]:
                        print(f"  → Soluzioni simboliche: {result['solutions']}")
                        print(f"  → Espressione semplificata: {result['simplified_expression']}")
                        continue
                
                result = engine.math.solve(expr)
                print(f"  → {result['explanation']}")
                continue

            # Altrimenti usa ragionamento + Ollama
            result = engine.reason(user_input)

            if result.answer and result.confidence > 0.5:
                print(f"  🧠 {result.answer}")
                # Mostra la fonte se disponibile
                if result.sources:
                    best_source = max(result.sources, key=lambda s: s.trust_score)
                    print(f"     [Certificato da Canale: {best_source.channel} | Confidenza: {result.confidence:.2f}]")
            elif ollama:
                print("  🤖 Chiedo a Ollama...")
                llm_result = ollama.generate(user_input, model=model_name)
                if llm_result.get("success"):
                    print(f"  → {llm_result['response'][:300]}")
                    print(f"     [Canale: ollama (fallback)]")
                else:
                    print(f"  ❌ Errore: {llm_result.get('error', 'sconosciuto')}")
            else:
                print(f"  🧠 {result.answer if result.answer else 'Non so rispondere'}")

            if user_input.startswith(":learn "):
                concept = user_input[7:]
                engine.learn(concept, examples=[], description=concept)
                print(f"  → Imparato: {concept}")
                continue

        except KeyboardInterrupt:
            print("\n  Usa :quit per uscire o :menu per il menu")
        except Exception as e:
            print(f"  ❌ Errore: {e}")


def menu_matematica(engine):
    """Menu matematica."""
    print()
    print("📐 MATEMATICA")
    print("-" * 40)

    tests = [
        ("15 + 27", "quanto fa 15 + 27?"),
        ("Area cerchio r=5", "area cerchio raggio 5"),
        ("Ipotenusa 3,4", "ipotenusa cateti 3 4"),
        ("√144", "radice di 144"),
        ("5!", "5 fattoriale"),
    ]

    for name, query in tests:
        if "quanto" in query:
            r = engine.reason(query)
            print(f"  {name} = {r.answer}")
        else:
            r = engine.math.solve(query)
            print(f"  {name} = {r['answer']}")

    print()
    input("  Premi INVIO per continuare...")


def menu_finanza(engine):
    """Menu finanza."""
    print()
    print("💰 FINANZA")
    print("-" * 40)

    finance = FinanceModule(engine.knowledge, engine.rules)

    r = finance.calculate("compound_interest", principal=1000, rate=0.07, years=10)
    print(f"  Interesse composto: {r.explanation}")

    r = finance.calculate("roi", gain=1200, cost=1000)
    print(f"  ROI: {r.explanation}")

    r = finance.calculate(
        "mortgage_payment", principal=200000, monthly_rate=0.003, months=360
    )
    print(f"  Mutuo: {r.explanation}")

    print()
    input("  Premi INVIO per continuare...")


def menu_test(engine):
    """Esegui test."""
    print()
    print("🧪 TEST SUITE")
    print("-" * 40)

    passed = 0
    total = 0

    # Test matematica
    total += 1
    r = engine.reason("quanto fa 15 + 27?")
    if r.answer == 42.0:
        print("  ✅ Addizione")
        passed += 1
    else:
        print("  ❌ Addizione")

    # Test geometria
    total += 1
    r = engine.math.solve("area cerchio raggio 5")
    if abs(r["answer"] - 78.5398) < 0.01:
        print("  ✅ Geometria")
        passed += 1
    else:
        print("  ❌ Geometria")

    # Test deduzione
    total += 1
    engine.learn("mammifero", examples=[], description="animale", category="biologia")
    engine.learn(
        "animale", examples=[], description="essere vivente", category="biologia"
    )
    engine.learn("gatto", examples=[], description="mammifero", category="biologia")
    engine.knowledge.connect("gatto", "è_un_tipo_di", "mammifero")
    engine.knowledge.connect("mammifero", "è_un_tipo_di", "animale")
    r = engine.deductive.deduce("gatto")
    if r.found:
        print("  ✅ Deduzione")
        passed += 1
    else:
        print("  ❌ Deduzione")

    print()
    print(f"  📊 Risultati: {passed}/{total} test passati")
    print()
    input("  Premi INVIO per continuare...")


def main():
    """Entry point principale."""
    engine = ReasoningEngine()

    # Rileva Ollama
    ollama, models = detect_ollama()

    while True:
        print_header()

        # Stato Ollama
        if ollama:
            print(f"  🤖 Ollama: ✅ ({len(models)} modelli)")
        else:
            print("  🤖 Ollama: ❌ non trovato")

        print()
        print("  ╔════════════════════════════════════════╗")
        print("  ║           MENU PRINCIPALE              ║")
        print("  ╠════════════════════════════════════════╣")
        print("  ║  1. 💬 Chat con AI                    ║")
        print("  ║  2. 📐 Demo Matematica                ║")
        print("  ║  3. 💰 Demo Finanza                   ║")
        print("  ║  4. 🧪 Esegui Test                    ║")
        print("  ║  5. 🤖 Configura Ollama               ║")
        print("  ║  6. 🚀 Esci                           ║")
        print("  ╚════════════════════════════════════════╝")
        print()

        scelta = input("  Scegli (1-6): ").strip()

        if scelta == "1":
            # Seleziona modello se Ollama è disponibile
            model_name = None
            if ollama and models:
                model_name = menu_ollama(ollama, models)

            result = menu_chat(engine, ollama, model_name)
            if result == "quit":
                break

        elif scelta == "2":
            menu_matematica(engine)

        elif scelta == "3":
            menu_finanza(engine)

        elif scelta == "4":
            menu_test(engine)

        elif scelta == "5":
            menu_ollama(ollama, models)
            # Ricarica modelli
            ollama, models = detect_ollama()

        elif scelta == "6" or scelta.lower() == "quit":
            print()
            print("  Arrivederci! 👋")
            break

        else:
            print("  Scelta non valida!")


if __name__ == "__main__":
    main()
