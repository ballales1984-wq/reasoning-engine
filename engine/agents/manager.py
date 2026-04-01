"""
Agent Manager — Coordinatore del team di agenti.
"""

from typing import Any, Dict, List
import re
from .researcher import ResearcherAgent
from .analyst import AnalystAgent
from .critic import CriticAgent

class AgentManager:
    """
    Coordinatore del flusso Multi-Agent.
    """
    def __init__(self, engine=None):
        self.engine = engine
        self.researcher = ResearcherAgent(engine)
        self.analyst = AnalystAgent(engine)
        self.critic = CriticAgent(engine)

    def orchestrate(self, question: str, parsed_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Esegue il workflow completo: Ricerca -> Analisi -> Critica."""
        
        # 0. Prepariamo i dati iniziali
        urls = re.findall(r'https?://[^\s{}()\[\]]+', question)
        input_data = {
            "query": question,
            "entities": parsed_dict.get("entities", []),
            "urls": urls
        }
        all_steps = []

        # 1. Fase Ricerca
        res_output = self.researcher.process(input_data)
        all_steps.extend(res_output.get("steps", []))
        input_data.update(res_output)

        # 2. Fase Analisi
        ana_output = self.analyst.process(input_data)
        all_steps.extend(ana_output.get("analyst_steps", []))
        input_data.update(ana_output)

        # 3. Fase Critica
        cri_output = self.critic.process(input_data)
        all_steps.extend(cri_output.get("critic_steps", []))
        
        # 4. Risultato Finale
        return {
            "answer": cri_output.get("final_answer"),
            "confidence": cri_output.get("final_confidence"),
            "steps": all_steps,
            "status": cri_output.get("status"),
            "feedback": cri_output.get("critic_feedback")
        }
