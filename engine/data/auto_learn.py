"""
Auto-Learner — L'engine impara automaticamente dalle interazioni.

Ogni volta che l'engine riceve una risposta dall'LLM o dall'utente,
analizza i nuovi concetti e li integra nel Knowledge Graph.
"""

import re
from datetime import datetime


class AutoLearner:
    """
    Apprendimento automatico da interazioni.
    """

    def __init__(self, knowledge_graph, llm_bridge=None):
        self.knowledge = knowledge_graph
        self.llm = llm_bridge
        self.interaction_log = []
        self.auto_learned = []

    def process_interaction(self, question: str, answer: str, source: str = "user"):
        """
        Analizza un'interazione e impara concetti nuovi.
        """
        self.interaction_log.append({
            "timestamp": datetime.now().isoformat(),
            "question": question,
            "answer": answer,
            "source": source
        })

        new_concepts = []

        # Estrai concetti dalla domanda
        q_concepts = self._extract_concepts_from_text(question)
        a_concepts = self._extract_concepts_from_text(answer)

        for concept in q_concepts + a_concepts:
            if concept not in self.knowledge.concepts:
                # Concetto nuovo — prova a impararlo
                if self.llm and self.llm.is_available():
                    response = self.llm.provide_knowledge(concept)
                    if response.facts:
                        self._integrate_facts(concept, response.facts)
                        new_concepts.append(concept)
                else:
                    # Senza LLM, crea placeholder
                    self.knowledge.add(concept, description=f"[da imparare] {concept}")
                    new_concepts.append(concept)

        # Estrai relazioni dal testo
        relations = self._extract_relations_from_text(question + " " + answer)
        for subj, rel, obj in relations:
            self.knowledge.add(subj)
            self.knowledge.add(obj)
            self.knowledge.connect(subj, rel, obj)

        if new_concepts:
            self.auto_learned.append({
                "timestamp": datetime.now().isoformat(),
                "concepts": new_concepts,
                "from_question": question
            })

        return new_concepts

    def batch_learn(self, items: list[dict]) -> dict:
        """
        Apprendimento in blocco.

        items = [
            {"concept": "DNA", "description": "...", "category": "biologia"},
            {"concept": "gene", "description": "...", "category": "biologia"},
            {"subject": "DNA", "relation": "contiene", "object": "geni"},
        ]
        """
        learned = 0
        relations_added = 0

        for item in items:
            if "concept" in item:
                self.knowledge.add(
                    item["concept"],
                    description=item.get("description", ""),
                    examples=item.get("examples", []),
                    category=item.get("category", "general")
                )
                learned += 1

                # Se c'è un LLM, arricchisci
                if self.llm and self.llm.is_available() and not item.get("description"):
                    response = self.llm.provide_knowledge(item["concept"])
                    if response.facts:
                        self._integrate_facts(item["concept"], response.facts)

            elif "subject" in item and "relation" in item and "object" in item:
                self.knowledge.add(item["subject"])
                self.knowledge.add(item["object"])
                self.knowledge.connect(item["subject"], item["relation"], item["object"])
                relations_added += 1

        return {
            "concepts_learned": learned,
            "relations_added": relations_added
        }

    def enrich_from_text(self, text: str) -> dict:
        """
        Analizza un testo libero e estrae concetti e relazioni.
        Utile per "insegnare" all'engine da documenti.
        """
        concepts = self._extract_concepts_from_text(text)
        relations = self._extract_relations_from_text(text)

        added_concepts = []
        for c in concepts:
            if c not in self.knowledge.concepts:
                self.knowledge.add(c, description=f"[estratto da testo] {c}")
                added_concepts.append(c)

        for subj, rel, obj in relations:
            self.knowledge.add(subj)
            self.knowledge.add(obj)
            self.knowledge.connect(subj, rel, obj)

        return {
            "concepts_extracted": len(added_concepts),
            "concepts": added_concepts,
            "relations": len(relations)
        }

    def get_stats(self) -> dict:
        """Statistiche di apprendimento."""
        return {
            "total_interactions": len(self.interaction_log),
            "auto_learned_batches": len(self.auto_learned),
            "concepts_auto_learned": sum(len(b["concepts"]) for b in self.auto_learned),
            "last_interaction": self.interaction_log[-1] if self.interaction_log else None
        }

    def _extract_concepts_from_text(self, text: str) -> list[str]:
        """Estrae concetti significativi dal testo."""
        # Stop words estese
        stops = {
            "il", "la", "lo", "i", "gli", "le", "un", "una", "di", "del",
            "della", "e", "è", "che", "cosa", "come", "quanto", "quale",
            "perché", "chi", "dove", "quando", "fa", "sono", "ha", "ho",
            "hai", "hanno", "più", "meno", "per", "con", "su", "da",
            "in", "non", "si", "se", "ma", "anche", "così", "poi",
            "vero", "falso", "giusto", "sbagliato", "calcola", "risolvi",
        }
        text_lower = text.lower()
        tokens = re.findall(r'[a-zàèéìòù]+', text_lower)
        concepts = []
        seen = set()
        for t in tokens:
            if t not in stops and len(t) > 2 and t not in seen:
                concepts.append(t)
                seen.add(t)
        return concepts

    def _extract_relations_from_text(self, text: str) -> list[tuple[str, str, str]]:
        """Estrae relazioni dal testo."""
        relations = []
        text_lower = text.lower()

        patterns = [
            (r'(\w+)\s+[èe]\s+(?:un[ao]?\s+)?(\w+)', 'è_un'),
            (r'(\w+)\s+ha\s+(?:il\s+|la\s+)?(\w+)', 'ha'),
            (r'(\w+)\s+(?:contiene|comprende)\s+(\w+)', 'contiene'),
            (r'(\w+)\s+(?:causa|provoca)\s+(\w+)', 'causa'),
            (r'(\w+)\s+(?:è simile a|assomiglia a)\s+(\w+)', 'simile_a'),
            (r'(\w+)\s+(?:serve per|viene usato per)\s+(.+?)(?:\.|$)', 'serve_per'),
        ]

        for pattern, rel_type in patterns:
            for match in re.finditer(pattern, text_lower):
                groups = match.groups()
                if len(groups) >= 2:
                    relations.append((groups[0], rel_type, groups[1].strip()))

        return relations

    def _integrate_facts(self, concept: str, facts: list):
        """Integra fatti estratti dall'LLM nel KG."""
        for fact in facts:
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
