import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine import ReasoningEngine


def test_datetime_fastpath_avoids_web():
    engine = ReasoningEngine()
    result = engine.reason("che giorno è oggi?", use_llm=True)
    assert result.reasoning_type == "datetime"
    assert "Oggi è" in str(result.answer)


def test_capital_fastpath_avoids_web():
    engine = ReasoningEngine()
    result = engine.reason("capitale del giappone?", use_llm=True)
    assert result.reasoning_type == "lookup"
    assert "Tokyo" in str(result.answer)


def test_deterministic_fact_does_not_use_web_fallback():
    engine = ReasoningEngine()
    parsed = engine._parse_question("capitale del canada?")
    mode = engine._classify_route_mode("capitale del canada?", parsed["_parsed"])
    assert mode == "deterministic_fact"

    result = engine.reason("capitale del canada?", use_llm=False)
    assert result.reasoning_type != "web"
