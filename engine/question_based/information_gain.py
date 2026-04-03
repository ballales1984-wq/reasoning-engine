from typing import List, Dict, Any, Optional
import math
from .hypothesis_space import HypothesisSpace, Hypothesis


class InformationGainSelector:
    def __init__(self):
        pass

    def calculate_entropy(self, probabilities: List[float]) -> float:
        filtered = [p for p in probabilities if p > 0]
        if not filtered:
            return 0.0
        return -sum(p * math.log2(p) for p in filtered)

    def calculate_information_gain(
        self,
        hypothesis_space: HypothesisSpace,
        question: str,
        yes_distribution: Dict[str, float],
        no_distribution: Dict[str, float],
    ) -> float:
        current_probs = [h.probability for h in hypothesis_space.all_hypotheses()]
        current_entropy = self.calculate_entropy(current_probs)

        yes_probs = list(yes_distribution.values())
        no_probs = list(no_distribution.values())

        yes_entropy = self.calculate_entropy(yes_probs) if yes_probs else 0
        no_entropy = self.calculate_entropy(no_probs) if no_probs else 0

        yes_weight = sum(yes_probs) if yes_probs else 0
        no_weight = sum(no_probs) if no_probs else 0
        total_weight = yes_weight + no_weight

        if total_weight == 0:
            return 0

        weighted_entropy = (
            yes_weight * yes_entropy + no_weight * no_entropy
        ) / total_weight

        return current_entropy - weighted_entropy

    def select_best_question(
        self,
        hypothesis_space: HypothesisSpace,
        candidates: List[str],
        yes_distributions: Dict[str, Dict[str, float]],
        no_distributions: Dict[str, Dict[str, float]],
    ) -> Optional[str]:
        if not candidates:
            return None

        best_question = None
        best_gain = -1

        for question in candidates:
            yes_dist = yes_distributions.get(question, {})
            no_dist = no_distributions.get(question, {})

            gain = self.calculate_information_gain(
                hypothesis_space, question, yes_dist, no_dist
            )

            if gain > best_gain:
                best_gain = gain
                best_question = question

        return best_question

    def to_dict(self) -> Dict[str, Any]:
        return {"selector": "InformationGainSelector", "method": "entropy-based"}
