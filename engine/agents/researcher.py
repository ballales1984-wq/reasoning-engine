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
        route_mode = input_data.get("route_mode", "reasoning_required")
        allow_web_fallback = route_mode == "open_world"
        constraints = input_data.get("researcher_constraints", {})
        results = []
        steps = []

        suggested_sources = constraints.get("suggested_sources", [])
        use_sources = constraints.get("use_sources", [])
        expand_with = constraints.get("expand_with", None)
        focus_on = constraints.get("focus_on", None)

        search_query = focus_on or query
        search_entities = input_data.get("entities", [])

        if suggested_sources:
            priority_order = suggested_sources
        elif use_sources:
            priority_order = use_sources
        else:
            priority_order = ["knowledge_graph", "vector_memory", "web_search"]

        for source in priority_order:
            if source == "knowledge_graph":
                raw_known = self.engine.knowledge.find(search_entities)
                known = {k: v for k, v in raw_known.items() if v is not None}
                if known:
                    results.append({"source": "knowledge_graph", "content": known})
                    steps.append(
                        self.create_step(
                            f"Trovate info nel Knowledge Graph: {list(known.keys())}",
                            known,
                        )
                    )

            elif source == "vector_memory":
                memory_res = self.engine.memory.search_semantic(search_query)
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

            elif source == "web_search":
                if "urls" in input_data and input_data["urls"]:
                    browse_res = self.engine.browser.browse_url(input_data["urls"][0])
                    if browse_res["success"]:
                        results.append(
                            {"source": "web_browsing", "content": browse_res}
                        )
                        steps.append(
                            self.create_step(
                                f"Estratto contenuto da URL: {browse_res['url']}",
                                browse_res,
                            )
                        )
                if not results and allow_web_fallback:
                    web_res = self.web_tool.search(search_query, max_results=3)
                    if web_res.get("results"):
                        results.append({"source": "web_search", "content": web_res})
                        steps.append(
                            self.create_step(
                                f"Ricerca web: {len(web_res['results'])} risultati",
                                web_res,
                            )
                        )

        if (
            constraints.get("reason") == "too_short"
            and expand_with == "evidence_details"
        ):
            if not results:
                if allow_web_fallback:
                    web_res = self.web_tool.search(search_query, max_results=5)
                    if web_res.get("results"):
                        results.append({"source": "web_search", "content": web_res})
                        steps.append(
                            self.create_step(
                                f"Expand con ricerca web aggiuntiva: {len(web_res['results'])}",
                                web_res,
                            )
                        )

        return {
            "accumulated_data": results,
            "steps": steps,
            "status": "gathered" if results else "no_results",
        }
