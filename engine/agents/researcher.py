"""
Researcher Agent — Raccoglie informazioni da tutti i canali disponibili.
Include catena di domande: se non sa, chiede al LLM.
"""

from typing import Any, Dict, List
from .base import BaseAgent
from ..tools.web import WebTool


class ResearcherAgent(BaseAgent):
    """
    Agente specializzato nel reperimento di informazioni.
    Usa catena: KG → Memory → Web → LLM (se necessario)
    """

    def __init__(self, engine=None):
        super().__init__("Researcher", "Data Gathering", engine)
        self.web_tool = WebTool()

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Esegue la ricerca su tutti i canali con catena di fallback."""
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

        found_info = False

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
                    found_info = True

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
                    found_info = True

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
                        found_info = True
                if not found_info and allow_web_fallback:
                    web_res = self.web_tool.search(search_query, max_results=3)
                    if web_res.get("results"):
                        results.append({"source": "web_search", "content": web_res})
                        steps.append(
                            self.create_step(
                                f"Ricerca web: {len(web_res['results'])} risultati",
                                web_res,
                            )
                        )
                        found_info = True

        # CATENA DI DOMANDE: se non ha trovato info, chiede al LLM
        if not found_info and self.engine.llm.is_available():
            llm_info = self._ask_llm_for_info(query, search_entities)
            if llm_info:
                results.append({"source": "llm_knowledge", "content": llm_info})
                steps.append(
                    self.create_step(
                        "Info da LLM (catena di domande)",
                        llm_info,
                        type="llm_chain",
                    )
                )
                found_info = True

        # Seconda iterazione: se info insufficienti, espandi con LLM
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
            "found_info": found_info,
        }

    def _ask_llm_for_info(
        self, query: str, entities: List[str]
    ) -> Dict[str, Any] | None:
        """Catena di domande: chiede al LLM info su entità sconosciute."""
        if not entities:
            entities = self._extract_entities_from_query(query)

        if not entities:
            return None

        info_collected = {}

        for entity in entities:
            # Prima chiede: " sai chi è X? "
            prompt = f"""
Sei un assistente di ricerca. Rispondi in italiano.

Domanda: "{query}"
Entità da cercare: {entity}

Istruzioni:
1. Se CONOSCI bene questa entità, rispondi con un JSON:
   {{"conoscenza": "descrizione dell'entità", "fonte": "memoria"}}

2. Se NON CONOSCI questa entità, rispondi con:
   {{"conoscenza": null, "fonte": "sconosciuto", "richiede_ricerca": true}}

Rispondi SOLO con JSON."""

            try:
                raw = self.engine.llm.llm.ask(prompt, max_tokens=200)
                import re
                import json

                json_match = re.search(r"\{[^{}]*\}", raw, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    if data.get("conoscenza"):
                        info_collected[entity] = {
                            "description": data["conoscenza"],
                            "source": data.get("fonte", "llm"),
                        }
                    elif data.get("richiede_ricerca"):
                        # Se non sa, marca per ricerca web
                        info_collected[entity] = {
                            "description": None,
                            "source": "sconosciuto",
                            "need_web_search": True,
                        }
            except:
                pass

        # Se almeno un'entità è sconosciuta, cerca sul web
        needs_web = any(v.get("need_web_search") for v in info_collected.values())
        if needs_web and self.web_tool:
            for entity, info in info_collected.items():
                if info.get("need_web_search"):
                    web_res = self.web_tool.search(entity, max_results=2)
                    if web_res.get("results"):
                        first = web_res["results"][0]
                        info["description"] = first.get("content", "")[:300]
                        info["source"] = "web_search"
                        info["need_web_search"] = False

        return info_collected if info_collected else None

    def _extract_entities_from_query(self, query: str) -> List[str]:
        """Estrae entità dalla query."""
        import re

        words = query.split()
        entities = []
        for w in words:
            if w and len(w) > 2 and w[0].isupper():
                entities.append(w.rstrip("?!.,;:"))
        return entities[:5]
