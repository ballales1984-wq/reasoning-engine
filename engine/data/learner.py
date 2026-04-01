"""
Learner — Il modulo di apprendimento.

Come un bambino impara:
1. Vede esempi concreti (6 mele, 6 cose, 6 dita)
2. Trova il pattern comune (tutti hanno "6" in comune)
3. Costruisce il concetto astratto (il numero 6)
4. Collega il concetto ad altri concetti (6 = 5+1, 6 > 5)
"""


class Learner:
    """
    Gestisce l'apprendimento di nuovi concetti con supporto multi-canale.
    """
    
    def __init__(self, knowledge_graph):
        self.knowledge = knowledge_graph
        self.learning_history = []
    
    def add_concept(self, name: str, examples: list[str],
                    description: str = None, category: str = "general",
                    channel: str = "local", trust_score: float = None):
        """
        Aggiunge un concetto attraverso esempi, specificando il canale.
        """
        # Se non c'è una descrizione, ne genera una dagli esempi
        if not description:
            description = self._infer_description(name, examples)
        
        # Aggiunge al knowledge graph specificando il canale
        concept = self.knowledge.add(name, description, examples, category, channel, trust_score)
        
        # Cerca automaticamente relazioni con concetti esistenti
        self._infer_relations(name, examples, channel)
        
        # Registra l'apprendimento
        self.learning_history.append({
            "concept": name,
            "examples": examples,
            "description": description,
            "category": category,
            "channel": channel,
            "trust_score": trust_score or concept.channels[channel]["trust_score"]
        })
        
        return concept
    
    def _infer_description(self, name: str, examples: list[str]) -> str:
        """
        Cerca di capire cos'è un concetto dagli esempi.
        """
        # Cerca pattern negli esempi
        has_numbers = any(str(c).isdigit() for ex in examples for c in str(ex))
        has_emoji = any(ord(c) > 127 for ex in examples for c in str(ex))
        
        if has_numbers and "+" in " ".join([str(e) for e in examples]):
            return f"un numero che può essere ottenuto per addizione"
        elif has_emoji:
            return f"un concetto rappresentabile con oggetti"
        else:
            return f"un concetto con {len(examples)} esempi"
    
    def _infer_relations(self, name: str, examples: list[str], channel: str = "local"):
        """
        Cerca relazioni automatiche tra il nuovo concetto e quelli esistenti.
        """
        for example in examples:
            example_str = str(example)
            # Cerca espressioni matematiche negli esempi
            if "+" in example_str:
                parts = example_str.split("+")
                for part in parts:
                    part = part.strip()
                    if self.knowledge.get(part):
                        self.knowledge.connect(name, "composto_da", part, channel)
                        self.knowledge.connect(part, "parte_di", name, channel)
    
    def learn_from_interaction(self, question: str, correct_answer,
                               explanation: str = "", channel: str = "user"):
        """
        Impara da un'interazione corretta.
        """
        self.learning_history.append({
            "type": "correction",
            "question": question,
            "correct_answer": correct_answer,
            "explanation": explanation,
            "channel": channel
        })
    
    def get_learning_progress(self) -> dict:
        """Mostra il progresso di apprendimento."""
        return {
            "total_lessons": len(self.learning_history),
            "recent": self.learning_history[-5:] if self.learning_history else []
        }
