from typing import Dict, Any
import math
from .hypothesis_space import HypothesisSpace, Hypothesis


class ProbabilityUpdater:
    def __init__(self, smoothing: float = 0.01):
        self.smoothing = smoothing

    def bayesian_update(
        self,
        hypothesis_space: HypothesisSpace,
        question: str,
        answer: bool,
        likelihood_yes: Dict[str, float],
        likelihood_no: Dict[str, float],
    ) -> HypothesisSpace:
        likelihoods = likelihood_yes if answer else likelihood_no

        for h_id, h in hypothesis_space.hypotheses.items():
            prior = h.probability
            likelihood = likelihoods.get(h_id, self.smoothing)

            posterior = prior * likelihood
            h.probability = max(self.smoothing, posterior)

        hypothesis_space.renormalize()
        return hypothesis_space

    def soft_update(
        self,
        hypothesis_space: HypothesisSpace,
        question: str,
        answer: bool,
        strength: float = 0.3,
    ) -> HypothesisSpace:
        for h_id, h in hypothesis_space.hypotheses.items():
            if answer:
                factor = 1 + strength
            else:
                factor = 1 - strength

            h.probability = h.probability * factor

        hypothesis_space.renormalize()
        return hypothesis_space

    def entropy_weighted_update(
        self,
        hypothesis_space: HypothesisSpace,
        question: str,
        answer: bool,
        entropy: float,
    ) -> HypothesisSpace:
        current_entropy = hypothesis_space.get_entropy()
        if current_entropy > 0:
            strength = min(0.5, entropy / current_entropy)
        else:
            strength = 0.3

        return self.soft_update(hypothesis_space, question, answer, strength)

    def to_dict(self) -> Dict[str, Any]:
        return {"updater": "ProbabilityUpdater", "smoothing": self.smoothing}
