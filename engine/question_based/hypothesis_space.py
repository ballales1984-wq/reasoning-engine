class HypothesisSpace:
    def __init__(self, hypotheses: dict, priors: dict = None):
        self.hypotheses = hypotheses
        self.active = set(hypotheses.keys())
        if priors:
            self.priors = priors
        else:
            n = len(hypotheses)
            self.priors = {h: 1.0 / n for h in hypotheses} if n else {}

    def filter(self, feature: str, value):
        self.active = {
            h for h in self.active if self.hypotheses.get(h, {}).get(feature) == value
        }

    def remaining(self):
        return list(self.active)

    def features(self):
        return list(next(iter(self.hypotheses.values())).keys()) if self.hypotheses else []
