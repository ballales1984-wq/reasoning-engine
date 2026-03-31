"""
Demo Fase 3 — Deduttivo, Induttivo, Analogico.
"""

from engine import ReasoningEngine


def main():
    print("=" * 60)
    print("🧠 ReasoningEngine — Fase 3: Ragionamento Avanzato")
    print("=" * 60)

    engine = ReasoningEngine()

    # ============================================================
    # SETUP: Insegna una gerarchia di concetti
    # ============================================================
    print("\n📚 SETUP: Insegno concetti e relazioni...")

    # Gerarchia biologica
    engine.knowledge.add("animale", description="essere vivente senziente", category="biologia")
    engine.knowledge.add("mammifero", description="animale che allatta i cuccioli", category="biologia")
    engine.knowledge.add("felino", description="mammifero predatore", category="biologia")
    engine.knowledge.add("gatto", description="felino domestico", category="biologia")
    engine.knowledge.add("cane", description="mammifero domestico, fedele", category="biologia")
    engine.knowledge.add("uccello", description="animale con piume e ali", category="biologia")
    engine.knowledge.add("aquila", description="uccello rapace", category="biologia")

    # Gerarchia
    engine.knowledge.connect("mammifero", "è_un_tipo_di", "animale")
    engine.knowledge.connect("felino", "è_un_tipo_di", "mammifero")
    engine.knowledge.connect("gatto", "è_un_tipo_di", "felino")
    engine.knowledge.connect("cane", "è_un_tipo_di", "mammifero")
    engine.knowledge.connect("uccello", "è_un_tipo_di", "animale")
    engine.knowledge.connect("aquila", "è_un_tipo_di", "uccello")

    # Proprietà
    engine.knowledge.connect("animale", "ha_caratteristica", "si_muove")
    engine.knowledge.connect("animale", "ha_caratteristica", "respira")
    engine.knowledge.connect("mammifero", "ha_caratteristica", "allatta")
    engine.knowledge.connect("mammifero", "ha_caratteristica", "ha_pelo")
    engine.knowledge.connect("uccello", "ha_caratteristica", "ha_piume")
    engine.knowledge.connect("uccello", "ha_caratteristica", "vola")
    engine.knowledge.connect("gatto", "ha_caratteristica", "fa_le_fusa")
    engine.knowledge.connect("cane", "ha_caratteristica", "abbaia")

    # Sistemi per analogie
    engine.knowledge.add("sistema_solare", description="sole + pianeti in orbita", category="astronomia")
    engine.knowledge.add("atomo", description="nucleo + elettroni", category="fisica")
    engine.knowledge.add("cuore", description="muscolo pompa sangue", category="biologia")
    engine.knowledge.add("pompa", description="dispositivo che spinge fluidi", category="meccanica")
    engine.knowledge.add("cervello", description="organo che elabora segnali", category="biologia")
    engine.knowledge.add("computer", description="macchina che elabora dati", category="tecnologia")

    engine.knowledge.connect("sistema_solare", "ha_parte", "sole")
    engine.knowledge.connect("sistema_solare", "ha_parte", "pianeti")
    engine.knowledge.connect("atomo", "ha_parte", "nucleo")
    engine.knowledge.connect("atomo", "ha_parte", "elettroni")
    engine.knowledge.connect("cuore", "ha_funzione", "pompa")
    engine.knowledge.connect("pompa", "ha_funzione", "spinge")
    engine.knowledge.connect("cervello", "ha_funzione", "elabora")
    engine.knowledge.connect("computer", "ha_funzione", "elabora")

    print("   ✅ 13 concetti, relazioni e proprietà configurati")

    # ============================================================
    # TEST 1: DEDUZIONE
    # ============================================================
    print("\n" + "=" * 60)
    print("🔍 TEST 1: Ragionamento Deduttivo")
    print("=" * 60)

    deduction_tests = [
        ("gatto", "animale", "Il gatto è un animale? (catena: gatto→felino→mammifero→animale)"),
        ("gatto", "si_muove", "Il gatto si muove? (proprietà ereditata da animale)"),
        ("gatto", "allatta", "Il gatto allatta? (proprietà ereditata da mammifero)"),
        ("aquila", "vola", "L'aquila vola? (proprietà ereditata da uccello)"),
        ("cane", "ha_pelo", "Il cane ha pelo? (proprietà ereditata da mammifero)"),
    ]

    for subject, target, description in deduction_tests:
        print(f"\n❓ {description}")
        result = engine.deductive.deduce(subject, target)
        if result.found:
            print(f"   ✅ Sì! ({result.steps_count} passi, confidenza: {result.confidence:.0%})")
            for step in result.chain:
                print(f"      → {step.rule_type}: {step.premise1}")
        else:
            print(f"   ❌ Non riesco a dedurlo")

    # ============================================================
    # TEST 2: INDUZIONE
    # ============================================================
    print("\n" + "=" * 60)
    print("📊 TEST 2: Ragionamento Induttivo")
    print("=" * 60)

    examples = [
        "il cane ha 4 zampe",
        "il gatto ha 4 zampe",
        "il cavallo ha 4 zampe",
        "la mucca ha 4 zampe",
    ]

    print(f"\n📝 Esempi:")
    for ex in examples:
        print(f"   • {ex}")

    result = engine.inductive.induce_from_examples(examples)
    print(f"\n{result.explanation}")

    # Induzione dalla conoscenza esistente
    print("\n📊 Induzione dalla conoscenza esistente:")
    kg_result = engine.inductive.induce_from_knowledge()
    print(f"   {kg_result.explanation}")
    if kg_result.patterns:
        for p in kg_result.patterns[:5]:
            print(f"   • {p.description} ({p.confidence:.0%})")

    # ============================================================
    # TEST 3: ANALOGIA
    # ============================================================
    print("\n" + "=" * 60)
    print("🔄 TEST 3: Ragionamento Analogico")
    print("=" * 60)

    analogy_tests = [
        ("sistema_solare", "atomo", "Sistema solare ↔ Atomo"),
        ("cuore", "pompa", "Cuore ↔ Pompa"),
        ("cervello", "computer", "Cervello ↔ Computer"),
    ]

    for source, target, description in analogy_tests:
        print(f"\n🔗 {description}")
        explanation = engine.explain_analogy(source, target)
        print(f"   {explanation}")

    # Trova analogie automaticamente
    print("\n🔍 Analogie automatiche per 'gatto':")
    result = engine.find_analogies("gatto")
    print(f"   {result.explanation}")

    # ============================================================
    # TEST 4: INTEGRAZIONE ENGINE
    # ============================================================
    print("\n" + "=" * 60)
    print("⚙️ TEST 4: Engine Integrato")
    print("=" * 60)

    integrated_tests = [
        "il gatto è un animale?",
        "il cane ha pelo?",
    ]

    for question in integrated_tests:
        result = engine.reason(question)
        print(f"\n❓ {question}")
        print(f"   💡 Risposta: {result['answer']}")
        print(f"   📊 Confidenza: {result['confidence']:.0%}")
        print(f"   ✅ Verificato: {'Sì' if result['verified'] else 'No'}")
        if result['steps']:
            for step in result['steps']:
                print(f"   {step}")

    print("\n" + "=" * 60)
    print("🎉 Fase 3 completata!")
    print("=" * 60)


if __name__ == "__main__":
    main()
