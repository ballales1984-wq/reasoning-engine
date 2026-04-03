from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
import math


@dataclass
class Hypothesis:
    id: str
    name: str
    probability: float = 0.5
    features: Dict[str, Any] = field(default_factory=dict)
    evidence: List[str] = field(default_factory=list)

    def __post_init__(self):
        self.probability = max(0.001, min(0.999, self.probability))


class HypothesisSpace:
    def __init__(self, domain: str = "general"):
        self.domain = domain
        self.hypotheses: Dict[str, Hypothesis] = {}
        self.observations: List[Dict[str, Any]] = []

    def add_hypothesis(self, h: Hypothesis):
        self.hypotheses[h.id] = h

    def get_hypothesis(self, h_id: str) -> Optional[Hypothesis]:
        return self.hypotheses.get(h_id)

    def all_hypotheses(self) -> List[Hypothesis]:
        return list(self.hypotheses.values())

    def update_probability(self, h_id: str, new_prob: float):
        if h_id in self.hypotheses:
            self.hypotheses[h_id].probability = new_prob

    def renormalize(self):
        total = sum(h.probability for h in self.hypotheses.values())
        if total > 0:
            for h in self.hypotheses.values():
                h.probability /= total

    def get_top_hypothesis(self) -> Optional[Hypothesis]:
        if not self.hypotheses:
            return None
        return max(self.hypotheses.values(), key=lambda h: h.probability)

    def get_entropy(self) -> float:
        probs = [h.probability for h in self.hypotheses.values() if h.probability > 0]
        if not probs:
            return 0.0
        return -sum(p * math.log2(p) for p in probs)

    def add_observation(self, obs: Dict[str, Any]):
        self.observations.append(obs)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "domain": self.domain,
            "hypotheses": {
                h_id: {
                    "name": h.name,
                    "probability": h.probability,
                    "features": h.features,
                    "evidence": h.evidence,
                }
                for h_id, h in self.hypotheses.items()
            },
            "observations": self.observations,
        }
