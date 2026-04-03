#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test rapido del Question-Based Reasoner
Esegue un caso completo in automatico
"""

import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

sys.path.insert(0, ".")

from engine.question_based import QuestionReasoner


def run_test():
    print("=" * 60)
    print("  QUESTION-BASED REASONER - TEST INTERATTIVO")
    print("=" * 60)
    print()
    print("Scenario: Indovina l'animale!")
    print("Ipotesi: Cane, Gatto, Volpe")
    print()

    reasoner = QuestionReasoner(
        domain="animals", max_iterations=10, confidence_threshold=0.80
    )

    # Aggiungi ipotesi con feature
    hypotheses = [
        {
            "id": "cane",
            "name": "Cane",
            "probability": 0.33,
            "features": {"domestico": True, "coda_lunga": False, "verso": "abbaia"},
        },
        {
            "id": "gatto",
            "name": "Gatto",
            "probability": 0.33,
            "features": {"domestico": True, "coda_lunga": True, "verso": "miao"},
        },
        {
            "id": "volpe",
            "name": "Volpe",
            "probability": 0.34,
            "features": {"domestico": False, "coda_lunga": True, "verso": "guaisce"},
        },
    ]

    reasoner.add_hypotheses(hypotheses)

    # Simuliamo un utente che risponde
    # L'utente sta pensando a un Gatto (domestico, coda lunga)

    def ask(question):
        print(f"  ? {question}")

        # Risposte simulate per "Gatto"
        if "domestico" in question.lower():
            answer = True
            print(f"    → Si")
        elif "coda" in question.lower():
            answer = True
            print(f"    → Si")
        elif "verso" in question.lower():
            answer = False  # "abbaia" != "miao"
            print(f"    → No")
        else:
            answer = False
            print(f"    → No")

        return answer

    print("Inizio ragionamento...")
    print()

    result = reasoner.run(ask)

    print()
    print("=" * 60)
    print("  RISULTATO")
    print("=" * 60)

    if result.get("result"):
        r = result["result"]
        print(f"  Animale identificato: {r.name}")
        print(f"  Confidenza: {r.probability:.1%}")
    else:
        print("  Nessuna conclusione")

    print(f"\n  Iterazioni: {result.get('iterations', 0)}")
    print(f"  Domande fatte: {len(result.get('trace', []))}")

    print()
    print("=" * 60)
    print("  RAGIONAMENTO PASSO PASSO")
    print("=" * 60)

    for i, step in enumerate(result.get("trace", []), 1):
        q = step.get("question", "?")
        a = "Si" if step.get("answer") else "No"
        top = step.get("top_hypothesis", "?")
        conf = step.get("confidence", 0)
        print(f"\n  Step {i}:")
        print(f"    Domanda: {q}")
        print(f"    Risposta: {a}")
        print(f"    Top: {top} ({conf:.1%})")

    print()
    print("=" * 60)

    # Verifica
    if result.get("result"):
        correct = result["result"].name == "Gatto"
        print(
            f"  {'[OK] RISPOSTA CORRETTA!' if correct else '[ERR] RISPOSTA SBAGLIATA'}"
        )
    else:
        print("  [ERR] NESSUNA RISPOSTA")

    print("=" * 60)

    return result.get("result", {}).get("name") == "Gatto"


if __name__ == "__main__":
    success = run_test()
    sys.exit(0)
