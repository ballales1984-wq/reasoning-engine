"""
Demo NLP Parser — Testa il parser con frasi italiane.
"""

from engine.nlp_parser import parse


def main():
    print("=" * 60)
    print("🧠 NLP Parser — Demo")
    print("=" * 60)

    test_cases = [
        # Calcoli
        "quanto fa 15 + 27?",
        "calcola il 20% di 150",
        "5 fattoriale",
        "radice di 144",
        "area cerchio raggio 5",
        "ipotenusa cateti 3 4",
        "quanto fa 12 × 12?",

        # Definizioni
        "cos'è un atomo?",
        "cosa è la fotosintesi?",
        "definisci gravità",

        # Apprendimento
        "il gatto è un mammifero",
        "la Roma è la capitale d'Italia",

        # Verifica
        "è vero che 2 + 2 = 4?",

        # Confronto
        "qual è più grande, 5 o 7?",

        # Spiegazione
        "perché il cielo è blu?",
    ]

    for text in test_cases:
        result = parse(text)
        print(f"\n📝 \"{text}\"")
        print(f"   Intent: {result.intent} (confidenza: {result.confidence:.0%})")
        print(f"   Operation: {result.operation}")
        print(f"   Numeri: {result.numbers}")
        print(f"   Operatori: {result.operators}")
        if result.entities:
            ent_names = [e.name for e in result.entities if e.entity_type == "concept"]
            if ent_names:
                print(f"   Concetti: {ent_names}")
        if result.relations:
            print(f"   Relazioni: {result.relations}")

    # Ora testiamo con l'engine completo
    print("\n" + "=" * 60)
    print("🧠 ReasoningEngine + NLP Parser — Test integrato")
    print("=" * 60)

    from engine import ReasoningEngine
    engine = ReasoningEngine()

    # Insegna qualcosa
    engine.learn("6", examples=["🍎🍎🍎🍎🍎🍎", "sei cose", "5+1"],
                 description="il numero sei", category="math/numbers")
    engine.learn("9", examples=["nove cose", "3×3"],
                 description="il numero nove", category="math/numbers")

    test_questions = [
        "quanto fa 6 + 9?",
        "quanto fa 15 più 27?",
        "il 20% di 150",
        "radice di 144",
        "cosa è 6?",
        "area cerchio raggio 5",
        "quanto fa 5 fattoriale?",
    ]

    for question in test_questions:
        result = engine.reason(question)
        print(f"\n❓ {question}")
        print(f"   💡 Risposta: {result['answer']}")
        print(f"   📊 Confidenza: {result['confidence']:.0%}")
        print(f"   ✅ Verificato: {'Sì' if result['verified'] else 'No'}")
        if result['steps']:
            print(f"   📋 Passi: {len(result['steps'])}")

    print("\n" + "=" * 60)
    print("🎉 Demo completata!")
    print("=" * 60)


if __name__ == "__main__":
    main()
