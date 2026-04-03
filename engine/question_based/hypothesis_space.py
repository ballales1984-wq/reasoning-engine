from dataclasses import dataclass, field
from typing import Any


@dataclass
class Hypothesis:
    id: str
    name: str
    probability: float = 0.0
    features: dict[str, Any] = field(default_factory=dict)


class HypothesisSpace:
    def __init__(self, hypotheses: dict | str | None = None, priors: dict | None = None):
        self.domain = hypotheses if isinstance(hypotheses, str) else "default"
        self.hypotheses = hypotheses if isinstance(hypotheses, dict) else {}
        self.names = {h: h for h in self.hypotheses}
        self.active = set(self.hypotheses.keys())
        self.priors = {}

        if priors:
            self.priors = {k: float(v) for k, v in priors.items()}
        elif self.hypotheses:
            n = len(self.hypotheses)
            self.priors = {h: 1.0 / n for h in self.hypotheses}

        # Ensure priors cover all hypotheses.
        for h in self.hypotheses:
            self.priors.setdefault(h, 0.0)
        self.renormalize()

    def add_hypothesis(self, hypothesis: Hypothesis):
        self.hypotheses[hypothesis.id] = dict(hypothesis.features or {})
        self.names[hypothesis.id] = hypothesis.name or hypothesis.id
        self.priors[hypothesis.id] = float(hypothesis.probability)
        self.active.add(hypothesis.id)

    def get_hypothesis(self, hypothesis_id: str):
        if hypothesis_id not in self.hypotheses:
            return None
        return Hypothesis(
            id=hypothesis_id,
            name=self.names.get(hypothesis_id, hypothesis_id),
            probability=float(self.priors.get(hypothesis_id, 0.0)),
            features=dict(self.hypotheses.get(hypothesis_id, {})),
        )

    def all_hypotheses(self):
        out = []
        for h in self.hypotheses:
            hyp = self.get_hypothesis(h)
            if hyp is not None:
                out.append(hyp)
        return out

    def get_top_hypothesis(self):
        if not self.active:
            return None
        top_id = max(self.active, key=lambda h: self.priors.get(h, 0.0))
        return self.get_hypothesis(top_id)

    def renormalize(self):
        if not self.active:
            return
        total = sum(max(0.0, self.priors.get(h, 0.0)) for h in self.active)
        if total <= 0:
            uniform = 1.0 / len(self.active)
            for h in self.hypotheses:
                self.priors[h] = uniform if h in self.active else 0.0
            return
        for h in self.hypotheses:
            self.priors[h] = (max(0.0, self.priors.get(h, 0.0)) / total) if h in self.active else 0.0

    def filter(self, feature: str, value):
        self.active = {
            h for h in self.active if self.hypotheses.get(h, {}).get(feature) == value
        }
        for h in self.hypotheses:
            if h not in self.active:
                self.priors[h] = 0.0
        self.renormalize()

    def remaining(self):
        return list(self.active)

    def features(self):
        feats = set()
        for h in self.active:
            feats.update(self.hypotheses.get(h, {}).keys())
        return list(feats)
