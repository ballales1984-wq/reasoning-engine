#!/usr/bin/env python3
"""
Question-Based Reasoner Demo
Domande iteractive per ragionare su un dominio
"""

from engine.question_based import QuestionReasoner, HypothesisSpace
from engine.question_based.question_generator import QuestionGenerator


def main():
    print("\n" + "=" * 50)
    print("QUESTION-BASED REASONER DEMO")
    print("=" * 50 + "\n")

    domain = input("Scegli dominio (animals/colors/sports): ").strip().lower()
    if not domain:
        domain = "animals"

    reasoner = QuestionReasoner(
        domain=domain, max_iterations=10, confidence_threshold=0.85
    )

    if domain == "animals":
        hypotheses = [
            {
                "id": "cane",
                "name": "Cane",
                "probability": 0.2,
                "features": {"habitat": "terra", "domestico": True},
            },
            {
                "id": "gatto",
                "name": "Gatto",
                "probability": 0.2,
                "features": {"habitat": "terra", "domestico": True},
            },
            {
                "id": "pesce",
                "name": "Pesce",
                "probability": 0.2,
                "features": {"habitat": "acqua", "domestico": True},
            },
            {
                "id": "uccello",
                "name": "Uccello",
                "probability": 0.2,
                "features": {"habitat": "aria", "domestico": False},
            },
            {
                "id": "leone",
                "name": "Leone",
                "probability": 0.2,
                "features": {"habitat": "terra", "domestico": False},
            },
        ]
    elif domain == "colors":
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

    reasoner.add_hypotheses(hypotheses)

    def ask(question: str) -> bool:
        print(f"\n? {question}")
        while True:
            risp = input("Rispondi (s/n/?): ").strip().lower()
            if risp in ["s", "si", "y", "yes"]:
                return True
            elif risp in ["n", "no"]:
                return False
            elif risp == "?":
                reasoner.show_top()
                print("(Domanda ignorata)")
                return False

    result = reasoner.run(ask)

    print("\n" + "=" * 50)
    print("RISULTATO")
    print("=" * 50)

    if result.get("result"):
        r = result["result"]
        print(f"\nIpotesi: {r.name}")
        print(f"Confidenza: {r.probability:.2%}")
    else:
        print("\nNessun risultato.")

    print(f"\nIterazioni: {result.get('iterations', 0)}")
    print("\n" + result.get("explanation", ""))

    return result


if __name__ == "__main__":
    main()
