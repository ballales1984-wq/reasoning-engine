#!/usr/bin/env python3
"""
Demo del ReasoningEngine — Matematica completa.

Esegui: python demo_math.py
"""

from engine import ReasoningEngine


def main():
    print("=" * 60)
    print("🧠 ReasoningEngine — Demo Matematica")
    print("=" * 60)
    print()
    
    engine = ReasoningEngine()
    
    # --- TEST MATEMATICA AVANZATA ---
    tests = [
        # Operazioni base
        ("Quanto fa 12 + 8?", "addizione"),
        ("Quanto fa 100 - 37?", "sottrazione"),
        ("Quanto fa 12 × 12?", "moltiplicazione"),
        ("Quanto fa 144 ÷ 12?", "divisione"),
        
        # Potenze
        ("2 alla seconda", "potenza al quadrato"),
        ("2 alla terza", "potenza al cubo"),
        ("5 elevato a 3", "potenza generica"),
        
        # Radici
        ("radice di 144", "radice quadrata"),
        ("√81", "radice quadrata"),
        
        # Percentuali
        ("il 20% di 150", "percentuale"),
        ("il 50% di 200", "percentuale"),
        
        # Fattoriale
        ("5 fattoriale", "fattoriale"),
        ("10!", "fattoriale"),
        
        # Geometria
        ("area cerchio raggio 5", "geometria"),
        ("area rettangolo 10 5", "geometria"),
        ("area triangolo base 8 altezza 6", "geometria"),
        ("circonferenza raggio 3", "geometria"),
        ("ipotenusa cateti 3 4", "pitagora"),
        ("volume cubo lato 4", "geometria"),
        ("volume sfera raggio 3", "geometria"),
        
        # Equazioni
        ("x + 5 = 12", "equazione"),
        ("2x = 20", "equazione"),
    ]
    
    print("🧮 TEST MATEMATICA\n")
    
    passed = 0
    failed = 0
    
    for expression, category in tests:
        result = engine.math.solve(expression)
        
        if result["answer"] is not None:
            status = "✅"
            passed += 1
        else:
            status = "❌"
            failed += 1
        
        print(f"{status} {expression}")
        print(f"   → {result['explanation']}")
        print()
    
    print("=" * 60)
    print(f"📊 Risultati: {passed} passati, {failed} falliti")
    print("=" * 60)
    
    # --- CONCETTI MATEMATICI ---
    print()
    print("📚 Concetti matematici registrati:")
    print()
    
    knowledge = engine.what_do_you_know()
    math_concepts = [c for c in knowledge['concepts'] if 'math' in c.get('category', '')]
    
    for concept in math_concepts:
        print(f"  • {concept['name']}: {concept['description'][:60]}...")
    
    print()
    print("=" * 60)
    print("🎉 Demo completata!")
    print("=" * 60)


if __name__ == "__main__":
    main()
