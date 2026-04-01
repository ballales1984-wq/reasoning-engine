"""
Analogical Reasoner — Trova analogie tra concetti.

Confronta la struttura di due concetti (relazioni e proprietà)
e trova somiglianze strutturali.

Esempio:
  "il sistema solare" (sole + pianeti in orbita)
  "l'atomo" (nucleo + elettroni in orbita)
  → "Un atomo è come un sistema solare in miniatura"
"""

from dataclasses import dataclass, field
from collections import Counter


from ..core.types import Analogy, AnalogyResult


class AnalogicalReasoner:
    """
    Motore analogico. Trova somiglianze strutturali
    tra concetti nel Knowledge Graph.
    """

    def __init__(self, knowledge_graph):
        self.knowledge = knowledge_graph
        self._signature_cache = {}  # {concept_name: signature}

    def find_analogies(self, concept_name: str, max_results: int = 3) -> AnalogyResult:
        """
        Trova concetti simili a concept_name nel Knowledge Graph.

        Confronta la struttura delle relazioni (non il contenuto).
        """
        source = self.knowledge.get(concept_name)
        if not source:
            return AnalogyResult(
                found=False, explanation=f"Non conosco '{concept_name}'"
            )

        analogies = []

        # Confronta con tutti gli altri concetti
        for other_name, other_concept in self.knowledge.concepts.items():
            if other_name == concept_name:
                continue

            analogy = self._compare(source, other_concept)
            if analogy and analogy.structural_similarity > 0.2:
                analogies.append(analogy)

        # Ordina per similarità
        analogies.sort(key=lambda a: a.structural_similarity, reverse=True)
        analogies = analogies[:max_results]

        if analogies:
            best = analogies[0]
            explanation = f"🔗 **Analogie per '{concept_name}':**\n\n"
            for a in analogies:
                bar = "█" * int(a.structural_similarity * 10)
                explanation += f"  • {concept_name} ↔ {a.target}\n"
                explanation += f"    Similarità: {bar} {a.structural_similarity:.0%}\n"
                if a.explanation:
                    explanation += f"    {a.explanation}\n"

            return AnalogyResult(
                found=True,
                analogies=analogies,
                best_analogy=best,
                explanation=explanation,
            )

        return AnalogyResult(
            found=False, explanation=f"Non ho trovato analogie per '{concept_name}'"
        )

    def explain_analogy(self, source_name: str, target_name: str) -> str:
        """
        Spiega l'analogia tra due concetti specifici.
        """
        source = self.knowledge.get(source_name)
        target = self.knowledge.get(target_name)

        if not source or not target:
            return "Non conosco uno o entrambi i concetti"

        analogy = self._compare(source, target)

        if not analogy or analogy.structural_similarity < 0.1:
            return f"'{source_name}' e '{target_name}' non sono particolarmente simili"

        explanation = f"🔄 **Analogia: {source_name} ↔ {target_name}**\n\n"

        if analogy.shared_relations:
            explanation += "**Relazioni in comune:**\n"
            for rel in analogy.shared_relations:
                explanation += f"  • {rel}\n"

        if analogy.shared_properties:
            explanation += "\n**Proprietà in comune:**\n"
            for prop in analogy.shared_properties:
                explanation += f"  • {prop}\n"

        if analogy.explanation:
            explanation += f"\n💡 {analogy.explanation}"

        explanation += (
            f"\n\n📊 Similarità strutturale: {analogy.structural_similarity:.0%}"
        )

        return explanation

    def transfer_knowledge(self, source_name: str, target_name: str) -> dict:
        """
        Trasferisce proprietà da un concetto all'altro tramite analogia.

        Se A è analogo a B, e A ha proprietà P,
        allora B probabilmente ha una proprietà simile a P.
        """
        source = self.knowledge.get(source_name)
        target = self.knowledge.get(target_name)

        if not source or not target:
            return {"transferred": False, "reason": "Concetto non trovato"}

        analogy = self._compare(source, target)

        if analogy.structural_similarity < 0.3:
            return {"transferred": False, "reason": "Troppo diversi per trasferire"}

        transferred = []

        # Trova proprietà di source che target non ha
        for rel_type, targets in source.relations.items():
            if rel_type not in target.relations:
                transferred.append(
                    {
                        "relation": rel_type,
                        "values": targets,
                        "confidence": analogy.structural_similarity,
                    }
                )

        return {
            "transferred": len(transferred) > 0,
            "properties": transferred,
            "based_on_analogy": analogy.structural_similarity,
        }

    def _compare(self, concept_a, concept_b) -> Analogy | None:
        """
        Confronta due concetti e calcola la similarità strutturale.
        """
        # Estrai "firma strutturale" di ogni concetto
        sig_a = self._structural_signature(concept_a)
        sig_b = self._structural_signature(concept_b)

        # Trova relazioni in comune (per TIPO, non per valore)
        rel_types_a = set(sig_a["relation_types"])
        rel_types_b = set(sig_b["relation_types"])
        shared_rel_types = rel_types_a & rel_types_b

        # Trova proprietà in comune
        props_a = set(sig_a["property_types"])
        props_b = set(sig_b["property_types"])
        shared_props = props_a & props_b

        # Calcola similarità strutturale
        total_types = len(rel_types_a | rel_types_b)
        if total_types == 0:
            similarity = 0.0
        else:
            similarity = len(shared_rel_types) / total_types

        # Bonus per proprietà comuni
        if props_a or props_b:
            prop_similarity = len(shared_props) / max(len(props_a | props_b), 1)
            similarity = (similarity + prop_similarity) / 2

        # Genera spiegazione
        explanation = ""
        if shared_rel_types:
            explanation = f"Entrambi hanno: {', '.join(shared_rel_types)}"

        return Analogy(
            source=concept_a.name,
            target=concept_b.name,
            shared_relations=list(shared_rel_types),
            shared_properties=list(shared_props),
            structural_similarity=similarity,
            explanation=explanation,
        )

    def _structural_signature(self, concept) -> dict:
        """
        Genera una "firma strutturale" di un concetto (con cache).
        La firma contiene i TIPI di relazioni, non i valori specifici.
        """
        if concept.name in self._signature_cache:
            return self._signature_cache[concept.name]

        relation_types = []
        property_types = []

        for rel_type, targets in concept.relations.items():
            relation_types.append(rel_type)
            if len(targets) > 3:
                property_types.append(f"{rel_type}:many")
            elif len(targets) == 1:
                property_types.append(f"{rel_type}:single")

        sig = {
            "relation_types": relation_types,
            "property_types": property_types,
            "num_relations": len(relation_types),
        }
        self._signature_cache[concept.name] = sig
        return sig
