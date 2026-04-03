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


class InformationGainSelector:
    # Legacy adapter expected by older tests.
    def calculate_entropy(self, probabilities):
        total = sum(probabilities)
        if total <= 0:
            return 0.0
        e = 0.0
        for p in probabilities:
            if p > 0:
                ratio = p / total
                e -= ratio * math.log2(ratio)
        return e

    def calculate_information_gain(self, hypothesis_space, question, yes_map, no_map):
        priors = [hypothesis_space.priors.get(h, 0.0) for h in hypothesis_space.remaining()]
        base = self.calculate_entropy(priors)
        yes_probs = [hypothesis_space.priors.get(h, 0.0) * float(yes_map.get(h, 0.0)) for h in hypothesis_space.remaining()]
        no_probs = [hypothesis_space.priors.get(h, 0.0) * float(no_map.get(h, 0.0)) for h in hypothesis_space.remaining()]
        py = sum(yes_probs)
        pn = sum(no_probs)
        total = py + pn
        if total <= 0:
            return 0.0
        expected = (py / total) * self.calculate_entropy(yes_probs) + (pn / total) * self.calculate_entropy(no_probs)
        gain = base - expected
        return max(0.0, gain)
