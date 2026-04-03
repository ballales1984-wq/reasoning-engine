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
        query = str(input_data.get("query", "") or "")
        steps = []

        # 1. Filtriamo per trovare l'informazione migliore
        # Per ora prendiamo l'informazione più completa tra quelle disponibili
        text_chunks = []
        direct_answer = None
        for item in accumulated_data:
            if item["source"] == "knowledge_graph":
                # Convertiamo il dizionario Concepts in testo leggibile
                for concept_name, concept in item["content"].items():
                    if concept:
                        best_info = concept.get_best_info()
                        if best_info and best_info.get("description"):
                            text_chunks.append(
                                f"{concept_name}: {best_info['description']}."
                            )

                        # Valorizza anche le relazioni del KG (capitale, ecc.).
                        rels = getattr(concept, "relations", {}) or {}
                        for rel_name, targets in rels.items():
                            for target in targets:
                                target_value = (
                                    target[0] if isinstance(target, tuple) else target
                                )
                                text_chunks.append(
                                    f"{concept_name} {rel_name} {target_value}."
                                )

                        ql = query.lower()
                        if "capitale" in ql:
                            for rel_name, targets in rels.items():
                                if "capitale" in rel_name.lower() and targets:
                                    target = (
                                        targets[0][0]
                                        if isinstance(targets[0], tuple)
                                        else targets[0]
                                    )
                                    direct_answer = (
                                        f"La capitale della {concept_name} è {target}."
                                    )
            elif item["source"] == "vector_memory":
                for match in item["content"]:
                    text_chunks.append(f"{match['text']}.")
            elif item["source"] == "web_browsing":
                web_content = item["content"].get("content", "")[:2000]
                if web_content:
                    text_chunks.append(web_content)
            elif item["source"] == "web_search":
                # Usa risultati web solo se non hai dati dal KG o memoria
                if not text_chunks:
                    # Estrai risultati dalla ricerca web - prendi SOLO il primo
                    results = item["content"].get("results", [])
                    if results and results[0].get("content"):
                        # Prendi solo il primo risultato
                        text_chunks.append(results[0]["content"][:300])

        all_text = " ".join(text_chunks).strip()

        # 2. Ragionamento Simbolico (Fase 1: Deduzione)
        logical_deductions = []
        entities = input_data.get("entities", [])
        for entity in entities:
            ded_res = self.engine.deductive.deduce(entity)
            if ded_res.found:
                logical_deductions.append(ded_res)
                steps.append(
                    self.create_step(
                        f"Deduzione logica su '{entity}': {ded_res.conclusion}", ded_res
                    )
                )

        # 3. Ragionamento Simbolico (Fase 2: Analogia - Fallback se dati scarsi)
        analogies_found = []
        if not all_text or len(all_text) < 100:
            for entity in entities:
                ana_res = self.engine.analogical.find_analogies(entity)
                if ana_res.found:
                    analogies_found.append(ana_res)
                    steps.append(
                        self.create_step(
                            f"Trovata analogia per '{entity}' ↔ {ana_res.best_analogy.target}",
                            ana_res,
                        )
                    )

        # 4. Sintetizziamo la risposta finale arricchita
        if direct_answer:
            draft = direct_answer
            confidence = 0.95
        elif not all_text and not logical_deductions:
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

        steps.append(
            self.create_step(
                "Analisi e inferenze logiche completate", {"confidence": confidence}
            )
        )

        return {
            "draft_answer": draft,
            "analyst_steps": steps,
            "status": "analyzed",
            "confidence": confidence,
        }
