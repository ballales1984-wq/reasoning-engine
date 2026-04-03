import math


class InformationGain:
    def __init__(self, space):
        self.space = space

    def entropy(self, hypotheses) -> float:
        total = sum(self.space.priors.get(h, 0.0) for h in hypotheses)
        if total == 0:
            return 0.0
        e = 0.0
        for h in hypotheses:
            p = self.space.priors.get(h, 0.0)
            if p > 0:
                ratio = p / total
                e -= ratio * math.log2(ratio)
        return e

    def _expected_entropy(self, feature):
        active = list(self.space.active)
        total = sum(self.space.priors.get(h, 0.0) for h in active)
        if total == 0:
            return 0.0

        groups = {}
        for h in active:
            value = self.space.hypotheses[h].get(feature)
            groups.setdefault(value, set()).add(h)

        expected = 0.0
        for _, hs in groups.items():
            weight = sum(self.space.priors.get(g, 0.0) for g in hs) / total
            expected += weight * self.entropy(hs)
        return expected

    def best_question(self, questions):
        if not questions:
            return None
        base = self.entropy(self.space.active)
        return max(questions, key=lambda q: base - self._expected_entropy(q))
