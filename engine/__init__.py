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
        
        # Step 3: Prova a risolvere con le regole
        result = self.rules.apply(parsed, known_concepts)
        
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
        Analizza la domanda per capire:
        - intent: cosa vuole sapere (calcolo, definizione, etc.)
        - entities: gli oggetti coinvolti (numeri, concetti)
        - operation: l'operazione richiesta
        """
        question = question.strip().lower()
        
        # Rileva operazioni matematiche
        if "quanto fa" in question or "calcola" in question:
            # Estrai numeri e operazione
            import re
            numbers = [int(x) for x in re.findall(r'\d+', question)]
            
            if "+" in question or "più" in question or "somma" in question:
                return {
                    "intent": "calcolo",
                    "operation": "addition",
                    "entities": [str(n) for n in numbers],
                    "numbers": numbers
                }
            elif "-" in question or "meno" in question:
                return {
                    "intent": "calcolo",
                    "operation": "subtraction",
                    "entities": [str(n) for n in numbers],
                    "numbers": numbers
                }
            elif "×" in question or "per" in question and "volte" in question:
                return {
                    "intent": "calcolo",
                    "operation": "multiplication",
                    "entities": [str(n) for n in numbers],
                    "numbers": numbers
                }
            elif "÷" in question or "diviso" in question:
                return {
                    "intent": "calcolo",
                    "operation": "division",
                    "entities": [str(n) for n in numbers],
                    "numbers": numbers
                }
            
            return {
                "intent": "calcolo",
                "operation": "unknown",
                "entities": [str(n) for n in numbers],
                "numbers": numbers
            }
        
        # Rileva definizioni
        if "cosa è" in question or "cos'è" in question or "definisci" in question:
            import re
            # Estrai la parola dopo "cosa è"
            match = re.search(r"cos['']è\s+(\w+)|cosa\s+è\s+(\w+)|definisci\s+(\w+)", question)
            concept = match.group(1) or match.group(2) or match.group(3) if match else question
            return {
                "intent": "definizione",
                "operation": "lookup",
                "entities": [concept],
                "numbers": []
            }
        
        # Default
        return {
            "intent": "sconosciuto",
            "operation": "unknown",
            "entities": question.split(),
            "numbers": []
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
