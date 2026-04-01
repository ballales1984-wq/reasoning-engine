"""
ReasoningEngine — Un AI che ragiona come un umano.
Il cervello principale che coordina tutti i layer.
"""

from .core.types import (
    Entity, ParsedQuery, DeductionResult, InductionResult, 
    AnalogyResult, ReasoningStep, ReasoningResult
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
from .llm.bridge import LLMBridge, LLMClient

class ReasoningEngine:
    """
    Il cervello principale. Coordina tutti i componenti.
    """
    
    def __init__(self, llm_api_key: str = None, llm_model: str = "gpt-4o-mini"):
        self.knowledge = KnowledgeGraph()
        self.rules = RuleEngine()
        self.learner = Learner(self.knowledge)
        self.verifier = Verifier(self.rules)
        self.explainer = Explainer()
        self.math = MathModule(self.knowledge, self.rules)
        self.deductive = DeductiveReasoner(self.knowledge, self.rules)
        self.inductive = InductiveReasoner(self.knowledge, self.rules)
        self.analogical = AnalogicalReasoner(self.knowledge)

        # LLM Bridge
        llm_client = LLMClient(model=llm_model, api_key=llm_api_key)
        self.llm = LLMBridge(llm_client, self.knowledge, self.verifier)
    
    def learn(self, concept: str, examples: list[str], 
              description: str = None, category: str = "general"):
        """Insegna un concetto all'engine."""
        self.learner.add_concept(concept, examples, description, category)
        return f"Ho imparato: {concept}"
    
    def learn_rule(self, name: str, func, description: str = "",
                   inputs: list[str] = None, output_type: str = "any"):
        """Insegna una regola all'engine."""
        self.rules.add_rule(name, func, description, inputs, output_type)
        return f"Regola aggiunta: {name}"
    
    def reason(self, question: str, use_llm: bool = False) -> ReasoningResult:
        """
        Ragiona su una domanda.
        """
        steps = []
        
        # Step 1: NLP Parsing
        parsed_dict = self._parse_question(question)
        parsed = parsed_dict["_parsed"]
        steps.append(ReasoningStep(
            type="nlp", 
            description=f"Ho capito che stai chiedendo: {parsed.intent}",
            output=parsed
        ))
        
        # Step 2: Knowledge Lookup
        known_concepts = self.knowledge.find(parsed_dict['entities'])
        for entity, info in known_concepts.items():
            if info:
                steps.append(ReasoningStep(
                    type="lookup",
                    description=f"So che '{entity}' = {info.description}",
                    output=info
                ))
        
        # Step 3: Reasoning Pipeline
        result_data = None
        
        # Try Rule Engine (Base)
        base_result = self.rules.apply(parsed_dict, known_concepts)
        if base_result:
            result_data = base_result
            steps.append(ReasoningStep(
                type="rule_engine",
                description="Applicata regola base",
                output=base_result
            ))

        # Try Math (if needed)
        if result_data is None and parsed.operation != "unknown":
            math_res = self.math.solve(question)
            if math_res and math_res.get("answer") is not None:
                result_data = {
                    "answer": math_res["answer"],
                    "rule_used": "math",
                    "confidence": 1.0,
                    "explanation": math_res.get("explanation", "")
                }
                steps.append(ReasoningStep(
                    type="math",
                    description="Risolto con modulo matematico",
                    output=math_res
                ))

        # Step 4: Verification
        verified = False
        if result_data:
            verified = self.verifier.check(result_data, parsed_dict)
            steps.append(ReasoningStep(
                type="verification",
                description="Verifica del risultato",
                output=verified
            ))

        # Step 5: Final Response Generation
        if result_data:
            final_explanation = self.explainer.generate([s.description for s in steps], result_data)
            return ReasoningResult(
                answer=result_data["answer"],
                confidence=result_data.get("confidence", 0.9),
                reasoning_type=result_data.get("rule_used", "deductive"),
                steps=steps,
                explanation=final_explanation,
                verified=verified
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
                    steps=steps + [ReasoningStep(type="llm", description="Risposta da LLM")],
                    explanation="Ottenuto tramite LLM Bridge",
                    llm_used=True
                )

        return ReasoningResult(
            answer=None,
            confidence=0.0,
            steps=steps,
            explanation="Non riesco a rispondere con le conoscenze attuali."
        )

    def _parse_question(self, question: str) -> dict:
        """Analisi NLP."""
        parsed = parse(question)
        return {
            "intent": parsed.intent,
            "operation": parsed.operation,
            "entities": [e.name for e in parsed.entities],
            "numbers": parsed.numbers,
            "operators": parsed.operators,
            "relations": parsed.relations,
            "confidence": parsed.confidence,
            "_parsed": parsed
        }
