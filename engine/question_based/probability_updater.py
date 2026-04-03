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

    def __init__(self, space=None, smoothing=0.01):
        self.space = space
        self.smoothing = float(smoothing)

    def update(self, feature, value, conf=AnswerConfidence.HIGH):
        if self.space is None:
            return
        if value in ("unknown", "maybe", None):
            self._normalize(self.space)
            return

        penalty = self.PENALTY[conf]
        for h in list(self.space.hypotheses.keys()):
            if h not in self.space.active:
                self.space.priors[h] = 0.0
                continue
            if self.space.hypotheses[h].get(feature) != value:
                newp = self.space.priors.get(h, 0.0) * penalty
                self.space.priors[h] = max(0.0, newp)

        self.space.active = {h for h in self.space.active if self.space.priors.get(h, 0.0) > 0.01}
        self._normalize(self.space)

    def _normalize(self, space):
        total = sum(space.priors.get(h, 0.0) for h in space.active)
        if total:
            for h in list(space.active):
                space.priors[h] = space.priors[h] / total
            for h in list(space.hypotheses.keys()):
                if h not in space.active:
                    space.priors[h] = 0.0
        elif space.active:
            uniform = 1.0 / len(space.active)
            for h in list(space.hypotheses.keys()):
                space.priors[h] = uniform if h in space.active else 0.0

    # Backward-compatible API expected by old tests.
    def soft_update(self, hypothesis_space, question, answer, strength=0.3):
        feature, expected = self._extract_feature_from_question(question)
        effective = expected if isinstance(answer, bool) and answer else (not expected if isinstance(expected, bool) else answer)
        if effective == "unknown":
            return
        backup = self.space
        self.space = hypothesis_space
        self.update(feature, effective, AnswerConfidence.LOW if strength > 0 else AnswerConfidence.HIGH)
        self.space = backup

    def _extract_feature_from_question(self, question):
        q = (question or "").lower()
        mapping = {
            "domestico": "domestico",
            "coda": "coda_lunga",
            "caldo": "caldo",
            "primario": "primario",
            "team": "team",
            "palla": "palla",
            "rosso": "colore",
            "colore": "colore",
        }
        for k, v in mapping.items():
            if k in q:
                return v, True
        return "unknown", True


ProbabilityUpdater = SoftProbabilityUpdater
