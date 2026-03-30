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
    Gestisce l'apprendimento di nuovi concetti.
    """
    
    def __init__(self, knowledge_graph):
        self.knowledge = knowledge_graph
        self.learning_history = []
    
    def add_concept(self, name: str, examples: list[str],
                    description: str = None, category: str = "general"):
        """
        Aggiunge un concetto attraverso esempi.
        
        learner.add_concept("6",
            examples=["🍎🍎🍎🍎🍎🍎", "sei cose", "5+1"],
            description="il numero sei",
            category="math/numbers")
        """
        # Se non c'è una descrizione, ne genera una dagli esempi
        if not description:
            description = self._infer_description(name, examples)
        
        # Aggiunge al knowledge graph
        concept = self.knowledge.add(name, description, examples, category)
        
        # Cerca automaticamente relazioni con concetti esistenti
        self._infer_relations(name, examples)
        
        # Registra l'apprendimento
        self.learning_history.append({
            "concept": name,
            "examples": examples,
            "description": description,
            "category": category
        })
        
        return concept
    
    def _infer_description(self, name: str, examples: list[str]) -> str:
        """
        Cerca di capire cos'è un concetto dagli esempi.
        Questo è il "ragionamento" del learner.
        """
        # Cerca pattern negli esempi
        has_numbers = any(c.isdigit() for ex in examples for c in ex)
        has_emoji = any(ord(c) > 127 for ex in examples for c in ex)
        
        if has_numbers and "+" in " ".join(examples):
            return f"un numero che può essere ottenuto per addizione"
        elif has_emoji:
            return f"un concetto rappresentabile con oggetti"
        else:
            return f"un concetto con {len(examples)} esempi"
    
    def _infer_relations(self, name: str, examples: list[str]):
        """
        Cerca relazioni automatiche tra il nuovo concetto e quelli esistenti.
        
        Se insegno "6" con esempio "5+1", e già conosco "5" e "1",
        creo automaticamente la relazione: 6 = 5 + 1
        """
        for example in examples:
            # Cerca espressioni matematiche negli esempi
            if "+" in example:
                parts = example.split("+")
                for part in parts:
                    part = part.strip()
                    if self.knowledge.get(part):
                        self.knowledge.connect(name, "composto_da", part)
                        self.knowledge.connect(part, "parte_di", name)
    
    def learn_from_interaction(self, question: str, correct_answer,
                               explanation: str = ""):
        """
        Impara da un'interazione corretta.
        Se l'utente corregge una risposta, l'engine impara.
        """
        self.learning_history.append({
            "type": "correction",
            "question": question,
            "correct_answer": correct_answer,
            "explanation": explanation
        })
    
    def get_learning_progress(self) -> dict:
        """Mostra il progresso di apprendimento."""
        return {
            "total_lessons": len(self.learning_history),
            "recent": self.learning_history[-5:] if self.learning_history else []
        }
