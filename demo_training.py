#!/usr/bin/env python3
"""
Demo TrainingModule — Addestramento dell'engine.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine import ReasoningEngine
from engine.training_module import TrainingModule


def main():
    print("=" * 60)
    print("📚 TRAINING MODULE — Addestramento")
    print("=" * 60)
    print()
    
    engine = ReasoningEngine()
    trainer = TrainingModule(engine)
    
    # === AGGIUNGI ESEMPI DI TRAINING ===
    print("📝 AGGIUNGO ESEMPI DI TRAINING")
    print("-" * 40)
    
    examples = [
        {"input": "quanto fa 2 + 2?", "output": "4", "category": "math"},
        {"input": "quanto fa 3 * 3?", "output": "9", "category": "math"},
        {"input": "area cerchio raggio 1", "output": "3.14", "category": "math"},
        {"input": "ROI 1000 guadagno 1200", "output": "20%", "category": "finance"},
        {"input": "interesse 1000 al 10% per 1 anno", "output": "100", "category": "finance"},
    ]
    
    count = trainer.add_examples_batch(examples)
    print(f"  Aggiunti {count} esempi")
    print()
    
    # === ESEGUI TRAINING ===
    print("🎓 ESEGUO TRAINING")
    print("-" * 40)
    
    result = trainer.train()
    print(f"  Esempi processati: {result.examples_processed}")
    print(f"  Regole create: {result.rules_created}")
    print(f"  Concetti aggiunti: {result.concepts_added}")
    print(f"  Accuracy prima: {result.accuracy_before:.1%}")
    print(f"  Accuracy dopo: {result.accuracy_after:.1%}")
    print(f"  Miglioramento: {result.improvement:.1%}")
    print()
    
    # === VALUTAZIONE ===
    print("📊 VALUTAZIONE")
    print("-" * 40)
    
    eval_result = trainer.evaluate()
    print(f"  Test totali: {eval_result.total_tests}")
    print(f"  Passati: {eval_result.passed}")
    print(f"  Falliti: {eval_result.failed}")
    print(f"  Accuracy: {eval_result.accuracy:.1%}")
    print()
    
    # === FEEDBACK ===
    print("💬 APPRENDIMENTO DA FEEDBACK")
    print("-" * 40)
    
    feedback = trainer.learn_from_feedback(
        input_text="quanto fa 5 + 5?",
        actual_output="9",
        correct=False,
        correct_answer="10"
    )
    print(f"  {feedback['message']}")
    print()
    
    # === ESPORTA ===
    print("💾 ESPORTA DATI")
    print("-" * 40)
    
    export_msg = trainer.export_training_data("training_export.json")
    print(f"  {export_msg}")
    print()
    
    # === STATISTICHE ===
    print("📈 STATISTICHE")
    print("-" * 40)
    
    stats = trainer.get_stats()
    print(f"  Esempi totali: {stats['total_examples']}")
    print(f"  Esempi verificati: {stats['verified_examples']}")
    print(f"  Categorie: {', '.join(stats['categories'])}")
    print(f"  Training eseguiti: {stats['training_runs']}")
    print(f"  Feedback ricevuti: {stats['feedback_count']}")
    print()
    
    # === RIEPILOGO ===
    print("=" * 60)
    print("🎯 TRAINING MODULE:")
    print()
    print("  ✅ Aggiunta esempi (singoli e batch)")
    print("  ✅ Training con epoche multiple")
    print("  ✅ Apprendimento da feedback")
    print("  ✅ Valutazione accuracy")
    print("  ✅ Esporta/importa training data")
    print("  ✅ Statistiche dettagliate")
    print("=" * 60)


if __name__ == "__main__":
    main()
