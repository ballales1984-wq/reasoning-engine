"""
Core Engine — Tipi e classi base.
"""

from .loop import ReasoningLoop
from .state import StateManager
from .context import ContextManager
from .types import (
    Entity,
    Relation,
    ParsedQuery,
    DeductionStep,
    DeductionResult,
    Pattern,
    InductionResult,
    Analogy,
    AnalogyResult,
    ReasoningStep,
    ReasoningResult,
)
