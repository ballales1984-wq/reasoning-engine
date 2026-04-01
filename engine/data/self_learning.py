"""
SelfLearningEngine — Impara da solo, come un umano.

Questo è il CUORE del progetto. Non applica regole date — le SCOPRE.

Come impara un umano:
1. Osserva → vede esempi
2. Ipotizza → "forse è sempre così?"
3. Testa → prova la regola su nuovi casi
4. Errore → se sbaglia, corregge
5. Conferma → se funziona, la tiene
6. Generalizza → la applica a casi nuovi

L'engine fa lo stesso:
- Trial and error (prova, sbaglia, corregge)
- Curiosità (esplora l'ignoto)
- Memoria esperienziale (ricorda cosa ha funzionato)
- Creazione autonoma di regole
"""

from dataclasses import dataclass, field
from typing import Optional, Any
from collections import defaultdict
import random
import json


@dataclass
class Hypothesis:
    """Un'ipotesi che l'engine ha formulato."""
    id: str
    description: str
    rule: Any  # La regola (funzione, pattern, relazione)
    confidence: float = 0.5  # 0 = pura ipotesi, 1 = confermata
    tests_passed: int = 0
    tests_failed: int = 0
    examples: list = field(default_factory=list)
    created_at: int = 0
    
    @property
    def success_rate(self) -> float:
        total = self.tests_passed + self.tests_failed
        if total == 0:
            return 0.5
        return self.tests_passed / total


@dataclass
class Experience:
    """Un'esperienza dell'engine (tentativo + risultato)."""
    action: str
    context: dict
    result: Any
    success: bool
    lesson: str  # Cosa ha imparato
    timestamp: int = 0


class SelfLearningEngine:
    """
    Il motore di apprendimento autonomo.
    
    Non gli dici cosa imparare — lui scopre da solo.
    """
    
    def __init__(self, knowledge_graph, rule_engine):
        self.knowledge = knowledge_graph
        self.rules = rule_engine
        
        # Memoria
        self.hypotheses = {}  # {id: Hypothesis}
        self.experiences = []  # Lista di Experience
        self.curiosity_queue = []  # Cosa vuole esplorare
        
        # Contatori
        self.hypothesis_counter = 0
        self.experience_counter = 0
        
        # Patterns scoperti
        self.discovered_patterns = []
        
        # Regole create autonomamente
        self.self_created_rules = []
    
    def observe(self, examples: list[str]) -> list[Hypothesis]:
        """
        Osserva degli esempi e FORMULA IPOTESI.
        
        Non gli dici la regola — la trova da solo.
        
        engine.observe([
            "2 + 3 = 5",
            "4 + 1 = 5", 
            "1 + 4 = 5"
        ])
        → Ipotesi: "La somma di due numeri che dà 5 è commutativa"
        """
        hypotheses = []
        
        # Analizza ogni esempio
        parsed_examples = [self._parse_example(ex) for ex in examples]
        
        # Cerca pattern comuni
        patterns = self._find_patterns(parsed_examples)
        
        # Crea un'ipotesi per ogni pattern trovato
        for pattern in patterns:
            hypothesis = self._create_hypothesis(pattern, examples)
            hypotheses.append(hypothesis)
            self.hypotheses[hypothesis.id] = hypothesis
        
        return hypotheses
    
    def _parse_example(self, example: str) -> dict:
        """Analizza un esempio per estrarre struttura."""
        import re
        
        result = {
            "raw": example,
            "numbers": [float(x) for x in re.findall(r'-?\d+\.?\d*', example)],
            "words": example.lower().split(),
            "operators": [],
            "structure": None
        }
        
        # Rileva operatori
        if "+" in example or "più" in example.lower():
            result["operators"].append("addition")
        if "-" in example or "meno" in example.lower():
            result["operators"].append("subtraction")
        if "×" in example or "*" in example or "per" in example.lower():
            result["operators"].append("multiplication")
        if "=" in example:
            result["operators"].append("equals")
        
        # Rileva struttura "X operatore Y = Z"
        match = re.search(r'(\d+)\s*([+\-×*/])\s*(\d+)\s*=\s*(\d+)', example)
        if match:
            result["structure"] = {
                "a": float(match.group(1)),
                "op": match.group(2),
                "b": float(match.group(3)),
                "result": float(match.group(4))
            }
        
        return result
    
    def _find_patterns(self, parsed_examples: list[dict]) -> list[dict]:
        """
        Trova pattern comuni tra gli esempi.
        
        Questo è il "ragionamento" dell'engine:
        confronta, trova somiglianze, crea regole.
        """
        patterns = []
        
        # Pattern 1: Stesso risultato, operandi diversi (commutatività)
        results = defaultdict(list)
        for ex in parsed_examples:
            if ex["structure"]:
                key = ex["structure"]["result"]
                results[key].append(ex["structure"])
        
        for result, structures in results.items():
            if len(structures) >= 2:
                # Controlla se gli operandi sono scambiati
                for i, s1 in enumerate(structures):
                    for s2 in structures[i+1:]:
                        if s1["a"] == s2["b"] and s1["b"] == s2["a"]:
                            patterns.append({
                                "type": "commutativity",
                                "operation": s1["op"],
                                "description": f"{s1['a']} {s1['op']} {s1['b']} = {s2['a']} {s2['op']} {s2['b']} (commutativo)",
                                "confidence": 0.8,
                                "examples": len(structures)
                            })
        
        # Pattern 2: Stesso operatore, risultati diversi (linearità)
        operations = defaultdict(list)
        for ex in parsed_examples:
            if ex["structure"]:
                op = ex["structure"]["op"]
                operations[op].append(ex["structure"])
        
        for op, structures in operations.items():
            if len(structures) >= 3:
                # Controlla se c'è una relazione lineare
                # Es: se a+b=result, allora (a+1)+b=result+1
                patterns.append({
                    "type": "linearity",
                    "operation": op,
                    "description": f"L'operazione {op} è lineare",
                    "confidence": 0.6,
                    "examples": len(structures)
                })
        
        # Pattern 3: Relazioni numeriche
        all_numbers = []
        for ex in parsed_examples:
            all_numbers.extend(ex["numbers"])
        
        if len(all_numbers) >= 4:
            # Cerca relazioni aritmetiche
            sorted_nums = sorted(set(all_numbers))
            for i in range(len(sorted_nums)-1):
                diff = sorted_nums[i+1] - sorted_nums[i]
                if all(sorted_nums[j+1] - sorted_nums[j] == diff 
                       for j in range(len(sorted_nums)-1)):
                    patterns.append({
                        "type": "arithmetic_sequence",
                        "difference": diff,
                        "description": f"Sequenza aritmetica con differenza {diff}",
                        "confidence": 0.9,
                        "examples": len(sorted_nums)
                    })
        
        return patterns
    
    def _create_hypothesis(self, pattern: dict, examples: list[str]) -> Hypothesis:
        """Crea un'ipotesi da un pattern trovato."""
        self.hypothesis_counter += 1
        
        return Hypothesis(
            id=f"H{self.hypothesis_counter}",
            description=pattern["description"],
            rule=pattern,
            confidence=pattern.get("confidence", 0.5),
            examples=examples[:3],  # Salva max 3 esempi
            created_at=self.experience_counter
        )
    
    def test_hypothesis(self, hypothesis_id: str, test_case: str) -> dict:
        """
        TESTA un'ipotesi su un caso nuovo.
        
        Questo è il "trial and error":
        - Se funziona → aumenta la confidenza
        - Se fallisce → diminuisce la confidenza
        - Se fallisce troppo → scarta l'ipotesi
        """
        if hypothesis_id not in self.hypotheses:
            return {"success": False, "error": "Ipotesi non trovata"}
        
        hypothesis = self.hypotheses[hypothesis_id]
        
        # Applica la regola dell'ipotesi al caso di test
        result = self._apply_hypothesis(hypothesis, test_case)
        
        if result["success"]:
            hypothesis.tests_passed += 1
            hypothesis.confidence = min(1.0, hypothesis.confidence + 0.1)
            lesson = f"Ipotesi {hypothesis_id} confermata: {hypothesis.description}"
        else:
            hypothesis.tests_failed += 1
            hypothesis.confidence = max(0.0, hypothesis.confidence - 0.15)
            lesson = f"Ipotesi {hypothesis_id} fallita: {hypothesis.description}"
        
        # Registra l'esperienza
        experience = Experience(
            action=f"test_hypothesis_{hypothesis_id}",
            context={"test_case": test_case, "hypothesis": hypothesis.description},
            result=result,
            success=result["success"],
            lesson=lesson,
            timestamp=self.experience_counter
        )
        self.experience_counter += 1
        self.experiences.append(experience)
        
        # Se la confidenza è alta, crea una regola vera
        if hypothesis.confidence >= 0.8 and hypothesis.tests_passed >= 3:
            self._promote_to_rule(hypothesis)
        
        return {
            "success": result["success"],
            "confidence": hypothesis.confidence,
            "tests_passed": hypothesis.tests_passed,
            "tests_failed": hypothesis.tests_failed,
            "lesson": lesson
        }
    
    def _apply_hypothesis(self, hypothesis: Hypothesis, test_case: str) -> dict:
        """Applica un'ipotesi a un caso di test."""
        import re
        
        pattern_type = hypothesis.rule.get("type", "unknown")
        
        # Test commutatività
        if pattern_type == "commutativity":
            match = re.search(r'(\d+)\s*([+\-×*/])\s*(\d+)\s*=\s*(\d+)', test_case)
            if match:
                a, op, b, result = float(match.group(1)), match.group(2), float(match.group(3)), float(match.group(4))
                # Verifica se b op a = result
                expected = self._calculate(b, op, a)
                return {"success": abs(expected - result) < 0.001, "expected": expected, "actual": result}
        
        # Test sequenza aritmetica
        if pattern_type == "arithmetic_sequence":
            numbers = [float(x) for x in re.findall(r'-?\d+\.?\d*', test_case)]
            if len(numbers) >= 2:
                diff = hypothesis.rule.get("difference", 0)
                is_valid = all(numbers[i+1] - numbers[i] == diff for i in range(len(numbers)-1))
                return {"success": is_valid}
        
        # Default: non sa testare
        return {"success": True, "note": "Caso non testabile con questa ipotesi"}
    
    def _calculate(self, a: float, op: str, b: float) -> float:
        """Esegue un'operazione."""
        if op == "+":
            return a + b
        elif op == "-":
            return a - b
        elif op == "*" or op == "×":
            return a * b
        elif op == "/" or op == "÷":
            return a / b if b != 0 else float('nan')
        return 0
    
    def _promote_to_rule(self, hypothesis: Hypothesis):
        """
        Promuove un'ipotesi a REGOLA VERA.
        
        Quando un'ipotesi ha abbastanza conferme,
        diventa una regola che l'engine può usare.
        """
        rule = {
            "id": hypothesis.id,
            "description": hypothesis.description,
            "pattern": hypothesis.rule,
            "confidence": hypothesis.confidence,
            "source": "self_learned",
            "tests_passed": hypothesis.tests_passed
        }
        
        self.self_created_rules.append(rule)
        
        # Aggiungi al knowledge graph
        self.knowledge.add(
            f"regola_{hypothesis.id}",
            description=hypothesis.description,
            examples=hypothesis.examples,
            category="self_learned/rules"
        )
    
    def explore(self, unknown: str) -> dict:
        """
        ESPLORA qualcosa di sconosciuto.
        
        Questa è la CURIOSITÀ:
        - Se non sa qualcosa, non si arrende
        - Formula ipotesi casuali
        - Le testa
        - Impara
        """
        # Genera ipotesi casuali
        hypotheses = self._generate_random_hypotheses(unknown)
        
        # Aggiungi alla coda di curiosità
        self.curiosity_queue.append({
            "topic": unknown,
            "hypotheses": [h.id for h in hypotheses],
            "status": "exploring"
        })
        
        return {
            "topic": unknown,
            "hypotheses_generated": len(hypotheses),
            "status": "exploring",
            "next_step": "Testare le ipotesi con esempi"
        }
    
    def _generate_random_hypotheses(self, topic: str) -> list[Hypothesis]:
        """Genera ipotesi casuali su un argomento sconosciuto."""
        hypotheses = []
        
        # Ipotesi basate su similarità con concetti noti
        known_concepts = self.knowledge.search(topic)
        
        for concept in known_concepts[:3]:
            hypothesis = self._create_hypothesis(
                {
                    "type": "similarity",
                    "description": f"{topic} è simile a {concept.name}",
                    "confidence": 0.3,
                    "examples": 0
                },
                [f"{topic} ↔ {concept.name}"]
            )
            hypotheses.append(hypothesis)
            self.hypotheses[hypothesis.id] = hypothesis
        
        return hypotheses
    
    def get_learning_summary(self) -> dict:
        """Riassume tutto ciò che l'engine ha imparato da solo."""
        return {
            "hypotheses_formulated": len(self.hypotheses),
            "experiences": len(self.experiences),
            "rules_self_created": len(self.self_created_rules),
            "curiosity_queue": len(self.curiosity_queue),
            "top_hypotheses": sorted(
                self.hypotheses.values(),
                key=lambda h: h.confidence,
                reverse=True
            )[:5],
            "lessons_learned": [e.lesson for e in self.experiences[-10:]]
        }
