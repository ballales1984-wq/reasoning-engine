"""
Test suite per Question-Based Reasoner
Test automatici, ripetibili, offline (no LLM required)
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.question_based import (
    HypothesisSpace,
    QuestionGenerator,
    InformationGain,
    ProbabilityUpdater,
    Explainer,
    QuestionReasoner,
)


def test_reasoner_basic_cycle():
    """Test 1: Ciclo di ragionamento completo"""
    print("=== TEST 1: Ciclo di ragionamento completo ===")

    hypotheses = {
        "cane": {"domestico": True, "coda_lunga": False, "rosso": False},
        "gatto": {"domestico": True, "coda_lunga": True, "rosso": False},
        "volpe": {"domestico": False, "coda_lunga": True, "rosso": True},
    }

    space = HypothesisSpace(hypotheses)
    generator = QuestionGenerator(space)
    selector = InformationGain(space)
    updater = ProbabilityUpdater(space)
    explainer = Explainer()

    answers = {"domestico": True, "coda_lunga": True, "rosso": False}

    def callback(q):
        return answers.get(q, True)

    reasoner = QuestionReasoner(space=space)
    result = reasoner.run(callback)

    print(f"  Ipotesi finali: {result.get('final_hypothesis')}")
    print(f"  Probabilita: {result.get('final_probabilities')}")
    print(f"  Status: {result.get('status')}")
    print(f"  Trace: {len(result.get('trace', []))} domande")

    assert len(result.get("final_hypothesis", [])) >= 1, (
        "Errore: nessuna ipotesi finale"
    )
    assert len(result.get("trace", [])) > 0, "Errore: nessun log generato"
    total_prob = sum(result.get("final_probabilities", {}).values())
    assert abs(total_prob - 1) < 1e-6 or total_prob == 0, (
        "Errore: probabilita non normalizzate"
    )

    print("  [PASS]\n")
    return True


def test_reasoner_stress_incoherent():
    """Test 2: Stress test con risposte incoerenti"""
    print("=== TEST 2: Stress test con risposte incoerenti ===")

    hypotheses = {
        "cane": {"domestico": True, "coda_lunga": False},
        "gatto": {"domestico": True, "coda_lunga": True},
        "volpe": {"domestico": False, "coda_lunga": True},
        "lupo": {"domestico": False, "coda_lunga": True},
    }

    space = HypothesisSpace(hypotheses)
    reasoner = QuestionReasoner(space=space)

    answers = {"domestico": True, "coda_lunga": False}

    def callback(q):
        return answers.get(q, True)

    result = reasoner.run(callback)

    print(f"  Ipotesi finali: {result.get('final_hypothesis')}")
    print(f"  Probabilita: {result.get('final_probabilities')}")
    print(f"  Status: {result.get('status')}")

    assert len(result.get("final_hypothesis", [])) >= 1, (
        "Errore: il sistema non converge"
    )
    total_prob = sum(result.get("final_probabilities", {}).values())
    assert abs(total_prob - 1) < 1e-6 or total_prob == 0, (
        "Errore: probabilita non normalizzate"
    )

    print("  [PASS]\n")
    return True


def test_probability_consistency():
    """Test 3: Verifica coerenza probabilistica"""
    print("=== TEST 3: Coerenza probabilistica ===")

    hypotheses = {
        "cane": {"domestico": True},
        "gatto": {"domestico": True},
        "volpe": {"domestico": False},
    }

    space = HypothesisSpace(hypotheses)
    reasoner = QuestionReasoner(space=space)

    def callback(q):
        return True

    result = reasoner.run(callback)

    probs = result.get("final_probabilities", {})
    total = sum(probs.values())

    print(f"  Probabilita: {probs}")
    print(f"  Totale: {total}")

    assert abs(total - 1) < 1e-6 or total == 0, (
        f"Errore: probabilita non sommano a 1 (totale={total})"
    )
    assert all(p >= 0 for p in probs.values()), "Errore: probabilita negative"

    print("  [PASS]\n")
    return True


def test_explainability():
    """Test 4: Verifica spiegabilita (audit trail)"""
    print("=== TEST 4: Spiegabilita (audit trail) ===")

    hypotheses = {
        "cane": {"domestico": True},
        "volpe": {"domestico": False},
    }

    space = HypothesisSpace(hypotheses)
    reasoner = QuestionReasoner(space=space)

    def callback(q):
        return True

    result = reasoner.run(callback)

    trace = result.get("trace", [])

    print(f"  Trace entries: {len(trace)}")

    assert len(trace) > 0, "Errore: nessun audit trail generato"
    if len(trace) > 0:
        assert "question" in trace[0], "Errore: log incompleto (question)"
        assert "answer" in trace[0], "Errore: log incompleto (answer)"

    print("  [PASS]\n")
    return True


def test_information_gain_selection():
    """Test 5: Verifica che Information Gain selezioni la domanda migliore"""
    print("=== TEST 5: Information Gain ===")

    hypotheses = {
        "cane": {"domestico": True, "coda_lunga": False, "rosso": False},
        "gatto": {"domestico": True, "coda_lunga": True, "rosso": False},
        "volpe": {"domestico": False, "coda_lunga": True, "rosso": True},
    }

    space = HypothesisSpace(hypotheses)
    generator = QuestionGenerator(space)
    selector = InformationGain(space)

    questions = generator.generate()
    print(f"  Domande disponibili: {questions}")

    best = selector.best_question(questions)
    print(f"  Domanda selezionata: {best}")

    assert best is not None, "Errore: nessuna domanda selezionata"
    assert best in questions, "Errore: domanda non in lista"

    print("  [PASS]\n")
    return True


def test_question_generator():
    """Test 6: Verifica generazione domande utili"""
    print("=== TEST 6: Generatore domande ===")

    hypotheses = {
        "cane": {"domestico": True, "coda_lunga": False},
        "gatto": {"domestico": True, "coda_lunga": True},
        "volpe": {"domestico": False, "coda_lunga": True},
    }

    space = HypothesisSpace(hypotheses)
    generator = QuestionGenerator(space)

    questions = generator.generate()

    print(f"  Domande generate: {questions}")

    assert len(questions) > 0, "Errore: nessuna domanda generata"
    assert "domestico" in questions or "coda_lunga" in questions, (
        "Errore: domande non utili"
    )

    print("  [PASS]\n")
    return True


def test_hypothesis_filter():
    """Test 7: Verifica eliminazione ipotesi"""
    print("=== TEST 7: Eliminazione ipotesi ===")

    hypotheses = {
        "cane": {"domestico": True},
        "gatto": {"domestico": True},
        "volpe": {"domestico": False},
    }

    space = HypothesisSpace(hypotheses)
    print(f"  Iniziali: {space.remaining()}")

    space.filter("domestico", True)
    print(f"  Dopo filtro (domestico=True): {space.remaining()}")

    assert "volpe" not in space.remaining(), "Errore: volpe non eliminata"
    assert len(space.remaining()) == 2, "Errore: numero ipotesi errato"

    print("  [PASS]\n")
    return True


def test_uncertain_answer():
    """Test 8: Gestione risposta incerta (unknown)"""
    print("=== TEST 8: Risposta incerta ===")

    hypotheses = {
        "cane": {"domestico": True, "coda_lunga": False},
        "gatto": {"domestico": True, "coda_lunga": True},
        "volpe": {"domestico": False, "coda_lunga": True},
    }

    space = HypothesisSpace(hypotheses)
    reasoner = QuestionReasoner(space=space)

    def callback(q):
        return ("unknown", "low")

    result = reasoner.run(callback)

    print(f"  Status: {result.get('status')}")
    print(f"  Ipotesi: {result.get('final_hypothesis')}")

    assert result.get("status") in ["ambiguous", "undecidable", "success"], (
        "Errore: status non gestito"
    )

    print("  [PASS]\n")
    return True


def run_all_tests():
    """Esegue tutti i test"""
    print("=" * 50)
    print("QUESTION-BASED REASONER - TEST SUITE")
    print("=" * 50 + "\n")

    tests = [
        test_reasoner_basic_cycle,
        test_reasoner_stress_incoherent,
        test_probability_consistency,
        test_explainability,
        test_information_gain_selection,
        test_question_generator,
        test_hypothesis_filter,
        test_uncertain_answer,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"  [FAIL] {e}\n")
            failed += 1

    print("=" * 50)
    print(f"RISULTATI: {passed} passed, {failed} failed")
    print("=" * 50)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
