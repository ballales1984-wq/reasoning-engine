"""
RuleEngine — Il "ragionatore" che applica regole logiche.

Le regole sono funzioni esplicite, non pattern statistici.
Se sai che 2+3=5 e conosci la regola dell'addizione,
puoi calcolare 6+9 senza averlo mai visto prima.
"""


class Rule:
    """Una singola regola."""
    
    def __init__(self, name: str, func, description: str = "",
                 inputs: list[str] = None, output_type: str = "any"):
        self.name = name
        self.func = func
        self.description = description
        self.inputs = inputs or []
        self.output_type = output_type
    
    def apply(self, *args, **kwargs):
        """Applica la regola."""
        return self.func(*args, **kwargs)
    
    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "inputs": self.inputs,
            "output_type": self.output_type
        }


class RuleEngine:
    """
    Motore delle regole. Contiene tutte le regole logiche
    e sa quale applicare in base alla domanda.
    """
    
    def __init__(self):
        self.rules = {}  # {name: Rule}
        self._register_builtins()
    
    def _register_builtins(self):
        """Registra le regole matematiche base."""
        
        # Addizione
        self.add_rule(
            "addition",
            lambda a, b: a + b,
            description="Somma due numeri: a + b",
            inputs=["number", "number"],
            output_type="number"
        )
        
        # Sottrazione
        self.add_rule(
            "subtraction",
            lambda a, b: a - b,
            description="Sottrae b da a: a - b",
            inputs=["number", "number"],
            output_type="number"
        )
        
        # Moltiplicazione
        self.add_rule(
            "multiplication",
            lambda a, b: a * b,
            description="Moltiplica due numeri: a × b",
            inputs=["number", "number"],
            output_type="number"
        )
        
        # Divisione
        self.add_rule(
            "division",
            lambda a, b: a / b if b != 0 else None,
            description="Divide a per b: a ÷ b",
            inputs=["number", "number"],
            output_type="number"
        )
        
        # Confronto
        self.add_rule(
            "greater_than",
            lambda a, b: a > b,
            description="Verifica se a > b",
            inputs=["number", "number"],
            output_type="boolean"
        )
        
        self.add_rule(
            "equals",
            lambda a, b: a == b,
            description="Verifica se a == b",
            inputs=["any", "any"],
            output_type="boolean"
        )
    
    def add_rule(self, name: str, func, description: str = "",
                 inputs: list[str] = None, output_type: str = "any"):
        """Aggiunge una regola al motore."""
        self.rules[name] = Rule(name, func, description, inputs, output_type)
    
    def apply(self, parsed_question: dict, known_concepts: dict) -> dict | None:
        """
        Applica la regola appropriata alla domanda parsata.
        
        Ritorna {
            "answer": il risultato,
            "rule_used": nome della regola,
            "confidence": 0-1
        } oppure None se non riesce.
        """
        operation = parsed_question.get("operation")
        numbers = parsed_question.get("numbers", [])
        
        if operation == "addition" and len(numbers) >= 2:
            result = self.rules["addition"].apply(numbers[0], numbers[1])
            return {
                "answer": result,
                "rule_used": "addition",
                "confidence": 1.0,
                "explanation": f"{numbers[0]} + {numbers[1]} = {result}"
            }
        
        elif operation == "subtraction" and len(numbers) >= 2:
            result = self.rules["subtraction"].apply(numbers[0], numbers[1])
            return {
                "answer": result,
                "rule_used": "subtraction",
                "confidence": 1.0,
                "explanation": f"{numbers[0]} - {numbers[1]} = {result}"
            }
        
        elif operation == "multiplication" and len(numbers) >= 2:
            result = self.rules["multiplication"].apply(numbers[0], numbers[1])
            return {
                "answer": result,
                "rule_used": "multiplication",
                "confidence": 1.0,
                "explanation": f"{numbers[0]} × {numbers[1]} = {result}"
            }
        
        elif operation == "division" and len(numbers) >= 2:
            if numbers[1] == 0:
                return {
                    "answer": "Errore: divisione per zero",
                    "rule_used": "division",
                    "confidence": 1.0,
                    "explanation": "Non puoi dividere per zero!"
                }
            result = self.rules["division"].apply(numbers[0], numbers[1])
            return {
                "answer": result,
                "rule_used": "division",
                "confidence": 1.0,
                "explanation": f"{numbers[0]} ÷ {numbers[1]} = {result}"
            }
        
        # Lookup per definizioni
        elif operation == "lookup":
            entities = parsed_question.get("entities", [])
            for entity in entities:
                if entity in known_concepts and known_concepts[entity]:
                    concept = known_concepts[entity]
                    return {
                        "answer": concept.description,
                        "rule_used": "lookup",
                        "confidence": 0.95,
                        "explanation": f"{entity}: {concept.description}"
                    }
        
        return None
    
    def list_all(self) -> list[dict]:
        """Lista tutte le regole."""
        return [r.to_dict() for r in self.rules.values()]
    
    def get_rule(self, name: str) -> Rule | None:
        """Recupera una regola per nome."""
        return self.rules.get(name)
