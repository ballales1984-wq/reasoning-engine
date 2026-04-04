import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine import ReasoningEngine
from engine.agents.manager import AgentManager


def test_manager_returns_termination_approved():
    engine = ReasoningEngine()
    manager = AgentManager(engine)
    parsed_dict = {
        "entities": ["Francia"],
        "route_mode": "reasoning_required",
    }
    result = manager.orchestrate("Qual è la capitale della Francia?", parsed_dict)
    assert result.get("termination") == "approved"
    assert "1" in str(result.get("iterations", ""))


def test_manager_returns_termination_rejected():
    engine = ReasoningEngine()
    manager = AgentManager(engine)
    parsed_dict = {
        "entities": [],
        "route_mode": "reasoning_required",
    }
    result = manager.orchestrate("xxx non ha senso questa domanda xxx", parsed_dict)
    assert result.get("termination") in ("rejected", "budget_exhausted")


def test_manager_iteration_count():
    engine = ReasoningEngine()
    manager = AgentManager(engine)
    parsed_dict = {
        "entities": ["Francia"],
        "route_mode": "reasoning_required",
    }
    result = manager.orchestrate("Qual è la capitale della Francia?", parsed_dict)
    assert result.get("iterations", 0) >= 1
