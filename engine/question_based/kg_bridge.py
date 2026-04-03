"""
KnowledgeGraph Bridge - Collega question_based al KnowledgeGraph esistente

Permette di:
1. Estrarre caratteristiche automaticamente dal KnowledgeGraph
2. Costruire HypothesisSpace da nodi esistenti
3. Aggiornare il grafo con nuove informazioni
"""

from .hypothesis_space import HypothesisSpace
from .probability_updater import AnswerConfidence


class KnowledgeGraphBridge:
    """
    Bridge tra Question-Based Reasoner e KnowledgeGraph.
    
    Permette di usare il knowledge graph come fonte di conoscenza
    per le ipotesi e le loro caratteristiche.
    """
    
    # Mapping relazioni → caratteristiche
    RELATION_TO_FEATURE = {
        "ha_proprietà": "property",
        "ha_attributo": "attribute",
        "è_un": "is_a",
        "ha_categoria": "category",
        "è_domestico": "domestico",
        "è_selvatico": "selvatico",
        "ha_colore": "colore",
        "ha_forma": "forma",
        "ha_dimensione": "dimensione",
    }
    
    def __init__(self, knowledge_graph=None):
        """
        Args:
            knowledge_graph: KnowledgeGraph instance (opzionale)
        """
        self.kg = knowledge_graph
        self._feature_cache = {}
    
    def build_hypothesis_space(
        self,
        concept_names: list[str],
        feature_template: dict = None,
        default_features: list[str] = None
    ) -> HypothesisSpace:
        """
        Costruisce HypothesisSpace da una lista di concetti.
        
        Args:
            concept_names: Lista di nomi concetti nel KG
            feature_template: Template opzionale di caratteristiche
            default_features: Lista default di feature da estrarre
            
        Returns:
            HypothesisSpace pronto per il QuestionReasoner
        """
        hypotheses = {}
        
        for name in concept_names:
            if self.kg and name in self.kg.concepts:
                concept = self.kg.concepts[name]
                # Estrai feature dal concetto
                features = self._extract_features(concept, default_features)
            else:
                # Usa template o salta
                features = feature_template or {}
            
            if features:  # Solo se ha almeno una feature
                hypotheses[name] = features
        
        return HypothesisSpace(hypotheses)
    
    def _extract_features(self, concept, default_features: list = None) -> dict:
        """
        Estrae caratteristiche da un concetto.
        
        Args:
            concept: Concept instance
            default_features: Feature da cercare nelle relazioni
            
        Returns:
            dict di {feature: value}
        """
        features = {}
        
        # Feature di default da cercare nelle relazioni
        search_features = default_features or [
            "domestico", "selvatico", "colore", "dimensione",
            "forma", "category", "property", "attribute"
        ]
        
        for rel_type, targets in concept.relations.items():
            # Mappa relazione a feature
            feature = self.RELATION_TO_FEATURE.get(rel_type, rel_type)
            
            # Se la feature è una di quelle cercate
            if feature in search_features:
                # Prendi il primo target come valore
                if targets:
                    value = targets[0]
                    # Normalizza valori booleani
                    if isinstance(value, str):
                        value = value.lower() in ["true", "si", "yes", "1", "domestico"]
                    features[feature] = value
        
        # Aggiungi category come feature
        if concept.category and concept.category != "general":
            features["category"] = concept.category
        
        return features
    
    def add_hypothesis_from_text(
        self,
        name: str,
        description: str,
        features: dict,
        relations: dict = None
    ) -> bool:
        """
        Aggiunge una nuova ipotesi al knowledge graph.
        
        Args:
            name: Nome del concetto
            description: Descrizione
            features: Caratteristiche {feature: value}
            relations: Relazioni opzionali
            
        Returns:
            True se aggiunto, False se già esistente
        """
        if not self.kg:
            return False
        
        if name in self.kg.concepts:
            return False  # Già esiste
        
        # Crea il concetto
        concept = self.kg.add(name, description)
        
        # Aggiungi le feature come relazioni
        for feature, value in features.items():
            if isinstance(value, bool):
                # Feature booleane → relazione è_un o ha_proprietà
                rel = "è_domestico" if feature == "domestico" else "ha_proprietà"
                concept.add_relation(rel, str(value))
            else:
                concept.add_relation(f"ha_{feature}", str(value))
        
        # Aggiungi relazioni custom
        if relations:
            for rel_type, targets in relations.items():
                if isinstance(targets, list):
                    for t in targets:
                        concept.add_relation(rel_type, t)
                else:
                    concept.add_relation(rel_type, str(targets))
        
        return True
    
    def update_hypothesis_features(self, name: str, features: dict) -> bool:
        """
        Aggiorna le caratteristiche di un'ipotesi esistente.
        
        Args:
            name: Nome concetto
            features: Nuove caratteristiche
            
        Returns:
            True se aggiornato, False se non trovato
        """
        if not self.kg or name not in self.kg.concepts:
            return False
        
        concept = self.kg.concepts[name]
        
        for feature, value in features.items():
            rel = f"ha_{feature}"
            # Rimuovi vecchie relazioni di questo tipo
            if rel in concept.relations:
                concept.relations[rel] = []
            concept.add_relation(rel, str(value))
        
        return True
    
    def get_hypothesis_features(self, name: str) -> dict:
        """
        Estrae le caratteristiche di un'ipotesi.
        
        Args:
            name: Nome concetto
            
        Returns:
            dict di {feature: value} o None se non trovato
        """
        if not self.kg or name not in self.kg.concepts:
            return None
        
        concept = self.kg.concepts[name]
        return self._extract_features(concept)
    
    def suggest_new_features(self, active_hypotheses: list) -> list:
        """
        Suggerisce nuove caratteristiche che potrebbero distinguere le ipotesi.
        
        Args:
            active_hypotheses: Lista di ipotesi attive
            
        Returns:
            Lista di feature suggerite
        """
        if not self.kg:
            return []
        
        suggested = []
        
        # Per ogni concetto, guarda le sue relazioni
        for name in active_hypotheses:
            if name not in self.kg.concepts:
                continue
            
            concept = self.kg.concepts[name]
            
            # Le relazioni che potrebbero essere utili come feature
            for rel_type in concept.relations:
                if rel_type not in self.RELATION_TO_FEATURE:
                    # Nuova relazione non ancora mappata
                    suggested.append(rel_type)
        
        return list(set(suggested))  # Rimuovi duplicati


# Funzione helper per creare HypothesisSpace da KG
def create_space_from_knowledge(
    knowledge_graph,
    concept_names: list,
    default_features: list = None
) -> HypothesisSpace:
    """
    Factory function per creare HypothesisSpace da KnowledgeGraph.
    
    Args:
        knowledge_graph: KnowledgeGraph instance
        concept_names: Lista di concetti da usare come ipotesi
        default_features: Feature da estrarre
        
    Returns:
        HypothesisSpace
    """
    bridge = KnowledgeGraphBridge(knowledge_graph)
    return bridge.build_hypothesis_space(
        concept_names,
        default_features=default_features
    )


# Esempio di utilizzo
if __name__ == "__main__":
    from engine.knowledge_graph import KnowledgeGraph
    
    # Crea KG con alcuni animali
    kg = KnowledgeGraph()
    
    kg.add("cane", "Animale domestico", category="mammifero")
    kg.concepts["cane"].add_relation("è_domestico", "true")
    kg.concepts["cane"].add_relation("ha_proprietà", "coda_corta")
    
    kg.add("gatto", "Animale domestico", category="mammifero")
    kg.concepts["gatto"].add_relation("è_domestico", "true")
    kg.concepts["gatto"].add_relation("ha_proprietà", "coda_lunga")
    
    kg.add("volpe", "Animale selvatico", category="mammifero")
    kg.concepts["volpe"].add_relation("è_domestico", "false")
    kg.concepts["volpe"].add_relation("ha_proprietà", "coda_lunga")
    
    # Crea HypothesisSpace
    bridge = KnowledgeGraphBridge(kg)
    space = bridge.build_hypothesis_space(
        ["cane", "gatto", "volpe"],
        default_features=["domestico", "proprietà"]
    )
    
    print("HypothesisSpace creato dal KnowledgeGraph:")
    print(f"  Ipotesi: {space.remaining()}")
    print(f"  Features: {space.features()}")
    print(f"  Priors: {space.priors}")