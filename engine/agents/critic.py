"""
Critic Agent — Controllo qualità e verifica della verità.
"""

from typing import Any, Dict, List
from .base import BaseAgent

class CriticAgent(BaseAgent):
    """
    Agente specializzato nel trovare errori e allucinazioni.
    """
    def __init__(self, engine=None):
        super().__init__("Critic", "Quality Control", engine)

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Critica il lavoro dell'Analyst."""
        draft = input_data.get("draft_answer", "")
        accumulated_data = input_data.get("accumulated_data", [])
        steps = []
        
        # 1. Verifica coerenza (Mock logic per ora)
        # Se la bozza è troppo breve rispetto ai dati, il critico si lamenta
        if len(draft) < 10 and accumulated_data:
            feedback = "La risposta è troppo sintetica e ignora i dati raccolti."
            status = "rejected"
            score = 0.3
        else:
            feedback = "La risposta sembra coerente con i dati raccolti."
            status = "approved"
            score = 0.95
            
        steps.append(self.create_step(f"Verifica completata: {status}", {"feedback": feedback, "score": score}))

        return {
            "final_answer": draft,
            "critic_feedback": feedback,
            "critic_steps": steps,
            "status": status,
            "final_confidence": score
        }
