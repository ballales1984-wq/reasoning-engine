from .hypothesis_space import HypothesisSpace


class KnowledgeGraphBridge:
    def __init__(self, kg=None):
        self.kg = kg

    def build_hypothesis_space(self, names, features=None, default_features=None):
        wanted = features or default_features
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
                if wanted and rel not in wanted:
                    continue
                row[rel] = bool(targets)

            hypotheses[name] = row

        return HypothesisSpace(hypotheses)

    # Backward-compatible API.
    def load_from_dict(self, data):
        self.kg = dict(data or {})
        return self

    def get_features(self, name):
        if isinstance(self.kg, dict):
            return dict(self.kg.get(name, {}))
        concept = self.kg.get(name) if self.kg and hasattr(self.kg, "get") else None
        if not concept:
            return {}
        rels = getattr(concept, "relations", {}) or {}
        return {k: bool(v) for k, v in rels.items()}

    def to_hypotheses(self):
        if isinstance(self.kg, dict):
            return dict(self.kg)
        out = {}
        if not self.kg or not hasattr(self.kg, "concepts"):
            return out
        for name in self.kg.concepts:
            out[name] = self.get_features(name)
        return out


KGBridge = KnowledgeGraphBridge
