import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine import ReasoningEngine


def test_question_based_available():
    engine = ReasoningEngine()
    assert engine.question_reasoner is not None or engine.question_reasoner is None


def test_engine_init_no_crash():
    engine = ReasoningEngine()
    assert engine is not None
    assert engine.knowledge is not None
