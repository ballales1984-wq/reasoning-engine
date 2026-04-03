#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Coverage per Question-Based Reasoner
Testa casi limite, edge cases, e diversi scenari
"""

import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

sys.path.insert(0, ".")

from engine.question_based import QuestionReasoner
from engine.question_based.hypothesis_space import HypothesisSpace, Hypothesis
from engine.question_based.question_generator import QuestionGenerator
from engine.question_based.information_gain import InformationGainSelector
from engine.question_based.probability_updater import ProbabilityUpdater
from engine.question_based.explainer import Explainer
from engine.question_based.kg_bridge import KGBridge
from engine.question_based.llm_extractor import LLMExtractor
from engine.question_based.auto_researcher import AutoResearcher


def test_hypothesis_space():
    print("\n[TEST] HypothesisSpace")
    hs = HypothesisSpace("test")
    hs.add_hypothesis(Hypothesis("h1", "H1", 0.5))
    hs.add_hypothesis(Hypothesis("h2", "H2", 0.5))
    assert hs.get_hypothesis("h1") is not None
    hs.renormalize()
    assert abs(hs.get_hypothesis("h1").probability - 0.5) < 0.01
    print("  OK")


def test_question_generator():
    print("\n[TEST] QuestionGenerator")
    qg = QuestionGenerator("animals")
    qs = qg.get_questions()
    assert len(qs) > 0
    q = qg.generate_question("colore", "animals")
    assert "colore" in q
    for domain in ["animals", "colors", "sports"]:
        assert len(QuestionGenerator(domain).get_questions()) > 0
    print("  OK")


def test_kg_bridge():
    print("\n[TEST] KGBridge")
    kg = KGBridge()
    kg.load_from_dict({"Cane": {"domestico": True}, "Gatto": {"domestico": True}})
    assert kg.get_features("Cane")["domestico"] == True
    assert len(kg.to_hypotheses()) == 2
    print("  OK")


def test_information_gain():
    print("\n[TEST] InformationGainSelector")
    igs = InformationGainSelector()
    assert abs(igs.calculate_entropy([0.5, 0.5]) - 1.0) < 0.01
    hs = HypothesisSpace("test")
    hs.add_hypothesis(Hypothesis("h1", "H1", 0.33))
    hs.add_hypothesis(Hypothesis("h2", "H2", 0.33))
    hs.add_hypothesis(Hypothesis("h3", "H3", 0.34))
    gain = igs.calculate_information_gain(
        hs,
        "test?",
        {"h1": 0.8, "h2": 0.2, "h3": 0.1},
        {"h1": 0.2, "h2": 0.8, "h3": 0.9},
    )
    assert gain >= 0
    print("  OK")


def test_probability_updater():
    print("\n[TEST] ProbabilityUpdater")
    pu = ProbabilityUpdater(smoothing=0.01)
    hs = HypothesisSpace("test")
    hs.add_hypothesis(Hypothesis("h1", "H1", 0.5, features={"colore": True}))
    hs.add_hypothesis(Hypothesis("h2", "H2", 0.5, features={"colore": False}))
    pu.soft_update(hs, "E' rosso?", True, 0.3)
    feature, value = pu._extract_feature_from_question("E' un animale domestico?")
    assert feature == "domestico"
    print("  OK")


def test_explainer():
    print("\n[TEST] Explainer")
    exp = Explainer()
    exp.add_step({"question": "Test?", "answer": True, "confidence": 0.8})
    exp.add_step({"question": "Test2?", "answer": False, "confidence": 0.9})
    assert "Test?" in exp.get_summary()
    assert len(exp.get_trace()) == 2
    print("  OK")


def test_kg_bridge():
    print("\n[TEST] KGBridge")
    kg = KGBridge({"Cane": {"domestico": True}, "Gatto": {"domestico": True}})
    assert kg.get_features("Cane")["domestico"] == True
    assert len(kg.to_hypotheses()) == 2
    print("  OK")


def test_llm_extractor():
    print("\n[TEST] LLMExtractor")
    le = LLMExtractor()
    features = le._rule_based_extraction("Il cane ha il pelo rosso")
    assert "colore" in features
    print("  OK")


def test_auto_researcher():
    print("\n[TEST] AutoResearcher")
    ar = AutoResearcher()
    assert "error" in ar.research("test")
    print("  OK")


def test_edge_cases():
    print("\n[TEST] Edge Cases")
    reasoner = QuestionReasoner(domain="test", max_iterations=3)
    reasoner.add_hypotheses(
        [{"id": "solo", "name": "Unico", "probability": 1.0, "features": {}}]
    )
    assert reasoner.hypothesis_space.get_top_hypothesis().name == "Unico"
    reasoner2 = QuestionReasoner(domain="test")
    assert reasoner2.hypothesis_space.get_top_hypothesis() is None
    pu = ProbabilityUpdater()
    feature, _ = pu._extract_feature_from_question("Domanda generica?")
    assert feature == "unknown"
    print("  OK")


def test_reasoner_flow():
    print("\n[TEST] Reasoner Flow")
    reasoner = QuestionReasoner(
        domain="colors", max_iterations=5, confidence_threshold=0.90
    )
    reasoner.add_hypotheses(
        [
            {
                "id": "rosso",
                "name": "Rosso",
                "probability": 0.33,
                "features": {"primario": True, "caldo": True},
            },
            {
                "id": "blu",
                "name": "Blu",
                "probability": 0.33,
                "features": {"primario": True, "caldo": False},
            },
            {
                "id": "verde",
                "name": "Verde",
                "probability": 0.34,
                "features": {"primario": False, "caldo": False},
            },
        ]
    )

    def ask_simulated(q):
        return "primario" in q.lower() or "caldo" in q.lower()

    result = reasoner.run(ask_simulated)
    assert result["result"] is not None
    print(f"  Risultato: {result['result'].name}")
    print("  OK")


def test_multiple_domains():
    print("\n[TEST] Multiple Domains")
    for domain in ["animals", "colors", "sports", "general"]:
        r = QuestionReasoner(domain=domain, max_iterations=2)
        r.add_hypotheses(
            [
                {
                    "id": "a",
                    "name": "A",
                    "probability": 0.5,
                    "features": {"test": True},
                },
                {
                    "id": "b",
                    "name": "B",
                    "probability": 0.5,
                    "features": {"test": False},
                },
            ]
        )
        q = r.generate_next_question()
        assert q is not None
        r.step(q, True)
    print("  OK")


def main():
    print("=" * 60)
    print("  QUESTION-BASED REASONER - TEST COVERAGE")
    print("=" * 60)

    tests = [
        test_hypothesis_space,
        test_question_generator,
        test_information_gain,
        test_probability_updater,
        test_explainer,
        test_kg_bridge,
        test_llm_extractor,
        test_auto_researcher,
        test_edge_cases,
        test_reasoner_flow,
        test_multiple_domains,
    ]

    passed = failed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"  ERR: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"  Test: {passed + failed} | Passati: {passed} | Falliti: {failed}")
    print("=" * 60)
    return failed == 0


if __name__ == "__main__":
    success = main()
    print("\n" + ("TUTTI I TEST PASSATI!" if success else "ALCUNI TEST FALLITI!"))
    sys.exit(0 if success else 1)
