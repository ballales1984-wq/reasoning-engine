"""
ReasoningEngine — Un AI che ragiona come un umano.

Idea di Alessio Gnappo:
Invece di usare pattern statistici (come gli LLM),
questo engine costruisce comprensione step-by-step,
come fa un bambino quando impara.
"""

from .knowledge_graph import KnowledgeGraph
from .rule_engine import RuleEngine
from .learner import Learner
from .verifier import Verifier
from .explainer import Explainer
from .math_module import MathModule
from .nlp_parser import parse, ParsedQuery, Entity
from .deductive import DeductiveReasoner, DeductionResult
from .inductive import InductiveReasoner, InductionResult
from .analogical import AnalogicalReasoner, AnalogyResult


class ReasoningEngine:
    """
    Il cervello principale. Coordina tutti i componenti.
    
    Flusso:
    1. Riceve una domanda
    2. Cerca concetti noti nel Knowledge Graph
    3. Applica regole dal Rule Engine
    4. Se non sa, chiede all'LLM (opzionale)
    5. Verifica la risposta
    6. Spiega il ragionamento
    """
    
    def __init__(self):
        self.knowledge = KnowledgeGraph()
        self.rules = RuleEngine()
        self.learner = Learner(self.knowledge)
        self.verifier = Verifier(self.rules)
        self.explainer = Explainer()
        self.math = MathModule(self.rules, self.knowledge)
        self.deductive = DeductiveReasoner(self.knowledge, self.rules)
        self.inductive = InductiveReasoner(self.knowledge, self.rules)
        self.analogical = AnalogicalReasoner(self.knowledge)
    
    def learn(self, concept: str, examples: list[str], 
              description: str = None, category: str = "general"):
        """
        Insegna un concetto all'engine attraverso esempi.
        
        engine.learn("6", 
            examples=["🍎🍎🍎🍎🍎🍎", "6 cose", "5+1"],
            description="il numero sei, una quantità",
            category="math/numbers")
        """
        self.learner.add_concept(concept, examples, description, category)
        return f"Ho imparato: {concept}"
    
    def learn_rule(self, name: str, func, description: str = "",
                   inputs: list[str] = None, output_type: str = "any"):
        """
        Insegna una regola all'engine.
        
        engine.learn_rule("addition", 
            lambda a, b: a + b,
            description="somma due numeri",
            inputs=["number", "number"],
            output_type="number")
        """
        self.rules.add_rule(name, func, description, inputs, output_type)
        return f"Regola aggiunta: {name}"
    
    def reason(self, question: str, use_llm: bool = False) -> dict:
        """
        Ragiona su una domanda e restituisce:
        - answer: la risposta
        - steps: i passaggi del ragionamento
        - confidence: quanto è sicuro (0-1)
        - explanation: spiegazione testuale
        """
        steps = []
        
        # Step 1: Analizza la domanda
        parsed = self._parse_question(question)
        steps.append(f"📝 Ho capito che stai chiedendo: {parsed['intent']}")
        
        # Step 2: Cerca concetti noti
        known_concepts = self.knowledge.find(parsed['entities'])
        for entity, info in known_concepts.items():
            if info:
                steps.append(f"🧠 So che '{entity}' = {info.description}")
            else:
                steps.append(f"❓ Non conosco '{entity}' — devo impararlo")
        
        # Step 3: Prova a risolvere con le regole base
        result = self.rules.apply(parsed, known_concepts)
        
        # Se le regole base non bastano, prova il MathModule
        if result is None and parsed.get("operation") not in ("unknown", "lookup"):
            math_result = self.math.solve(question)
            if math_result and math_result.get("answer") is not None:
                result = {
                    "answer": math_result["answer"],
                    "rule_used": parsed.get("operation", "math"),
                    "confidence": 1.0,
                    "explanation": math_result.get("explanation", "")
                }
        
        # Step 3b: Ragionamento deduttivo (se verify o define)
        if result is None and parsed.get("intent") in ("verify", "define"):
            entities = parsed.get("entities", [])
            # Se abbiamo 2 entità, deduci la relazione tra loro
            if len(entities) >= 2:
                deduction = self.deductive.deduce(entities[0], entities[1])
                if deduction.found:
                    result = {
                        "answer": f"Sì, {entities[0]} → {entities[1]}",
                        "rule_used": "deduction",
                        "confidence": deduction.confidence,
                        "explanation": f"Deduzione: {entities[0]} → {entities[1]} ({deduction.steps_count} passi)"
                    }
                    steps.append(f"🔍 Deduzione: {entities[0]} → {entities[1]}")
                    for step in deduction.chain:
                        steps.append(f"   → {step.rule_type}: {step.conclusion}")
                else:
                    result = {
                        "answer": f"No, non posso dedurre che {entities[0]} → {entities[1]}",
                        "rule_used": "deduction",
                        "confidence": 0.5,
                        "explanation": f"Non riesco a dedurre {entities[0]} → {entities[1]}"
                    }
                    steps.append(f"❌ Non riesco a dedurre: {entities[0]} → {entities[1]}")
            elif len(entities) == 1:
                deduction = self.deductive.deduce(entities[0])
                if deduction.found:
                    result = {
                        "answer": deduction.conclusion,
                        "rule_used": "deduction",
                        "confidence": deduction.confidence,
                        "explanation": f"Deduzione: {deduction.conclusion} ({deduction.steps_count} passi)"
                    }
                    steps.append(f"🔍 Deduzione: {deduction.conclusion}")
                    for step in deduction.chain:
                        steps.append(f"   → {step.rule_type}: {step.conclusion}")
        
        # Step 3c: Analogia (se explain e non ha trovato risposta)
        if result is None and parsed.get("intent") == "explain":
            entities = parsed.get("entities", [])
            for entity in entities:
                analogy_result = self.analogical.find_analogies(entity, max_results=1)
                if analogy_result.found and analogy_result.best_analogy:
                    best = analogy_result.best_analogy
                    result = {
                        "answer": f"{entity} è come {best.target}",
                        "rule_used": "analogy",
                        "confidence": best.structural_similarity * 0.8,
                        "explanation": analogy_result.explanation
                    }
                    steps.append(f"🔄 Analogia: {entity} ↔ {best.target}")
                    break
        
        if result is not None:
            steps.append(f"⚙️ Ho applicato la regola: {result['rule_used']}")
            steps.append(f"✅ Risultato: {result['answer']}")
            
            # Step 4: Verifica
            is_valid = self.verifier.check(result, parsed)
            if is_valid:
                steps.append("✔️ Verifica superata")
            else:
                steps.append("⚠️ Verifica fallita — potrebbe essere sbagliato")
            
            # Step 5: Genera spiegazione
            explanation = self.explainer.generate(steps, result)
            
            return {
                "answer": result["answer"],
                "steps": steps,
                "confidence": result.get("confidence", 0.9),
                "explanation": explanation,
                "verified": is_valid
            }
        
        # Se non riesce da solo, può chiedere all'LLM
        if use_llm:
            steps.append("🤖 Chiedo all'LLM...")
            # TODO: integrare LLM come fallback
            steps.append("⚠️ LLM non ancora integrato")
        
        return {
            "answer": None,
            "steps": steps,
            "confidence": 0.0,
            "explanation": "Non riesco a risolvere questo problema con le regole che conosco.",
            "verified": False
        }
    
    def _parse_question(self, question: str) -> dict:
        """
        Analizza la domanda usando il NLP Parser.
        """
        parsed = parse(question)
        
        return {
            "intent": parsed.intent,
            "operation": parsed.operation,
            "entities": [e.name for e in parsed.entities],
            "numbers": parsed.nlp_numbers if hasattr(parsed, 'nlp_numbers') else parsed.numbers,
            "operators": parsed.operators,
            "relations": parsed.relations,
            "confidence": parsed.confidence,
            "_parsed": parsed  # Mantiene l'oggetto completo per usi futuri
        }
    
    def explain_concept(self, concept: str) -> str:
        """Spiega un concetto che l'engine conosce."""
        info = self.knowledge.get(concept)
        if info:
            return self.explainer.explain_concept(info)
        return f"Non conosco il concetto '{concept}'. Insegnamelo!"
    
    def what_do_you_know(self) -> dict:
        """Mostra tutto ciò che l'engine ha imparato."""
        return {
            "concepts": self.knowledge.list_all(),
            "rules": self.rules.list_all(),
            "stats": {
                "total_concepts": len(self.knowledge.list_all()),
                "total_rules": len(self.rules.list_all())
            }
        }

    def deduce(self, subject: str, target: str = None) -> dict:
        """Ragionamento deduttivo diretto."""
        return self.deductive.deduce(subject, target)

    def induce(self, examples: list[str]) -> dict:
        """Ragionamento induttivo da esempi."""
        return self.inductive.induce_from_examples(examples)

    def find_analogies(self, concept: str) -> dict:
        """Trova analogie per un concetto."""
        return self.analogical.find_analogies(concept)

    def explain_analogy(self, source: str, target: str) -> str:
        """Spiega l'analogia tra due concetti."""
        return self.analogical.explain_analogy(source, target)
