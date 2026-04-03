"""
Auto-Researcher - Ricerca automatica web per arricchire il Knowledge Graph

Quando il Reasoner incontra un concetto nuovo o non ha abbastanza feature,
questo modulo:
1. Cerca sul web
2. Estrae informazioni rilevanti
3. Normalizza in proprietà strutturate
4. Aggiorna il Knowledge Graph

Flusso:
1. Riceve un concetto (es. "lupo")
2. Cerca informazioni sul web
3. Estrae testi rilevanti
4. Li converte in feature
5. Aggiorna il KG
"""

import re
import json
from typing import Optional


class AutoResearcher:
    """
    Ricerca automatica per arricchire la conoscenza.
    
    Usage:
        researcher = AutoResearcher(web_tool, vector_store)
        features = researcher.research("lupo", context=["cane", "gatto", "volpe"])
        kg = researcher.update_knowledge_graph(kg, "lupo", features)
    """
    
    # Pattern per estrarre feature da testo
    FEATURE_PATTERNS = [
        # "... è/sono ..."
        re.compile(r'(\w+)\s+(?:è|sono)\s+(?:un[’’]|una[’’]|di)?(\w+)', re.IGNORECASE),
        # "... ha/ hanno ..."
        re.compile(r'(\w+)\s+ha\s+([\w\s,]+)', re.IGNORECASE),
        # "... non ha ..."
        re.compile(r'(\w+)\s+non\s+ha\s+([\w\s,]+)', re.IGNORECASE),
    ]
    
    def __init__(
        self,
        web_tool=None,
        vector_store=None,
        llm_extractor=None
    ):
        """
        Args:
            web_tool: Tool per cercare sul web (es. DuckDuckGo)
            vector_store: Memorie vettoriale per salvare/articoli
            llm_extractor: LLMFeatureExtractor per normalizzare
        """
        self.web = web_tool
        self.vector = vector_store
        self.llm = llm_extractor
    
    def research(
        self,
        concept: str,
        context_hypotheses: list = None,
        max_results: int = 5
    ) -> dict:
        """
        Ricerca informazioni su un concetto.
        
        Args:
            concept: Concetto da cercare
            context_hypotheses: Ipotesi esistenti per contesto
            max_results: Numero massimo risultati web
            
        Returns:
            dict di {feature: value}
        """
        features = {}
        
        # 1. Cerca sul web
        if self.web:
            results = self._web_search(concept, max_results)
            
            # Estrai feature dai risultati
            for result in results:
                extracted = self._extract_from_text(
                    result.get("text", ""),
                    concept
                )
                features.update(extracted)
        
        # 2. Cerca nella memoria vettoriale
        if self.vector and concept:
            memory_results = self._search_memory(concept, context_hypotheses)
            for mem in memory_results:
                extracted = self._extract_from_text(mem, concept)
                features.update(extracted)
        
        # 3. Arricchisci con LLM
        if self.llm and features:
            features = self.llm.enrich_features(concept, features)
        
        # 4. Se non ha trovato nulla, chiedi al LLM diretto
        if not features and self.llm and context_hypotheses:
            features = self.llm.extract_features(
                concept,
                context_hypotheses
            )
        
        return features
    
    def _web_search(self, query: str, max_results: int) -> list:
        """Cerca sul web."""
        if not self.web:
            return []
        
        try:
            # Format depends on web tool
            # Assuming similar to DuckDuckGo
            results = self.web.search(query, max_results)
            return results
        except:
            return []
    
    def _search_memory(self, concept: str, context: list) -> list:
        """Cerca nella memoria vettoriale."""
        if not self.vector:
            return []
        
        try:
            # Format depends on vector store
            results = self.vector.search(concept, top_k=3)
            return [r.get("text", "") for r in results]
        except:
            return []
    
    def _extract_from_text(self, text: str, concept: str) -> dict:
        """
        Estrae feature da testo libero.
        
        Args:
            text: Testo sorgente
            concept: Concetto cercato
            
        Returns:
            dict di {feature: value}
        """
        features = {}
        
        # Feature booleane comuni
        boolean_features = {
            "domestico": ["domestico", "domestic", "pet"],
            "selvatico": ["selvatico", "wild", "selvaggio"],
            "carnivoro": ["carnivoro", "carnivore", "mangia-carne"],
            "erbivoro": ["erbivoro", "herbivore", "mangia-piante"],
            "pericoloso": ["pericoloso", "dangerous", "predatore"],
            "notturno": ["notturno", "nocturnal", "notte"],
            "domestico": ["addomesticato", "tamed"],
        }
        
        text_lower = text.lower()
        
        for feature, keywords in boolean_features.items():
            for kw in keywords:
                if kw in text_lower:
                    # Verifica negazione
                    neg_pattern = f"non {kw}|mai {kw}|senza {kw}"
                    if re.search(neg_pattern, text_lower):
                        features[feature] = False
                    else:
                        features[feature] = True
                    break
        
        return features
    
    def update_knowledge_graph(
        self,
        knowledge_graph,
        concept: str,
        description: str = "",
        features: dict = None,
        relations: dict = None
    ):
        """
        Aggiorna il Knowledge Graph con nuove informazioni.
        
        Args:
            knowledge_graph: KnowledgeGraph instance
            concept: Nome concetto
            description: Descrizione
            features: Feature estratte
            relations: Relazioni custom
            
        Returns:
            KnowledgeGraph aggiornato
        """
        if not knowledge_graph:
            return None
        
        # Aggiungi il concetto
        concept_obj = knowledge_graph.add(concept, description)
        
        # Aggiungi le feature come relazioni
        if features:
            for feature, value in features.items():
                rel = f"ha_{feature}"
                concept_obj.add_relation(rel, str(value))
        
        # Aggiungi relazioni custom
        if relations:
            for rel_type, targets in relations.items():
                if isinstance(targets, list):
                    for t in targets:
                        concept_obj.add_relation(rel_type, t)
                else:
                    concept_obj.add_relation(rel_type, str(targets))
        
        return knowledge_graph
    
    def full_research_cycle(
        self,
        knowledge_graph,
        new_concept: str,
        existing_hypotheses: list = None,
        description: str = "",
        save_to_vector: bool = True
    ) -> dict:
        """
        Ciclo completo: ricerca → estrai → aggiorna KG.
        
        Args:
            knowledge_graph: KnowledgeGraph
            new_concept: Concetto da cercare
            existing_hypotheses: Ipotesi esistenti
            description: Descrizione iniziale
            save_to_vector: Salva in memoria vettoriale
            
        Returns:
            dict con {features, knowledge_graph, status}
        """
        # 1. Ricerca
        features = self.research(
            new_concept,
            existing_hypotheses
        )
        
        # 2. Aggiorna KG
        kg = self.update_knowledge_graph(
            knowledge_graph,
            new_concept,
            description,
            features
        )
        
        # 3. Salva in vector store se richiesto
        if save_to_vector and self.vector and features:
            try:
                self.vector.add(
                    f"{new_concept}: {json.dumps(features)}",
                    metadata={"concept": new_concept}
                )
            except:
                pass
        
        return {
            "concept": new_concept,
            "features": features,
            "knowledge_graph": kg,
            "status": "success" if features else "no_data"
        }


# Demo
if __name__ == "__main__":
    researcher = AutoResearcher()
    
    print("Auto-Researcher")
    print("=" * 40)
    print("""
researcher = AutoResearcher(web_tool, vector_store, llm_extractor)

# Ciclo completo
result = researcher.full_research_cycle(
    kg,
    new_concept="lupo",
    existing_hypotheses=["cane", "gatto", "volpe"],
    description="Mammifero carnivoro della famiglia dei canidi"
)

print(result["features"])
# Output: {"selvatico": true, "caccia_in_branco": true, "ulula": true, ...}
""")