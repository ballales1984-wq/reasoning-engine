class AutoResearcher:
    def __init__(self, web=None, vector=None, llm=None):
        self.web = web
        self.vector = vector
        self.llm = llm

    def research(self, concept, others=None):
        features = {}
        if self.llm and others:
            try:
                features = self.llm.extract_features(concept, others)
            except Exception:
                features = {}
        if not features:
            return {"error": "no_features_found", "concept": concept}
        return features

    def update_knowledge_graph(self, kg, concept, desc="", features=None, relations=None):
        if not kg:
            return None

        obj = kg.add(concept, desc)

        for k, v in (features or {}).items():
            if hasattr(obj, "add_relation"):
                obj.add_relation(f"ha_{k}", str(v))

        for r, t in (relations or {}).items():
            if hasattr(obj, "add_relation"):
                obj.add_relation(r, str(t))

        return kg

    # High-level helper used by demos/docs.
    def full_research_cycle(self, kg, new_concept, existing_hypotheses=None, description=""):
        features = self.research(new_concept, existing_hypotheses or [])
        if isinstance(features, dict) and "error" in features:
            features = {}
        updated = self.update_knowledge_graph(kg, new_concept, description, features=features)
        return {"features": features, "knowledge_graph": updated}
