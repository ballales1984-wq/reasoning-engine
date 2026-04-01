"""
Analyst Agent — Collatore di informazioni e creatore di risposte.
"""

from typing import Any, Dict, List
from .base import BaseAgent

class AnalystAgent(BaseAgent):
    """
    Agente specializzato nel processare i dati e formare un'ipotesi.
    """
    def __init__(self, engine=None):
        super().__init__("Analyst", "Data Processing", engine)

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analizza i dati raccolti dal Researcher."""
        accumulated_data = input_data.get("accumulated_data", [])
        steps = []
        
        # 1. Filtriamo per trovare l'informazione migliore
        # Per ora prendiamo l'informazione più completa tra quelle disponibili
        all_text = ""
        for item in accumulated_data:
            if item["source"] == "knowledge_graph":
                # Convertiamo il dizionario Concepts in testo leggibile
                for concept_name, concept in item["content"].items():
                    if concept:
                        best_info = concept.get_best_info()
                        if best_info:
                            all_text += f"{concept_name}: {best_info['description']}. "
            elif item["source"] == "vector_memory":
                for match in item["content"]:
                    all_text += f"{match['text']}. "
            elif item["source"] == "web_browsing":
                all_text += item["content"].get("content", "")[:2000]

        # 2. Sintetizziamo una bozza di risposta
        if not all_text:
            draft = "Non sono state trovate informazioni sufficienti."
            confidence = 0.0
        else:
            draft = all_text # In futuro questo passerebbe per l'Explainer/LLM
            confidence = 0.8
            
        steps.append(self.create_step(f"Sintetizzata bozza di risposta da {len(accumulated_data)} fonti", {"draft": draft[:100]}))

        return {
            "draft_answer": draft,
            "analyst_steps": steps,
            "status": "analyzed",
            "confidence": confidence
        }
