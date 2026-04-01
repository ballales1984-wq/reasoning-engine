"""
ReasoningEngine — Un AI che ragiona come un umano.
Il cervello principale che coordina tutti i layer.
"""

from .core.types import (
    Entity,
    ParsedQuery,
    DeductionResult,
    InductionResult,
    AnalogyResult,
    ReasoningStep,
    ReasoningResult,
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
from .llm.bridge import LLMBridge, LLMClient


class ReasoningEngine:
    """
    Il cervello principale. Coordina tutti i componenti.
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
        Ragiona su una domanda integrando le fonti.
        """
        steps = []

        # Step 1: NLP Parsing
        parsed_dict = self._parse_question(question)
        parsed = parsed_dict["_parsed"]
        parsed.channel = channel

        steps.append(
            ReasoningStep(
                type="nlp",
                description=f"Analisi query [Canale: {channel}]",
                output=parsed,
                channel=channel,
            )
        )

        # Step 2: Knowledge Lookup
        known_concepts = self.knowledge.find(parsed_dict["entities"])
        sources_used = []

        for entity, info in known_concepts.items():
            if info:
                best_info = info.get_best_info()
                steps.append(
                    ReasoningStep(
                        type="lookup",
                        description=f"Conoscenza: '{entity}' da {best_info['channel']} (fiducia {best_info['trust_score']})",
                        output=info,
                        channel=best_info["channel"],
                    )
                )
                sources_used.append(
                    SourceMetadata(
                        channel=best_info["channel"],
                        trust_score=best_info["trust_score"],
                    )
                )

        # Step 3: Reasoning Pipeline
        result_data = None

        # Step 3.0: Identity Handling
        if parsed.intent == "identity":
            identity = self.knowledge.get("self_identity")
            if identity:
                best_info = identity.get_best_info()
                result_data = {
                    "answer": best_info["description"],
                    "rule_used": "identity",
                    "confidence": 1.0,
                    "explanation": "Accesso alla base di conoscenza interna (self_identity).",
                }
                steps.append(
                    ReasoningStep(
                        type="identity",
                        description="Identificazione dell'engine",
                        output=result_data,
                        channel="system",
                    )
                )

        # Step 3.1: Financial Data (if intent or ticker detected)
        if result_data is None and (
            parsed.intent == "finance"
            or any(e.name.isupper() and len(e.name) <= 5 for e in parsed.entities)
        ):
            # Cerca ticker tra le entità
            tickers = [
                e.name for e in parsed.entities if e.name.isupper() and len(e.name) <= 5
            ]
            if tickers:
                ticker = tickers[0]
                finance_res = self.finance_data.get_stock_price(ticker)
                if finance_res["success"]:
                    result_data = {
                        "answer": f"Il prezzo attuale di {ticker} è {finance_res['price']} {finance_res['currency']}.",
                        "rule_used": "financial_market_api",
                        "confidence": 0.95,
                        "explanation": f"Dati recuperati in tempo reale tramite Canale: {self.finance_data.channel_name}",
                    }
                    steps.append(
                        ReasoningStep(
                            type="financial",
                            description=f"Recupero dati mercato per {ticker}",
                            output=finance_res,
                            channel=self.finance_data.channel_name,
                        )
                    )

        # Try Rule Engine (Base)
        if result_data is None:
            base_result = self.rules.apply(parsed_dict, known_concepts)
            if base_result:
                result_data = base_result
                steps.append(
                    ReasoningStep(
                        type="rule_engine",
                        description="Applicata regola base logica",
                        output=base_result,
                    )
                )

        # Try Math (if needed)
        if result_data is None and parsed.operation != "unknown":
            math_res = self.math.solve(question)
            if math_res and math_res.get("answer") is not None:
                result_data = {
                    "answer": math_res["answer"],
                    "rule_used": "math",
                    "confidence": 1.0,
                    "explanation": math_res.get("explanation", ""),
                }
                steps.append(
                    ReasoningStep(
                        type="math",
                        description="Risolto con modulo matematico",
                        output=math_res,
                    )
                )

        # ... (Deductive, Inductive logic remains same but uses channels if available)
        if result_data is None and parsed.intent == "verify":
            entities = parsed_dict.get("entities", [])
            if entities:
                ded_result = self.deductive.deduce(entities[0])
                if ded_result.found:
                    result_data = {
                        "answer": ded_result.conclusion,
                        "rule_used": "deductive",
                        "confidence": ded_result.confidence,
                        "explanation": ded_result.explanation,
                    }
                    steps.append(
                        ReasoningStep(
                            type="deduction",
                            description="Deduzione logica completata",
                            output=ded_result,
                        )
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
