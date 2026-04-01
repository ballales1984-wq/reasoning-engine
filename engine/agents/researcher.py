"""
Researcher Agent — Raccoglie informazioni da tutti i canali disponibili.
"""

from typing import Any, Dict, List
from .base import BaseAgent

class ResearcherAgent(BaseAgent):
    """
    Agente specializzato nel reperimento di informazioni.
    """
    def __init__(self, engine=None):
        super().__init__("Researcher", "Data Gathering", engine)

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Esegue la ricerca su tutti i canali."""
        query = input_data.get("query", "")
        results = []
        steps = []
        
        # 1. Ricerca nel Grafo (Structured)
        known = self.engine.knowledge.find(input_data.get("entities", []))
        if known:
            results.append({"source": "knowledge_graph", "content": known})
            steps.append(self.create_step(f"Trovate info nel Knowledge Graph: {list(known.keys())}", known))

        # 2. Ricerca Vettoriale (RAG)
        memory_res = self.engine.memory.search_semantic(query)
        if memory_res["success"] and memory_res["matches"]:
            results.append({"source": "vector_memory", "content": memory_res["matches"]})
            steps.append(self.create_step(f"Recuperate info semantiche: {len(memory_res['matches'])} risultati", memory_res["matches"], type="semantic_memory"))

        # 3. Ricerca Deep Browsing (se URL presente)
        if "urls" in input_data and input_data["urls"]:
            # Per semplicità cerchiamo sul primo URL
            browse_res = self.engine.browser.browse_url(input_data["urls"][0])
            if browse_res["success"]:
                results.append({"source": "web_browsing", "content": browse_res})
                steps.append(self.create_step(f"Estratto contenuto da URL: {browse_res['url']}", browse_res))

        return {
            "accumulated_data": results,
            "steps": steps,
            "status": "gathered"
        }
