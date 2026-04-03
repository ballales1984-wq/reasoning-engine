#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test automatico per Question-Based Reasoner con debug
"""

import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

sys.path.insert(0, ".")

from engine.question_based import QuestionReasoner
from engine.question_based.probability_updater import ProbabilityUpdater


def test_with_debug():
    print("\n=== TEST CON DEBUG ===\n")

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

    print("Stato iniziale:")
    for h in reasoner.hypothesis_space.all_hypotheses():
        print(f"  {h.name}: {h.probability:.4f} (features: {h.features})")

    # Testiamo direttamente l'updater
    updater = ProbabilityUpdater()
    question = "E' un animale domestico?"
    answer = True

    print(f"\nDomanda: '{question}'")
    print(f"Risposta: {answer}")

    # Estrai feature
    feature, expected = updater._extract_feature_from_question(question)
    print(f"Feature estratta: '{feature}', expected value: {expected}")

    # Mostra i valori delle feature per ogni ipotesi
    print("\nValori delle feature:")
    for h in reasoner.hypothesis_space.all_hypotheses():
        fv = h.features.get(feature, "NOT_FOUND")
        matches = (fv == expected) if fv != "NOT_FOUND" else False
        print(f"  {h.name}: feature '{feature}' = {fv}, matches = {matches}")

    # Applica l'update
    updater.soft_update(reasoner.hypothesis_space, question, answer, strength=0.3)

    print("\nDopo l'update:")
    for h in reasoner.hypothesis_space.all_hypotheses():
        print(f"  {h.name}: {h.probability:.4f}")

    top = reasoner.hypothesis_space.get_top_hypothesis()
    print(f"\nTop: {top.name} ({top.probability:.2%})")


if __name__ == "__main__":
    test_with_debug()
