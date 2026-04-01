import re
from .core.types import (
    Entity,
    ParsedQuery,
    DeductionResult,
    InductionResult,
    AnalogyResult,
    ReasoningStep,
    ReasoningResult,
    SourceMetadata,
)
from .nlp.parser import parse
from .reasoning.deductive import DeductiveReasoner
from .reasoning.inductive import InductiveReasoner
from .reasoning.analogical import AnalogicalReasoner
from .reasoning.rules import RuleEngine
from .reasoning.verifier import Verifier
from .reasoning.explainer import Explainer
from .data.graph import KnowledgeGraph
from .data.learner import Learner
from .tools.math import MathModule
from .tools.finance_data import FinancialDataTool
from .tools.data_analyzer import DataAnalysisTool
from .tools.memory_tool import MemoryTool
from .tools.browsing_tool import BrowsingTool
from .agents.manager import AgentManager
from .llm.bridge import LLMBridge, LLMClient


class ReasoningEngine:
    """
    Il cervello principale. Coordina tutti i componenti e il team di agenti Multi-Agent.
    """

    def __init__(self, llm_api_key: str = None, llm_model: str = "gpt-4o-mini"):
        self.knowledge = KnowledgeGraph()
        self.knowledge.load()  # Carica conoscenze salvate
        self.rules = RuleEngine()
        self.learner = Learner(self.knowledge)
        self.verifier = Verifier(self.rules)
        self.explainer = Explainer()
        self.math = MathModule(self.knowledge, self.rules)
        self.finance_data = FinancialDataTool(self)
        self.data_analyzer = DataAnalysisTool(self)
        self.memory = MemoryTool(self)  # Long-term semantic memory
        self.browser = BrowsingTool(self) # Deep web browsing
        self.agents = AgentManager(self) # Multi-Agent Team
        self.deductive = DeductiveReasoner(self.knowledge, self.rules)
        self.inductive = InductiveReasoner(self.knowledge, self.rules)
        self.analogical = AnalogicalReasoner(self.knowledge)

        # LLM Bridge
        llm_client = LLMClient(model=llm_model, api_key=llm_api_key)
        self.llm = LLMBridge(llm_client, self.knowledge, self.verifier)

        # Contesto conversazione
        self.conversation_history = []

        # Auto-identità
        self.knowledge.add(
            "self_identity",
            description="Sono ReasoningEngine v2.0, un AI che ragiona come un umano. "
            "Combino NLP, ragionamento deduttivo/induttivo/analogico, "
            "matematica avanzata, ricerca web e esecuzione codice.",
            category="system",
            channel="system",
        )

    def learn(
        self,
        concept: str,
        examples: list[str],
        description: str = None,
        category: str = "general",
        channel: str = "user",
        trust_score: float = None,
    ):
        """Insegna un concetto all'engine specificando il canale."""
        c = self.learner.add_concept(
            concept, examples, description, category, channel, trust_score
        )
        self.knowledge.save()
        return f"Ho imparato: {concept} [Canale: {channel}]"

    def save(self):
        """Salva tutta la conoscenza su disco."""
        self.knowledge.save()

    def learn_rule(
        self,
        name: str,
        func,
        description: str = "",
        inputs: list[str] = None,
        output_type: str = "any",
    ):
        """Insegna una regola all'engine."""
        self.rules.add_rule(name, func, description, inputs, output_type)
        return f"Regola aggiunta: {name}"

    def reason(
        self, question: str, use_llm: bool = False, channel: str = "user_interaction"
    ) -> ReasoningResult:
        """
        Ragiona su una domanda tramite collaborazione Multi-Agent.
        """
        # 1. NLP Parsing Iniziale (per intent e canali veloci)
        parsed_dict = self._parse_question(question)
        parsed = parsed_dict["_parsed"]
        
        # 2. Fast-Path: Identity Handling (Sistema 1)
        if parsed.intent == "identity":
            identity = self.knowledge.get("self_identity")
            if identity:
                best = identity.get_best_info()
                return ReasoningResult(
                    answer=best["description"],
                    confidence=1.0,
                    reasoning_type="identity",
                    steps=[ReasoningStep(type="identity", description="Identificazione rapida", output=best, channel="system")],
                    explanation="Accesso diretto all'identità di sistema."
                )

        # 3. Slow-Path: Multi-Agent Orchestration (Sistema 2)
        # Il manager coordina Researcher -> Analyst -> Critic
        agent_res = self.agents.orchestrate(question, parsed_dict)
        
        # 4. Verifica Finale Coerenza (Opzionale nel Critic, qui rinforzata)
        verified = agent_res.get("status") == "approved"
        
        # 5. Generazione Spiegazione Finale
        final_explanation = self.explainer.generate(
            [s.description for s in agent_res["steps"]], 
            {"answer": agent_res["answer"]}
        )
        if agent_res.get("feedback"):
            final_explanation += f"\n[Critica AI: {agent_res['feedback']}]"

        return ReasoningResult(
            answer=agent_res["answer"],
            confidence=agent_res["confidence"],
            reasoning_type="multi_agent_collaboration",
            steps=agent_res["steps"],
            explanation=final_explanation,
            verified=verified,
            sources=[] # Saranno riempiti dagli agenti
        )

        # Step 4: Verification
        verified = False
        if result_data:
            verified = self.verifier.check(result_data, parsed_dict)
            steps.append(
                ReasoningStep(
                    type="verification",
                    description="Verifica finale coerenza",
                    output=verified,
                )
            )

        # Step 5: Salva nel contesto conversazione
        self.conversation_history.append(
            {
                "question": question,
                "answer": str(result_data["answer"]) if result_data else None,
                "confidence": result_data.get("confidence", 0) if result_data else 0,
                "channel": channel,
            }
        )

        # Step 6: Final Response Generation
        if result_data:
            final_explanation = self.explainer.generate(
                [s.description for s in steps], result_data
            )
            # Aggiungi info canali all'explanation
            if sources_used:
                best_source = max(sources_used, key=lambda s: s.trust_score)
                final_explanation += f"\n[Fonte principale: {best_source.channel}]"

            return ReasoningResult(
                answer=result_data["answer"],
                confidence=result_data.get("confidence", 0.9),
                reasoning_type=result_data.get("rule_used", "reasoning"),
                steps=steps,
                explanation=final_explanation,
                verified=verified,
                sources=sources_used,
            )

        # Fallback to LLM if allowed
        if use_llm and self.llm.is_available():
            llm_res = self.llm.fallback_solve(question)
            if llm_res.facts:
                best = max(llm_res.facts, key=lambda f: f.confidence)
                return ReasoningResult(
                    answer=best.value,
                    confidence=best.confidence,
                    reasoning_type="llm",
                    steps=steps
                    + [
                        ReasoningStep(
                            type="llm",
                            description="Risposta via Canale LLM Bridge",
                            channel="ollama",
                        )
                    ],
                    explanation="Ottenuto tramite LLM Bridge (Canale: ollama)",
                    llm_used=True,
                    sources=[SourceMetadata(channel="ollama", trust_score=0.4)],
                )

        return ReasoningResult(
            answer=None,
            confidence=0.0,
            steps=steps,
            explanation="Non ho abbastanza informazioni nei canali attuali per rispondere.",
        )

    def _parse_question(self, question: str) -> dict:
        """Analisi NLP con mappatura delle entità."""
        parsed = parse(question)
        return {
            "intent": parsed.intent,
            "operation": parsed.operation,
            "entities": [e.name for e in parsed.entities],
            "numbers": parsed.numbers,
            "operators": parsed.operators,
            "relations": parsed.relations,
            "confidence": parsed.confidence,
            "_parsed": parsed,
        }

    def what_do_you_know(self) -> dict:
        """Mostra tutto ciò che l'engine ha imparato."""
        return {
            "concepts": self.knowledge.list_all(),
            "rules": self.rules.list_all(),
            "conversation_turns": len(self.conversation_history),
        }
