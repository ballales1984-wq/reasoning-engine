from typing import Dict, Any, List, Optional, Callable
import json


class AutoResearcher:
    def __init__(
        self,
        web_search: Optional[Callable] = None,
        llm_provider: Optional[Callable] = None,
    ):
        self.web_search = web_search
        self.llm_provider = llm_provider
        self.research_data: Dict[str, Any] = {}

    def research(self, query: str) -> Dict[str, Any]:
        if self.web_search:
            search_results = self.web_search(query)
            self.research_data[query] = search_results
            return search_results

        if self.llm_provider:
            response = self.llm_provider(
                f"Fornisci informazioni dettagliate su: {query}"
            )
            self.research_data[query] = {"text": response}
            return {"text": response}

        return {"error": "Nessun provider disponibile"}

    def research_topic(self, topic: str) -> Dict[str, Any]:
        sub_queries = [
            f"{topic} caratteristiche",
            f"{topic} proprietà",
            f"{topic} categorie",
        ]

        results = {}
        for sq in sub_queries:
            results[sq] = self.research(sq)

        return results

    def enrich_hypotheses(
        self, hypotheses: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        enriched = []

        for h in hypotheses:
            h_name = h.get("name", "")
            if h_name:
                info = self.research(h_name)
                h["research"] = info

            enriched.append(h)

        return enriched

    def get_research_data(self) -> Dict[str, Any]:
        return self.research_data

    def clear(self):
        self.research_data = {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "researcher": "AutoResearcher",
            "has_web_search": self.web_search is not None,
            "has_llm_provider": self.llm_provider is not None,
            "research_queries": list(self.research_data.keys()),
        }
