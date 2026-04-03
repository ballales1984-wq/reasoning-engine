"""
Researcher Agent — Raccoglie informazioni da tutti i canali disponibili.
"""

from typing import Any, Dict, List
from .base import BaseAgent
from ..tools.web import WebTool


class ResearcherAgent(BaseAgent):
    """
    Agente specializzato nel reperimento di informazioni.
    """

    def __init__(self, engine=None):
        super().__init__("Researcher", "Data Gathering", engine)
        self.web_tool = WebTool()

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Esegue la ricerca su tutti i canali."""
        query = input_data.get("query", "")
        results = []
        steps = []

        # 1. Ricerca nel Grafo (Structured)
        raw_known = self.engine.knowledge.find(input_data.get("entities", []))
        # Evita falsi positivi: mantieni solo concetti realmente trovati.
        known = {k: v for k, v in raw_known.items() if v is not None}
        if known:
            results.append({"source": "knowledge_graph", "content": known})
            steps.append(
                self.create_step(
                    f"Trovate info nel Knowledge Graph: {list(known.keys())}", known
                )
            )

        # 2. Ricerca Vettoriale (RAG)
        memory_res = self.engine.memory.search_semantic(query)
        if memory_res["success"] and memory_res["matches"]:
            results.append(
                {"source": "vector_memory", "content": memory_res["matches"]}
            )
            steps.append(
                self.create_step(
                    f"Recuperate info semantiche: {len(memory_res['matches'])} risultati",
                    memory_res["matches"],
                    type="semantic_memory",
                )
            )

        # 3. Ricerca Deep Browsing (se URL presente)
        if "urls" in input_data and input_data["urls"]:
            # Per semplicità cerchiamo sul primo URL
            browse_res = self.engine.browser.browse_url(input_data["urls"][0])
            if browse_res["success"]:
                results.append({"source": "web_browsing", "content": browse_res})
                steps.append(
                    self.create_step(
                        f"Estratto contenuto da URL: {browse_res['url']}", browse_res
                    )
                )

        # 4. Fallback: Ricerca web se nessun risultato trovato
        if not results:
            web_res = self.web_tool.search(query, max_results=3)
            if web_res.get("results"):
                results.append({"source": "web_search", "content": web_res})
                steps.append(
                    self.create_step(
                        f"Ricerca web: {len(web_res['results'])} risultati", web_res
                    )
                )

        return {
            "accumulated_data": results,
            "steps": steps,
            "status": "gathered" if results else "no_results",
        }
