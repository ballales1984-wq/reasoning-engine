from .hypothesis_space import HypothesisSpace


class KnowledgeGraphBridge:
    def __init__(self, kg=None):
        self.kg = kg

    def build_hypothesis_space(self, names, features=None):
        hypotheses = {}
        if not self.kg:
            return HypothesisSpace(hypotheses)

        for name in names:
            concept = self.kg.get(name) if hasattr(self.kg, "get") else None
            if not concept:
                continue

            # Estrazione minima e robusta: usa le relazioni come feature booleane.
            rels = getattr(concept, "relations", {}) or {}
            row = {}
            for rel, targets in rels.items():
                if features and rel not in features:
                    continue
                row[rel] = bool(targets)

            hypotheses[name] = row

        return HypothesisSpace(hypotheses)
