"""
KnowledgeGraph — Il "cervello" che memorizza concetti e le loro connessioni.

Ogni concetto è un nodo, ogni relazione è un arco.

Esempio:
    "6" → ha_categoria → "numero"
    "6" → è_uguale_a → "5+1"
    "6" → ha_esempi → ["🍎🍎🍎🍎🍎🍎", "sei cose"]
    "6" → è_maggiore_di → "5"
"""


class Concept:
    """Un singolo concetto nel knowledge graph."""
    
    def __init__(self, name: str, description: str = "",
                 examples: list[str] = None, category: str = "general"):
        self.name = name
        self.description = description
        self.examples = examples or []
        self.category = category
        self.relations = {}  # {relation_type: [target_concepts]}
    
    def add_relation(self, relation_type: str, target: str):
        if relation_type not in self.relations:
            self.relations[relation_type] = []
        if target not in self.relations[relation_type]:
            self.relations[relation_type].append(target)
    
    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "examples": self.examples,
            "category": self.category,
            "relations": self.relations
        }


class KnowledgeGraph:
    """
    Il grafo di conoscenza. Memorizza tutti i concetti e le loro connessioni.
    """
    
    def __init__(self):
        self.concepts = {}  # {name: Concept}
    
    def add(self, name: str, description: str = "",
            examples: list[str] = None, category: str = "general") -> Concept:
        """Aggiunge un concetto al grafo."""
        if name not in self.concepts:
            self.concepts[name] = Concept(name, description, examples, category)
        else:
            # Aggiorna se ci sono nuove info
            concept = self.concepts[name]
            if description:
                concept.description = description
            if examples:
                concept.examples.extend(examples)
            if category != "general":
                concept.category = category
        return self.concepts[name]
    
    def get(self, name: str) -> Concept | None:
        """Recupera un concetto per nome (case-insensitive)."""
        if name in self.concepts:
            return self.concepts[name]
        # Case-insensitive fallback
        name_lower = name.lower()
        for key, concept in self.concepts.items():
            if key.lower() == name_lower:
                return concept
        return None
    
    def find(self, names: list[str]) -> dict:
        """Cerca più concetti. Ritorna {name: Concept|None}."""
        return {name: self.concepts.get(name) for name in names}
    
    def connect(self, source: str, relation: str, target: str):
        """Crea una relazione tra due concetti."""
        if source in self.concepts:
            self.concepts[source].add_relation(relation, target)
    
    def list_all(self) -> list[dict]:
        """Lista tutti i concetti."""
        return [c.to_dict() for c in self.concepts.values()]
    
    def search(self, query: str) -> list[Concept]:
        """Cerca concetti per nome o descrizione."""
        results = []
        query_lower = query.lower()
        for concept in self.concepts.values():
            if (query_lower in concept.name.lower() or
                query_lower in concept.description.lower()):
                results.append(concept)
        return results
