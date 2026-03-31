#!/usr/bin/env python3
"""
Demo del SelfLearningEngine — Impara da solo, come un umano.

Esegui: python demo_self_learning.py
"""

from engine import ReasoningEngine
from engine.self_learning import SelfLearningEngine


def main():
    print("=" * 60)
    print("🧠 SelfLearningEngine — Impara da solo")
    print("=" * 60)
    print()
    
    engine = ReasoningEngine()
    learner = SelfLearningEngine(engine.knowledge, engine.rules)
    
    # === FASE 1: OSSERVA ===
    print("👁️ FASE 1: OSSERVA")
    print("-" * 40)
    print("L'engine osserva degli esempi e FORMULA IPOTESI")
    print("(non gli dico la regola — la trova da solo)")
    print()
    
    examples = [
        "2 + 3 = 5",
        "3 + 2 = 5",
        "4 + 1 = 5",
        "1 + 4 = 5",
    ]
    
    print("Esempi osservati:")
    for ex in examples:
        print(f"  • {ex}")
    print()
    
    hypotheses = learner.observe(examples)
    
    print(f"Ipotesi formulate: {len(hypotheses)}")
    for h in hypotheses:
        print(f"  💡 {h.id}: {h.description}")
        print(f"     Confidenza: {h.confidence:.0%}")
    print()
    
    # === FASE 2: TESTA ===
    print("🧪 FASE 2: TESTA LE IPOTESI")
    print("-" * 40)
    print("L'engine TESTA le ipotesi su nuovi casi")
    print("(trial and error)")
    print()
    
    test_cases = [
        "5 + 0 = 5",
        "0 + 5 = 5",
        "6 - 1 = 5",
    ]
    
    for test in test_cases:
        print(f"Test: {test}")
        for h in hypotheses:
            result = learner.test_hypothesis(h.id, test)
            status = "✅" if result["success"] else "❌"
            print(f"  {status} {h.id}: confidenza {result['confidence']:.0%}")
        print()
    
    # === FASE 3: IMPARA ===
    print("📚 FASE 3: COSA HA IMPARATO?")
    print("-" * 40)
    
    summary = learner.get_learning_summary()
    print(f"  Ipotesi formulate: {summary['hypotheses_formulated']}")
    print(f"  Esperienze: {summary['experiences']}")
    print(f"  Regole create da solo: {summary['rules_self_created']}")
    print()
    
    if summary['top_hypotheses']:
        print("  Top ipotesi:")
        for h in summary['top_hypotheses']:
            print(f"    • {h.description} ({h.confidence:.0%})")
    print()
    
    if summary['lessons_learned']:
        print("  Ultime lezioni:")
        for lesson in summary['lessons_learned']:
            print(f"    • {lesson}")
    print()
    
    # === FASE 4: CURIOSITÀ ===
    print("🔍 FASE 4: CURIOSITÀ")
    print("-" * 40)
    print("L'engine ESPLORA cose che non conosce")
    print()
    
    result = learner.esplora("fotoni")
    print(f"  Argomento: {result['topic']}")
    print(f"  Ipotesi generate: {result['hypotheses_generated']}")
    print(f"  Status: {result['status']}")
    print(f"  Prossimo passo: {result['next_step']}")
    print()
    
    # === RIEPILOGO ===
    print("=" * 60)
    print("🎯 COSA SA FARE ORA L'ENGINE:")
    print()
    print("  ✅ Osserva esempi → formula ipotesi")
    print("  ✅ Testa ipotesi → trial and error")
    print("  ✅ Impara dagli errori → corregge")
    print("  ✅ Conferma le regole → le promuove")
    print("  ✅ Esplora l'ignoto → curiosità")
    print("  ✅ Ricorda le esperienze → memoria")
    print()
    print("  🧠 Questo è come impara un umano!")
    print("=" * 60)
    print()
    print("🎉 Demo completata!")


if __name__ == "__main__":
    main()
