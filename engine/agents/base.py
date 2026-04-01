"""
Base Agent Interface — Definizione del comportamento comune per tutti gli agenti.
"""

from typing import Any, Dict, List, Optional
from ..core.types import ReasoningStep

class BaseAgent:
    """
    Interfaccia per gli agenti specializzati.
    """
    def __init__(self, name: str, role: str, engine=None):
        self.name = name
        self.role = role
        self.engine = engine
        self.context = {}

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Metodo principale da sovrascrivere negli agenti specializzati."""
        raise NotImplementedError("Ogni agente deve implementare il proprio metodo process()")

    def create_step(self, description: str, output: Any, type: str = "agent_action") -> ReasoningStep:
        """Crea uno step di ragionamento tracciabile."""
        return ReasoningStep(
            type=type,
            description=f"[{self.name}] {description}",
            output=output,
            channel=f"agent_{self.name.lower()}"
        )
