#!/usr/bin/env python3
"""
Demo del ReasoningEngine.

Esegui: python demo.py
"""

from engine import ReasoningEngine


def main():
    print("=" * 60)
    print("🧠 ReasoningEngine — Demo")
    print("=" * 60)
    print()
    
    # Crea l'engine
    engine = ReasoningEngine()
    
    # --- FASE 1: Insegna concetti ---
    print("📚 FASE 1: Insegno i numeri...")
    print()
    
    engine.learn("6", 
        examples=["🍎🍎🍎🍎🍎🍎", "sei cose", "5+1", "3×2"],
        description="il numero sei, una quantità di 6 elementi",
        category="math/numbers")
    print("  ✅ Ho imparato il numero 6")
    
    engine.learn("9",
        examples=["🍎🍎🍎🍎🍎🍎🍎🍎🍎", "nove cose", "10-1", "3×3"],
        description="il numero nove, una quantità di 9 elementi",
        category="math/numbers")
    print("  ✅ Ho imparato il numero 9")
    
    engine.learn("5",
        examples=["🖐️", "5 cose", "2+3", "10÷2"],
        description="il numero cinque, una quantità di 5 elementi",
        category="math/numbers")
    print("  ✅ Ho imparato il numero 5")
    
    engine.learn("15",
        examples=["una quindicina", "10+5", "3×5"],
        description="il numero quindici",
        category="math/numbers")
    print("  ✅ Ho imparato il numero 15")
    
    print()
    
    # --- FASE 2: Ragiona su problemi ---
    print("🧮 FASE 2: Risolvo problemi...")
    print()
    
    domande = [
        "Quanto fa 6 + 9?",
        "Quanto fa 5 + 5?",
        "Quanto fa 6 - 5?",
        "Quanto fa 3 × 5?",
        "Cosa è 6?",
    ]
    
    for domanda in domande:
        print(f"❓ {domanda}")
        result = engine.reason(domanda)
        
        print(f"   💡 Risposta: {result['answer']}")
        print(f"   📊 Confidenza: {result['confidence']:.0%}")
        print(f"   ✅ Verificato: {'Sì' if result['verified'] else 'No'}")
        print()
    
    # --- FASE 3: Mostra cosa sa ---
    print("📖 FASE 3: Cosa ho imparato?")
    print()
    
    knowledge = engine.what_do_you_know()
    print(f"  Concetti: {knowledge['stats']['total_concepts']}")
    print(f"  Regole: {knowledge['stats']['total_rules']}")
    print()
    
    print("  Concetti memorizzati:")
    for concept in knowledge['concepts']:
        print(f"    • {concept['name']}: {concept['description']}")
    print()
    
    print("  Regole disponibili:")
    for rule in knowledge['rules']:
        print(f"    • {rule['name']}: {rule['description']}")
    print()
    
    # --- FASE 4: Spiegazione dettagliata ---
    print("🔍 FASE 4: Spiegazione dettagliata")
    print()
    
    result = engine.reason("Quanto fa 6 + 9?")
    print(result['explanation'])
    print()
    
    print("=" * 60)
    print("🎉 Demo completata!")
    print("=" * 60)


if __name__ == "__main__":
    main()
