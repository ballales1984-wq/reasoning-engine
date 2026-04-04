import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine import ReasoningEngine


def test_fallback_thresholds_defined():
    engine = ReasoningEngine()
    assert hasattr(engine, "WEB_FALLBACK_MIN_PERTINENCE")
    assert hasattr(engine, "LLM_FALLBACK_MIN_CONFIDENCE")
    assert engine.WEB_FALLBACK_MIN_PERTINENCE == 0.30
    assert engine.LLM_FALLBACK_MIN_CONFIDENCE == 0.50


def test_fallback_explanation_includes_reason():
    engine = ReasoningEngine()
    engine.agents.orchestrate(
        "dummy query xyz", {"entities": [], "route_mode": "open_world"}
    )
