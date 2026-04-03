import re
import os
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
        self.browser = BrowsingTool(self)  # Deep web browsing
        self.agents = AgentManager(self)  # Multi-Agent Team
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

    def _state_path(self, name: str = "default", directory: str = None) -> str:
        """Costruisce il percorso del file di stato."""
        filename = name if str(name).endswith(".json") else f"{name}.json"
        if directory:
            return os.path.join(directory, filename)
        return os.path.join(os.path.dirname(__file__), "..", "data", filename)

    def save(self, name: str = "default", directory: str = None) -> str:
        """Salva la conoscenza su disco e ritorna il path usato."""
        if name == "default" and directory is None:
            self.knowledge.save()
            return os.path.join(os.path.dirname(__file__), "..", "data", "knowledge.json")
        path = self._state_path(name, directory)
        self.knowledge.save(path)
        return path

    def load(self, name: str = "default", directory: str = None) -> bool:
        """Carica conoscenza da disco; ritorna True se il file esiste."""
        if name == "default" and directory is None:
            self.knowledge.load()
            return True
        path = self._state_path(name, directory)
        if not os.path.exists(path):
            return False
        self.knowledge.load(path)
        return True

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

        # 2. Fast-Path: Saluti brevi (evita risposte "sporche" dal KG)
        normalized = re.sub(r"[^\w\s]", "", question.lower()).strip()
        greeting_tokens = set(normalized.split())
        greeting_words = {
            "ciao",
            "salve",
            "hey",
            "hello",
            "hi",
            "buongiorno",
            "buonasera",
            "buonanotte",
        }
        if (
            normalized
            and len(greeting_tokens) <= 3
            and greeting_tokens.issubset(greeting_words)
        ):
            return ReasoningResult(
                answer="Ciao! Ci sono, dimmi pure come ti posso aiutare.",
                confidence=1.0,
                reasoning_type="greeting",
                steps=[
                    ReasoningStep(
                        type="greeting",
                        description="Gestione diretta del saluto",
                        input=question,
                        output="saluto_riconosciuto",
                        channel="system",
                    )
                ],
                explanation="Risposta rapida di saluto.",
                verified=True,
            )

        # 3. Fast-Path: Richiesta capacità/identità (generale, non frase-per-frase)
        if self._is_capability_question(question, normalized, parsed):
            identity = self.knowledge.get("self_identity")
            if identity:
                best = identity.get_best_info()
                return ReasoningResult(
                    answer=best["description"],
                    confidence=1.0,
                    reasoning_type="identity",
                    steps=[
                        ReasoningStep(
                            type="identity",
                            description="Risposta diretta su identità e capacità",
                            input=question,
                            output=best,
                            channel="system",
                        )
                    ],
                    explanation="Accesso diretto alle capacità di sistema.",
                    verified=True,
                )

        # 4. Fast-Path: Calcolo matematico diretto (prima del multi-agent)
        math_ops = {
            "addition",
            "subtraction",
            "multiplication",
            "division",
            "power",
            "sqrt",
            "percentage",
            "factorial",
            "area_circle",
            "perimeter_circle",
            "area_rectangle",
            "area_triangle",
            "pythagoras",
            "volume_cube",
            "volume_sphere",
            "equation",
        }
        if parsed.intent == "calculate" or parsed.operation in math_ops:
            math_res = self.math.solve(question)
            if math_res.get("answer") is not None:
                return ReasoningResult(
                    answer=math_res.get("answer"),
                    confidence=1.0,
                    reasoning_type="math",
                    steps=[
                        ReasoningStep(
                            type="math",
                            description="Risoluzione diretta tramite MathModule",
                            input=question,
                            output=math_res,
                            channel="math_module",
                        )
                    ],
                    explanation=math_res.get("explanation", ""),
                    verified=True,
                )

        # 5. Fast-Path: Identity Handling (Sistema 1)
        if parsed.intent == "identity":
            identity = self.knowledge.get("self_identity")
            if identity:
                best = identity.get_best_info()
                return ReasoningResult(
                    answer=best["description"],
                    confidence=1.0,
                    reasoning_type="identity",
                    steps=[
                        ReasoningStep(
                            type="identity",
                            description="Identificazione rapida",
                            output=best,
                            channel="system",
                        )
                    ],
                    explanation="Accesso diretto all'identità di sistema.",
                )

        # 6. Slow-Path: Multi-Agent Orchestration (Sistema 2)
        # Il manager coordina Researcher -> Analyst -> Critic
        agent_res = self.agents.orchestrate(question, parsed_dict)

        # 7. Verifica Finale Coerenza (rinforzata oltre il Critic)
        verified = agent_res.get("status") == "approved"
        agent_steps = agent_res.get("steps", [])

        # 8. Salva nel contesto conversazione
        self.conversation_history.append(
            {
                "question": question,
                "answer": str(agent_res["answer"])
                if agent_res.get("answer") is not None
                else None,
                "confidence": agent_res.get("confidence", 0),
                "channel": channel,
            }
        )

        # 9. Generazione Spiegazione Finale
        final_explanation = self.explainer.generate(
            [s.description for s in agent_steps], {"answer": agent_res["answer"]}
        )
        if agent_res.get("feedback"):
            final_explanation += f"\n[Critica AI: {agent_res['feedback']}]"

        # 10. Fallback to LLM if agent didn't produce a useful answer
        if agent_res.get("answer") is None and use_llm and self.llm.is_available():
            llm_res = self.llm.fallback_solve(question)
            if llm_res.facts:
                best = max(llm_res.facts, key=lambda f: f.confidence)
                return ReasoningResult(
                    answer=best.value,
                    confidence=best.confidence,
                    reasoning_type="llm",
                    steps=agent_steps
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

        if agent_res.get("answer") is None:
            return ReasoningResult(
                answer=None,
                confidence=0.0,
                steps=agent_steps,
                explanation="Non ho abbastanza informazioni nei canali attuali per rispondere.",
            )

        return ReasoningResult(
            answer=agent_res["answer"],
            confidence=agent_res.get("confidence", 0.0),
            reasoning_type="multi_agent_collaboration",
            steps=agent_steps,
            explanation=final_explanation,
            verified=verified,
            sources=[],
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

    def _is_capability_question(self, raw: str, normalized: str, parsed) -> bool:
        """Riconosce domande su identità/capacità con euristiche robuste."""
        if parsed.intent == "identity":
            return True

        text = normalized
        if not text:
            return False

        # Pattern IT/EN più ampi (evita dipendenza da stringhe esatte).
        patterns = [
            r"\bchi\s+sei\b",
            r"\bdimmi\s+di\s+te\b",
            r"\b(cosa|che)\b.*\b(sai|puoi)\b.*\b(fare|aiutare)\b",
            r"\b(in\s+cosa|come)\b.*\bpuoi\b.*\b(aiutare)\b",
            r"\b(quali|che)\b.*\b(tue|tuoi)\b.*\b(capacità|capacita|funzioni|abilità|abilita)\b",
            r"\bwhat\s+can\s+you\s+do\b",
            r"\bhow\s+can\s+you\s+help\b",
            r"\btell\s+me\s+about\s+yourself\b",
        ]
        for pat in patterns:
            if re.search(pat, text):
                return True

        # Fallback euristico per domande brevi su "tu + poter/sapere + azione".
        tokens = text.split()
        if len(tokens) <= 12 and any(t in tokens for t in ["tu", "you"]):
            has_modal = any(t in tokens for t in ["puoi", "sai", "can"])
            has_action = any(
                t in tokens
                for t in [
                    "fare",
                    "aiutare",
                    "help",
                    "do",
                ]
            )
            if has_modal and has_action:
                return True

        return False

    def what_do_you_know(self) -> dict:
        """Mostra tutto ciò che l'engine ha imparato."""
        return {
            "concepts": self.knowledge.list_all(),
            "rules": self.rules.list_all(),
            "conversation_turns": len(self.conversation_history),
        }
