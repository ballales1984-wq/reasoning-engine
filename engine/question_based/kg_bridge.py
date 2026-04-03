from typing import Dict, Any, List, Optional
import json


class KGBridge:
    def __init__(self, knowledge_graph: Optional[Dict[str, Any]] = None):
        self.kg = knowledge_graph or {}
        self.entity_features: Dict[str, Dict[str, Any]] = {}

    def load_from_dict(self, kg: Dict[str, Any]):
        self.kg = kg
        self._extract_features()

    def _extract_features(self):
        for entity, data in self.kg.items():
            if isinstance(data, dict):
                self.entity_features[entity] = {
                    k: v
                    for k, v in data.items()
                    if isinstance(v, (str, int, float, bool))
                }

    def get_features(self, entity: str) -> Dict[str, Any]:
        return self.entity_features.get(entity, {})

    def get_entities(self) -> List[str]:
        return list(self.kg.keys())

    def query(self, feature: str, value: Any) -> List[str]:
        results = []
        for entity, features in self.entity_features.items():
            if features.get(feature) == value:
                results.append(entity)
        return results

    def to_hypotheses(self, domain: str = "general") -> List[Dict[str, Any]]:
        hypotheses = []
        for entity, features in self.entity_features.items():
            hypotheses.append(
                {
                    "id": entity.lower().replace(" ", "_"),
                    "name": entity,
                    "probability": 1.0 / len(self.entity_features)
                    if self.entity_features
                    else 0.5,
                    "features": features,
                    "evidence": [],
                }
            )
        return hypotheses

    def to_dict(self) -> Dict[str, Any]:
        return {"knowledge_graph": self.kg, "entity_features": self.entity_features}
