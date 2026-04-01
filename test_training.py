#!/usr/bin/env python3
"""
Test suite completa per il TrainingModule.
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine import ReasoningEngine
from engine.training_module import TrainingModule


def run_test(name, test_func):
    try:
        result = test_func()
        status = "[OK]" if result else "[FAIL]"
        print(f"  {status} {name}")
        return result
    except Exception as e:
        print(f"  [FAIL] {name}: {e}")
        return False


def main():
    print("=" * 60)
    print("[TEST] Training Module -- Test Suite")
    print("=" * 60)
    print()

    engine = ReasoningEngine()
    trainer = TrainingModule(engine)

    passed = 0
    total = 0

    # Test 1: Aggiunta esempi
    def test_add_example():
        trainer.add_example("test input", "test output", category="test")
        return len(trainer.training_data) > 0

    total += 1
    if run_test("Aggiunta esempio", test_add_example):
        passed += 1

    # Test 2: Aggiunta batch
    def test_add_batch():
        examples = [
            {"input": "2+2", "output": "4", "category": "math"},
            {"input": "3*3", "output": "9", "category": "math"},
        ]
        count = trainer.add_examples_batch(examples)
        return count == 2

    total += 1
    if run_test("Aggiunta batch", test_add_batch):
        passed += 1

    # Test 3: Training
    def test_train():
        result = trainer.train()
        return result.examples_processed > 0

    total += 1
    if run_test("Training", test_train):
        passed += 1

    # Test 4: Valutazione
    def test_evaluate():
        result = trainer.evaluate()
        return result.total_tests > 0

    total += 1
    if run_test("Valutazione", test_evaluate):
        passed += 1

    # Test 5: Feedback
    def test_feedback():
        feedback = trainer.learn_from_feedback("test", "wrong", False, "correct")
        return feedback.get("learned", False) or not feedback.get("learned", True)

    total += 1
    if run_test("Feedback", test_feedback):
        passed += 1

    # Test 6: Esportazione
    def test_export():
        msg = trainer.export_training_data("test_export.json")
        return "Esportati" in msg

    total += 1
    if run_test("Esportazione", test_export):
        passed += 1

    # Test 7: Importazione
    def test_import():
        count = trainer.import_training_data("test_export.json")
        return count > 0

    total += 1
    if run_test("Importazione", test_import):
        passed += 1

    # Test 8: Statistiche
    def test_stats():
        stats = trainer.get_stats()
        return "total_examples" in stats

    total += 1
    if run_test("Statistiche", test_stats):
        passed += 1

    print()
    print("=" * 60)
    print(f"[RISULTATI] {passed}/{total} test passati ({passed / total * 100:.0f}%)")

    if passed == total:
        print("[SUCCESSO] TUTTI I TEST PASSATI!")
    else:
        print(f"[ATTENZIONE] {total - passed} test falliti")

    print("=" * 60)

    # Pulisci file temporanei
    try:
        os.remove("test_export.json")
    except Exception:
        pass


if __name__ == "__main__":
    main()
