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

        # 2. Ragionamento Simbolico (Fase 1: Deduzione)
        logical_deductions = []
        entities = input_data.get("entities", [])
        for entity in entities:
            ded_res = self.engine.deductive.deduce(entity)
            if ded_res.found:
                logical_deductions.append(ded_res)
                steps.append(self.create_step(f"Deduzione logica su '{entity}': {ded_res.conclusion}", ded_res))

        # 3. Ragionamento Simbolico (Fase 2: Analogia - Fallback se dati scarsi)
        analogies_found = []
        if not all_text or len(all_text) < 100:
            for entity in entities:
                ana_res = self.engine.analogical.find_analogies(entity)
                if ana_res.found:
                    analogies_found.append(ana_res)
                    steps.append(self.create_step(f"Trovata analogia per '{entity}' ↔ {ana_res.best_analogy.target}", ana_res))

        # 4. Sintetizziamo la risposta finale arricchita
        if not all_text and not logical_deductions:
            draft = "Non ho trovato informazioni dirette."
            if analogies_found:
                best_ana = analogies_found[0].best_analogy
                draft += f" Tuttavia, per analogia con {best_ana.target}, potrei ipotizzare caratteristiche simili."
            confidence = 0.2
        else:
            draft = all_text
            if logical_deductions:
                draft += "\n\n💡 **Inferenze Deduttive:**\n"
                for d in logical_deductions:
                    draft += f" - {d.conclusion}\n"
            confidence = 0.9 if logical_deductions else 0.8
            
        steps.append(self.create_step("Analisi e inferenze logiche completate", {"confidence": confidence}))

        return {
            "draft_answer": draft,
            "analyst_steps": steps,
            "status": "analyzed",
            "confidence": confidence
        }
