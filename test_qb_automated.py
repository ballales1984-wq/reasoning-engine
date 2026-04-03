#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test automatico per Question-Based Reasoner
"""

import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

sys.path.insert(0, ".")

from engine.question_based import QuestionReasoner
from engine.question_based.hypothesis_space import Hypothesis


def test_animals():
    print("\n=== TEST: Animals Domain ===\n")

    reasoner = QuestionReasoner(
        domain="animals", max_iterations=5, confidence_threshold=0.85
    )

    # Ipotesi: cane, gatto, volpe
    hypotheses = [
        {
            "id": "cane",
            "name": "Cane",
            "probability": 0.33,
            "features": {"domestico": True, "coda_lunga": False},
        },
        {
            "id": "gatto",
            "name": "Gatto",
            "probability": 0.33,
            "features": {"domestico": True, "coda_lunga": True},
        },
        {
            "id": "volpe",
            "name": "Volpe",
            "probability": 0.34,
            "features": {"domestico": False, "coda_lunga": True},
        },
    ]

    reasoner.add_hypotheses(hypotheses)

    print(f"Ipotesi iniziali: {len(reasoner.hypothesis_space.hypotheses)}")
    for h in reasoner.hypothesis_space.all_hypotheses():
        print(f"  - {h.name}: {h.probability:.2%}")

    # Simuliamo risposte
    # Domanda 1: "E' un animale domestico?" -> risposta: True
    question = reasoner.generate_next_question()
    print(f"\n1. Domanda: {question}")
    reasoner.step(question, True)  # Si, e' domestico

    top = reasoner.hypothesis_space.get_top_hypothesis()
    print(
        f"   Top ipotesi: {top.name if top else 'Nessuna'} ({top.probability if top else 0:.2%})"
    )

    # Domanda 2: "Ha la coda lunga?" -> risposta: True
    question = reasoner.generate_next_question()
    print(f"\n2. Domanda: {question}")
    reasoner.step(question, True)  # Si, ha la coda lunga

    top = reasoner.hypothesis_space.get_top_hypothesis()
    print(
        f"   Top ipotesi: {top.name if top else 'Nessuna'} ({top.probability if top else 0:.2%})"
    )

    # Risultato finale
    result = reasoner.hypothesis_space.get_top_hypothesis()
    print(f"\n=== RISULTATO ===")
    print(f"Ipotesi: {result.name if result else 'Nessuna'}")
    print(f"Confidenza: {result.probability if result else 0:.2%}")
    print(f"\nTrace:")
    for i, step in enumerate(reasoner.trace, 1):
        print(
            f"  {i}. {step.get('question', '?')} -> {'Si' if step.get('answer') else 'No'}"
        )
        print(
            f"     Top: {step.get('top_hypothesis', '?')} ({step.get('confidence', 0):.2%})"
        )

    # Il risultato dovrebbe essere Gatto (domestico + coda_lunga)
    return result and result.name == "Gatto"


def test_colors():
    print("\n=== TEST: Colors Domain ===\n")

    reasoner = QuestionReasoner(
        domain="colors", max_iterations=3, confidence_threshold=0.90
    )

    hypotheses = [
        {
            "id": "rosso",
            "name": "Rosso",
            "probability": 0.33,
            "features": {"primario": True, "caldo": True},
        },
        {
            "id": "blu",
            "name": "Blu",
            "probability": 0.33,
            "features": {"primario": True, "caldo": False},
        },
        {
            "id": "verde",
            "name": "Verde",
            "probability": 0.34,
            "features": {"primario": False, "caldo": False},
        },
    ]

    reasoner.add_hypotheses(hypotheses)

    for h in reasoner.hypothesis_space.all_hypotheses():
        print(f"  - {h.name}: {h.probability:.2%}")

    # Test: "E' un colore primario?" -> si -> rosso o blu
    question = reasoner.generate_next_question()
    print(f"\nDomanda: {question}")

    reasoner.step(question, True)  # E' primario -> si

    top = reasoner.hypothesis_space.get_top_hypothesis()
    print(f"Top: {top.name} ({top.probability:.2%})")

    # Test: "E' un colore caldo?" -> si -> rosso
    question = reasoner.generate_next_question()
    print(f"Domanda: {question}")

    reasoner.step(question, True)  # Caldo -> si

    top = reasoner.hypothesis_space.get_top_hypothesis()
    print(f"Top: {top.name} ({top.probability:.2%})")

    return top and top.name == "Rosso"


def main():
    print("=" * 50)
    print("QUESTION-BASED REASONER - TEST AUTOMATICO")
    print("=" * 50)

    test1 = test_animals()
    test2 = test_colors()

    print("\n" + "=" * 50)
    print("RISULTATI")
    print("=" * 50)
    print(f"Animals test: {'OK' if test1 else 'FAILED'}")
    print(f"Colors test:  {'OK' if test2 else 'FAILED'}")
    print("=" * 50)

    return test1 and test2


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
