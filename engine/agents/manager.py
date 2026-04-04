"""
Agent Manager — Coordinatore del team di agenti.
"""

import re
from typing import Any, Dict, List
from .researcher import ResearcherAgent
from .analyst import AnalystAgent
from .critic import CriticAgent

MAX_ITERATIONS = 2


class AgentManager:
    """
    Coordinatore del flusso Multi-Agent.
    """

    def __init__(self, engine=None):
        self.engine = engine
        self.researcher = ResearcherAgent(engine)
        self.analyst = AnalystAgent(engine)
        self.critic = CriticAgent(engine)

    @staticmethod
    def _extract_entities(query: str) -> List[str]:
        entities = []
        query_lower = query.lower()
        words = query.split()
        for w in words:
            if w and len(w) > 2 and w[0].isupper():
                entities.append(w.rstrip("?!.,;:"))
        return entities

    def orchestrate(self, question: str, parsed_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Esegue il workflow completo: Ricerca -> Analisi -> Critica (con retry guidato)."""

        urls = re.findall(r"https?://[^\s{}()\[\]]+", question)
        input_data = {
            "query": question,
            "entities": parsed_dict.get("entities", [])
            or self._extract_entities(question),
            "urls": urls,
            "route_mode": parsed_dict.get("route_mode", "reasoning_required"),
        }
        all_steps = []

        critic_status = None
        critic_feedback = None
        iteration = 0

        while iteration < MAX_ITERATIONS:
            if iteration > 0 and critic_status == "needs_retry":
                constraints = input_data.get("critic_constraints", {})
                if constraints:
                    input_data["researcher_constraints"] = constraints

            res_output = self.researcher.process(input_data)
            all_steps.extend(res_output.get("steps", []))
            input_data.update(res_output)

            ana_output = self.analyst.process(input_data)
            all_steps.extend(ana_output.get("analyst_steps", []))
            input_data.update(ana_output)

            cri_output = self.critic.process(input_data)
            all_steps.extend(cri_output.get("critic_steps", []))

            critic_status = cri_output.get("status")
            critic_feedback = cri_output.get("critic_feedback")

            if critic_status == "approved":
                return {
                    "answer": cri_output.get("final_answer"),
                    "confidence": cri_output.get("final_confidence"),
                    "steps": all_steps,
                    "status": "success",
                    "feedback": critic_feedback,
                    "pertinence_score": cri_output.get("pertinence_score", 0.0),
                    "grounding_score": cri_output.get("grounding_score", 0.0),
                    "iterations": iteration + 1,
                    "termination": "approved",
                }

            if critic_status == "rejected":
                final_answer = (
                    "Mi dispiace, non ho trovato una risposta soddisfacente. "
                    "Puoi riformulare la domanda o fornire più contesto?"
                )
                return {
                    "answer": final_answer,
                    "confidence": 0.1,
                    "steps": all_steps,
                    "status": "rejected",
                    "feedback": critic_feedback,
                    "pertinence_score": 0.0,
                    "grounding_score": 0.0,
                    "iterations": iteration + 1,
                    "termination": "rejected",
                }

            iteration += 1

        if iteration == MAX_ITERATIONS:
            return {
                "answer": cri_output.get("final_answer")
                or "Raggiunto limite tentativi.",
                "confidence": max(cri_output.get("final_confidence", 0.3), 0.3),
                "steps": all_steps,
                "status": critic_status or "uncertain",
                "feedback": f"Buget iterazioni esaurito. {critic_feedback}",
                "pertinence_score": cri_output.get("pertinence_score", 0.0),
                "grounding_score": cri_output.get("grounding_score", 0.0),
                "iterations": iteration,
                "termination": "budget_exhausted",
            }

        return {
            "answer": cri_output.get("final_answer"),
            "confidence": cri_output.get("final_confidence", 0.0),
            "steps": all_steps,
            "status": critic_status,
            "feedback": critic_feedback,
            "iterations": iteration,
            "termination": "unknown",
        }
