from enum import Enum


class AnswerConfidence(Enum):
    HIGH = 1.0
    MEDIUM = 0.7
    LOW = 0.4
    UNKNOWN = 0.2


class SoftProbabilityUpdater:
    PENALTY = {
        AnswerConfidence.HIGH: 0.0,
        AnswerConfidence.MEDIUM: 0.1,
        AnswerConfidence.LOW: 0.3,
        AnswerConfidence.UNKNOWN: 0.8,
    }

    def __init__(self, space):
        self.space = space

    def update(self, feature, value, conf=AnswerConfidence.HIGH):
        penalty = self.PENALTY[conf]
        for h in list(self.space.active):
            if self.space.hypotheses[h].get(feature) != value:
                self.space.priors[h] = self.space.priors.get(h, 0.0) * penalty

        self.space.active = {h for h in self.space.active if self.space.priors.get(h, 0.0) > 0.01}
        self._normalize()

    def _normalize(self):
        total = sum(self.space.priors.get(h, 0.0) for h in self.space.active)
        if total:
            for h in list(self.space.active):
                self.space.priors[h] = self.space.priors[h] / total


ProbabilityUpdater = SoftProbabilityUpdater
