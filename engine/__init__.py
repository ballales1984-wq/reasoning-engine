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
from .llm_bridge import LLMBridge, LLMClient, LLMResponse, ExtractedFact
from .persistence import Persistence


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
    
    def __init__(self, llm_api_key: str = None, llm_model: str = "gpt-4o-mini"):
        self.knowledge = KnowledgeGraph()
        self.rules = RuleEngine()
        self.learner = Learner(self.knowledge)
        self.verifier = Verifier(self.rules)
        self.explainer = Explainer()
        self.math = MathModule(self.rules, self.knowledge)
        self.deductive = DeductiveReasoner(self.knowledge, self.rules)
        self.inductive = InductiveReasoner(self.knowledge, self.rules)
        self.analogical = AnalogicalReasoner(self.knowledge)

        # LLM Bridge (opzionale)
        llm_client = LLMClient(model=llm_model, api_key=llm_api_key)
        self.llm = LLMBridge(llm_client, self.knowledge, self.verifier)
    
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
        
        # Step 3b: Ragionamento deduttivo (solo verify, non define)
        if result is None and parsed.get("intent") == "verify":
            entities = parsed.get("entities", [])
            parsed_relations = parsed.get("relations", [])
            
            # Prova prima con le relazioni estratte dal parser
            deduction_target = None
            if parsed_relations:
                subj, rel, obj = parsed_relations[0]
                # Per "X ha Y" → cerca "ha_Y" come proprietà nella gerarchia
                if rel == "ha_caratteristica":
                    deduction_target = f"ha_{obj}"
                elif rel == "ha_caratteristica_si":
                    deduction_target = f"si_{obj}"
                else:
                    deduction_target = obj
                # Rimuovi articoli dal soggetto
                import re
                subj = re.sub(r'^(il|la|i|le|lo|un|una)\s+', '', subj)
                entities = [subj] + [e for e in entities if e != subj]
            
            # Se abbiamo 2 entità o un target, deduci la relazione
            if deduction_target and entities:
                deduction = self.deductive.deduce(entities[0], deduction_target)
                if deduction.found:
                    if parsed_relations and parsed_relations[0][1] == "ha_caratteristica":
                        answer_text = f"Sì, {entities[0]} ha {parsed_relations[0][2]}"
                    else:
                        answer_text = f"Sì, {entities[0]} → {deduction_target}"
                    result = {
                        "answer": answer_text,
                        "rule_used": "deduction",
                        "confidence": deduction.confidence,
                        "explanation": f"Deduzione: {answer_text} ({deduction.steps_count} passi)"
                    }
                    steps.append(f"🔍 Deduzione: {entities[0]} → {deduction_target}")
                    for step in deduction.chain:
                        steps.append(f"   → {step.rule_type}: {step.conclusion}")
                else:
                    # Prova anche con il nome semplice (senza "ha_")
                    deduction = self.deductive.deduce(entities[0], deduction_target.replace("ha_", ""))
                    if deduction.found:
                        result = {
                            "answer": f"Sì, {entities[0]} → {deduction_target}",
                            "rule_used": "deduction",
                            "confidence": deduction.confidence,
                            "explanation": f"Deduzione: {entities[0]} → {deduction_target} ({deduction.steps_count} passi)"
                        }
                        steps.append(f"🔍 Deduzione: {entities[0]} → {deduction_target}")
                        for step in deduction.chain:
                            steps.append(f"   → {step.rule_type}: {step.conclusion}")
                    else:
                        result = {
                            "answer": f"No, non posso dedurre che {entities[0]} ha {parsed_relations[0][2] if parsed_relations else deduction_target}",
                            "rule_used": "deduction",
                            "confidence": 0.5,
                            "explanation": f"Non riesco a dedurre"
                        }
                        steps.append(f"❌ Non riesco a dedurre: {entities[0]} → {deduction_target}")
            elif len(entities) >= 2:
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
                        "explanation": f"Non riesco a dedurre"
                    }
                    steps.append(f"❌ Non riesco a dedurre: {entities[0]} → {entities[1]}")
        
        # Step 3b2: Define intent — lookup nel KG, poi LLM
        if result is None and parsed.get("intent") == "define":
            entities = parsed.get("entities", [])
            # Rimuovi token di parsing spurii
            real_entities = [e for e in entities if e not in ("cosa", "cos", "definisci", "che", "significato")]
            if real_entities:
                concept = real_entities[0]
                known = self.knowledge.get(concept)
                if known and known.description:
                    result = {
                        "answer": known.description,
                        "rule_used": "lookup",
                        "confidence": 0.95,
                        "explanation": f"{concept}: {known.description}"
                    }
                    steps.append(f"🧠 Trovato nel KG: {concept} = {known.description}")
                elif use_llm and self.llm.is_available():
                    llm_response = self.llm.provide_knowledge(concept)
                    if llm_response.facts:
                        for fact in llm_response.facts:
                            if fact.relation == "descrizione":
                                self.knowledge.add(concept, description=fact.value)
                            elif fact.relation == "categoria":
                                if concept in self.knowledge.concepts:
                                    self.knowledge.concepts[concept].category = fact.value
                            elif fact.relation == "ha_esempio":
                                if concept in self.knowledge.concepts:
                                    self.knowledge.concepts[concept].examples.append(fact.value)
                            else:
                                self.knowledge.connect(concept, fact.relation, fact.value)
                        known_now = self.knowledge.get(concept)
                        result = {
                            "answer": known_now.description if known_now else str(llm_response.facts[0].value),
                            "rule_used": "llm_knowledge",
                            "confidence": llm_response.confidence * 0.8,
                            "explanation": f"Appreso dall'LLM ({len(llm_response.facts)} fatti)"
                        }
                        steps.append(f"📚 LLM ha insegnato: {concept} ({len(llm_response.facts)} fatti)")
                elif use_llm:
                    steps.append("⚠️ LLM non configurato")
        
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
        if use_llm and self.llm.is_available():
            steps.append("🤖 Chiedo all'LLM...")

            # Prima: prova a far imparare il concetto
            entities = parsed.get("entities", [])
            if entities and parsed.get("intent") in ("define", "explain", "general"):
                llm_response = self.llm.provide_knowledge(entities[0])
                if llm_response.facts:
                    # Aggiungi al knowledge graph
                    for fact in llm_response.facts:
                        if fact.relation == "descrizione":
                            self.knowledge.add(entities[0], description=fact.value)
                        elif fact.relation == "categoria":
                            if entities[0] in self.knowledge.concepts:
                                self.knowledge.concepts[entities[0]].category = fact.value
                        elif fact.relation == "ha_esempio":
                            if entities[0] in self.knowledge.concepts:
                                self.knowledge.concepts[entities[0]].examples.append(fact.value)
                        else:
                            self.knowledge.connect(entities[0], fact.relation, fact.value)

                    steps.append(f"📚 Ho imparato da LLM: {len(llm_response.facts)} fatti su '{entities[0]}'")

                    # Prova di nuovo a rispondere con la nuova conoscenza
                    known = self.knowledge.get(entities[0])
                    if known and known.description:
                        result = {
                            "answer": known.description,
                            "rule_used": "llm_knowledge",
                            "confidence": llm_response.confidence * 0.8,
                            "explanation": f"Risposta basata su conoscenza LLM (verificata: {llm_response.verified})"
                        }

            # Se ancora niente, fallback solver
            if result is None:
                context = {
                    "known_concepts": list(known_concepts.keys()) if known_concepts else [],
                    "steps": steps
                }
                llm_response = self.llm.fallback_solve(question, context)
                if llm_response.facts:
                    best_fact = max(llm_response.facts, key=lambda f: f.confidence)
                    result = {
                        "answer": best_fact.value,
                        "rule_used": "llm_fallback",
                        "confidence": best_fact.confidence * 0.7,
                        "explanation": f"Risposta LLM (non verificata internamente)"
                    }
                    steps.append(f"🤖 LLM risponde: {best_fact.value}")
        elif use_llm:
            steps.append("⚠️ LLM non configurato — impossibile fare fallback")

        if result is None:
            return {
                "answer": None,
                "steps": steps,
                "confidence": 0.0,
                "explanation": "Non riesco a risolvere questo problema con le regole che conosco.",
                "verified": False,
                "llm_used": False
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

    def save(self, name: str = "default", directory: str = None) -> str:
        """Salva lo stato dell'engine su disco."""
        p = Persistence(directory)
        return p.save_engine(self, name)

    def load(self, name: str = "default", directory: str = None) -> bool:
        """Carica lo stato dell'engine da disco."""
        p = Persistence(directory)
        return p.load_engine(self, name)

    def export_text(self) -> str:
        """Esporta lo stato come testo leggibile."""
        p = Persistence()
        return p.export_text(self)
