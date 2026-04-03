#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Question-Based Reasoner - Versione pronta all'uso
Esegue un dialogo interattivo per indovinare un concetto
"""

import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

sys.path.insert(0, ".")

from engine.question_based import QuestionReasoner


def main():
    print()
    print("=" * 60)
    print("  QUESTION-BASED REASONER")
    print("  Indovina il tuo pensiero con domande intelligenti!")
    print("=" * 60)
    print()

    # Scegli dominio
    print("Scegli un dominio:")
    print("  1. Animali (cane, gatto, volpe, leone...)")
    print("  2. Colori (rosso, blu, verde...)")
    print("  3. Sport (calcio, tennis, nuoto...)")
    print()

    scelta = input("Scegli (1/2/3): ").strip()

    if scelta == "1":
        domain = "animals"
        hypotheses = [
            {
                "id": "cane",
                "name": "Cane",
                "probability": 0.2,
                "features": {"domestico": True, "coda_lunga": False},
            },
            {
                "id": "gatto",
                "name": "Gatto",
                "probability": 0.2,
                "features": {"domestico": True, "coda_lunga": True},
            },
            {
                "id": "volpe",
                "name": "Volpe",
                "probability": 0.2,
                "features": {"domestico": False, "coda_lunga": True},
            },
            {
                "id": "leone",
                "name": "Leone",
                "probability": 0.2,
                "features": {"domestico": False, "coda_lunga": False},
            },
            {
                "id": "pesce",
                "name": "Pesce",
                "probability": 0.2,
                "features": {"domestico": True, "vive_in_acqua": True},
            },
        ]
    elif scelta == "2":
        domain = "colors"
        hypotheses = [
            {
                "id": "rosso",
                "name": "Rosso",
                "probability": 0.25,
                "features": {"primario": True, "caldo": True},
            },
            {
                "id": "blu",
                "name": "Blu",
                "probability": 0.25,
                "features": {"primario": True, "caldo": False},
            },
            {
                "id": "verde",
                "name": "Verde",
                "probability": 0.25,
                "features": {"primario": False, "caldo": False},
            },
            {
                "id": "giallo",
                "name": "Giallo",
                "probability": 0.25,
                "features": {"primario": True, "caldo": True},
            },
        ]
    else:
        domain = "sports"
        hypotheses = [
            {
                "id": "calcio",
                "name": "Calcio",
                "probability": 0.25,
                "features": {"team": True, "palla": True},
            },
            {
                "id": "tennis",
                "name": "Tennis",
                "probability": 0.25,
                "features": {"team": False, "palla": True},
            },
            {
                "id": "nuoto",
                "name": "Nuoto",
                "probability": 0.25,
                "features": {"team": False, "palla": False},
            },
            {
                "id": "basket",
                "name": "Basket",
                "probability": 0.25,
                "features": {"team": True, "palla": True},
            },
        ]

    # Crea il reasoner
    reasoner = QuestionReasoner(
        domain=domain, max_iterations=10, confidence_threshold=0.80
    )

    reasoner.add_hypotheses(hypotheses)

    print()
    print("Pensa a un elemento del dominio e rispondi alle domande!")
    print("Rispondi con: s = si, n = no")
    print()

    def ask(question):
        print(f"  ? {question}")
        while True:
            risp = input("    Risposta (s/n): ").strip().lower()
            if risp == "s":
                return True
            elif risp == "n":
                return False
            print("    Rispondi s o n!")

    # Esegui il ragionamento
    result = reasoner.run(ask)

    # Mostra risultato
    print()
    print("=" * 60)
    print("  RISULTATO")
    print("=" * 60)

    if result.get("result"):
        r = result["result"]
        print(f"  L'elemento che hai pensato e': {r.name}")
        print(f"  Confidenza: {r.probability:.0%}")
    else:
        print("  Non sono riuscito a individuarlo.")

    print(f"\n  Domande fatte: {len(result.get('trace', []))}")

    print()
    print("=" * 60)
    print("  RAGIONAMENTO")
    print("=" * 60)

    for i, step in enumerate(result.get("trace", []), 1):
        q = step.get("question", "?")
        a = "Si" if step.get("answer") else "No"
        top = step.get("top_hypothesis", "?")
        print(f"  {i}. {q}")
        print(f"     -> {a} | Top: {top}")

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
