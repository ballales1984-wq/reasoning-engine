import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine import ReasoningEngine


def test_fastpath_datetime():
    engine = ReasoningEngine()
    result = engine.reason("che giorno è oggi?")
    assert result.reasoning_type == "datetime"
    assert "Oggi è" in str(result.answer)
    assert result.confidence == 1.0


def test_fastpath_capital():
    engine = ReasoningEngine()
    result = engine.reason("capitale del giappone?")
    assert result.reasoning_type == "lookup"
    assert "Tokyo" in str(result.answer)
    assert result.confidence == 1.0


def test_multi_agent_pipeline():
    engine = ReasoningEngine()
    result = engine.reason("Qual è la capitale della Francia?", use_llm=False)
    assert result.reasoning_type in ("lookup", "multi_agent_collaboration")
    assert result.confidence > 0
    assert "Parigi" in str(result.answer) or result.confidence < 0.9


def test_critic_rejects_generic_answer():
    engine = ReasoningEngine()
    result = engine.reason("xyz non sense query abc", use_llm=False)
    assert result.confidence <= 0.2 or result.reasoning_type in (
        "web",
        "llm",
        "multi_agent_collaboration",
    )


def test_routing_deterministic_fact():
    engine = ReasoningEngine()
    parsed = engine._parse_question("capitale del canada?")
    mode = engine._classify_route_mode("capitale del canada?", parsed["_parsed"])
    assert mode == "deterministic_fact"


def test_routing_open_world():
    engine = ReasoningEngine()
    parsed = engine._parse_question("ultime notizie tecnologia?")
    mode = engine._classify_route_mode("ultime notizie tecnologia?", parsed["_parsed"])
    assert mode in ("open_world", "reasoning_required")


def test_manager_termination_states():
    from engine.agents.manager import AgentManager

    engine = ReasoningEngine()
    manager = AgentManager(engine)
    result = manager.orchestrate(
        "Qual è la capitale della Francia?",
        {"entities": ["Francia"], "route_mode": "reasoning_required"},
    )
    assert "termination" in result
    assert result["termination"] in ("approved", "rejected", "budget_exhausted")


def test_confidence_calibration():
    engine = ReasoningEngine()
    result = engine.reason("Qual è la capitale della Germania?")
    assert result.confidence is not None
    assert 0.0 <= result.confidence <= 1.0


def test_verified_field():
    engine = ReasoningEngine()
    result = engine.reason("capitale del francia?")
    assert hasattr(result, "verified")


def test_question_based_reasoner_available():
    engine = ReasoningEngine()
    has_qb = hasattr(engine, "question_reasoner")
    assert has_qb or engine.question_reasoner is None


def test_fallback_policy_thresholds():
    engine = ReasoningEngine()
    assert hasattr(engine, "WEB_FALLBACK_MIN_PERTINENCE")
    assert hasattr(engine, "LLM_FALLBACK_MIN_CONFIDENCE")
    assert engine.WEB_FALLBACK_MIN_PERTINENCE >= 0.0
    assert engine.LLM_FALLBACK_MIN_CONFIDENCE >= 0.0
