#!/usr/bin/env python3
"""
Test per Question-Based Module
"""

import sys

sys.path.insert(0, ".")

from engine.question_based import (
    HypothesisSpace,
    QuestionGenerator,
    InformationGainSelector,
    ProbabilityUpdater,
    QuestionReasoner,
    Explainer,
)
from engine.question_based.hypothesis_space import Hypothesis
from engine.question_based.kg_bridge import KGBridge
from engine.question_based.llm_extractor import LLMExtractor
from engine.question_based.auto_researcher import AutoResearcher


def test_hypothesis_space():
    print("Test HypothesisSpace...")
    hs = HypothesisSpace("animals")

    h1 = Hypothesis("cane", "Cane", 0.3)
    h2 = Hypothesis("gatto", "Gatto", 0.7)

    hs.add_hypothesis(h1)
    hs.add_hypothesis(h2)

    assert hs.get_hypothesis("cane") is not None
    assert hs.get_top_hypothesis().name == "Gatto"
    assert 0 < hs.get_entropy() <= 1

    print("  PASSED")


def test_question_generator():
    print("Test QuestionGenerator...")
    qg = QuestionGenerator("animals")

    questions = qg.get_questions()
    assert len(questions) > 0

    q = qg.generate_question("colore", "animals")
    assert "colore" in q

    print("  PASSED")


def test_information_gain():
    print("Test InformationGainSelector...")
    igs = InformationGainSelector()

    probs = [0.5, 0.5]
    entropy = igs.calculate_entropy(probs)
    assert entropy == 1.0

    print("  PASSED")


def test_probability_updater():
    print("Test ProbabilityUpdater...")
    pu = ProbabilityUpdater()

    hs = HypothesisSpace("test")
    hs.add_hypothesis(Hypothesis("h1", "H1", 0.5))
    hs.add_hypothesis(Hypothesis("h2", "H2", 0.5))

    pu.soft_update(hs, "test?", True, 0.3)

    top = hs.get_top_hypothesis()
    assert top.probability > 0.5

    print("  PASSED")


def test_question_reasoner():
    print("Test QuestionReasoner...")
    qr = QuestionReasoner(domain="test", max_iterations=3)

    qr.add_hypotheses(
        [
            {"id": "a", "name": "A", "probability": 0.5, "features": {}},
            {"id": "b", "name": "B", "probability": 0.5, "features": {}},
        ]
    )

    question = qr.generate_next_question()
    assert question is not None

    qr.step(question, True)
    assert len(qr.trace) == 1

    print("  PASSED")


def test_explainer():
    print("Test Explainer...")
    exp = Explainer()

    exp.add_step({"question": "Test?", "answer": True, "confidence": 0.8})
    exp.add_step({"question": "Test2?", "answer": False, "confidence": 0.9})

    summary = exp.get_summary()
    assert "Test?" in summary
    assert len(exp.get_trace()) == 2

    print("  PASSED")


def test_kg_bridge():
    print("Test KGBridge...")
    kg = KGBridge()

    kg.load_from_dict(
        {
            "Cane": {"habitat": "terra", "domestico": True},
            "Gatto": {"habitat": "terra", "domestico": True},
        }
    )

    features = kg.get_features("Cane")
    assert features["habitat"] == "terra"

    hypos = kg.to_hypotheses()
    assert len(hypos) == 2

    print("  PASSED")


def test_llm_extractor():
    print("Test LLMExtractor...")
    le = LLMExtractor()

    features = le._rule_based_extraction("Il cane ha il pelo rosso e grande")
    assert "colore" in features

    hypos = le.generate_hypotheses("1. Cane\n  habitat: terra\n2. Gatto")
    assert len(hypos) >= 1

    print("  PASSED")


def test_auto_researcher():
    print("Test AutoResearcher...")
    ar = AutoResearcher()

    result = ar.research("test query")
    assert "error" in result or "text" in result

    ar.research_topic("animali")
    assert len(ar.get_research_data()) > 0

    print("  PASSED")


def run_all_tests():
    print("\n=== QUESTION_BASED MODULE TESTS ===\n")

    test_hypothesis_space()
    test_question_generator()
    test_information_gain()
    test_probability_updater()
    test_question_reasoner()
    test_explainer()
    test_kg_bridge()
    test_llm_extractor()
    test_auto_researcher()

    print("\n=== ALL TESTS PASSED ===\n")


if __name__ == "__main__":
    run_all_tests()
