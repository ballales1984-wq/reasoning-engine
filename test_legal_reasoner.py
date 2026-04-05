import math
from typing import Dict, List, Any, Optional


class HypothesisSpace:
    def __init__(
        self,
        hypotheses: Dict[str, Dict[str, Any]],
        priors: Dict[str, float] | None = None,
    ):
        self.hypotheses = hypotheses
        self.names = {hid: hid.replace("_", " ").title() for hid in hypotheses}
        self.active = set(hypotheses.keys())

        if priors is None:
            uniform = 1.0 / len(hypotheses)
            self.priors = {hid: uniform for hid in hypotheses}
        else:
            self.priors = {hid: float(priors.get(hid, 0.0)) for hid in hypotheses}

        self.renormalize()

    def renormalize(self):
        active_probs = [self.priors[hid] for hid in self.active]
        total = sum(active_probs)

        if total <= 1e-10:
            uniform = 1.0 / max(1, len(self.active))
            for hid in self.active:
                self.priors[hid] = uniform
        else:
            for hid in list(self.priors.keys()):
                if hid in self.active:
                    self.priors[hid] /= total
                else:
                    self.priors[hid] = 0.0

    def filter(self, feature: str, value: Any):
        to_remove = []
        for hid in self.active:
            hyp_features = self.hypotheses[hid]
            if hyp_features.get(feature) != value:
                to_remove.append(hid)

        for hid in to_remove:
            self.active.discard(hid)
            self.priors[hid] = 0.0

        self.renormalize()

    def get_probabilities(self) -> Dict[str, float]:
        return {hid: self.priors[hid] for hid in self.active if self.priors[hid] > 1e-8}

    def entropy(self) -> float:
        probs = [p for p in self.priors.values() if p > 1e-10]
        if not probs:
            return 0.0
        return -sum(p * math.log2(p) for p in probs)

    def remaining_count(self) -> int:
        return len(self.active)

    def get_top_hypothesis(self) -> Optional[Dict[str, Any]]:
        if not self.active:
            return None
        probs = self.get_probabilities()
        if not probs:
            return None
        top_id = max(probs, key=probs.get)
        return {"id": top_id, "name": self.names[top_id], "probability": probs[top_id]}

    def features(self) -> List[str]:
        feat_set = set()
        for hid in self.active:
            feat_set.update(self.hypotheses[hid].keys())
        return list(feat_set)


class QuestionGenerator:
    def __init__(self, space: HypothesisSpace):
        self.space = space
        self.feature_names = {
            "contestazione_scritta": "E stata inviata la contestazione scritta?",
            "audizione_difensiva": "Il lavoratore e stato sentito in audizione difensiva?",
            "recidiva": "C'e recidiva specifica documentata?",
            "sproporzione_sanzione": "Esiste sproporzione tra fatto e sanzione?",
        }

    def generate(self) -> List[str]:
        return list(self.space.features())

    def get_question_text(self, feature: str) -> str:
        return self.feature_names.get(
            feature, feature.replace("_", " ").capitalize() + "?"
        )


class InformationGain:
    def __init__(self, space: HypothesisSpace):
        self.space = space

    def calculate(self, feature: str) -> float:
        current_entropy = self.space.entropy()

        yes_count = 0.0
        no_count = 0.0
        yes_probs = {}
        no_probs = {}

        for hid in self.space.active:
            p = self.space.priors[hid]
            val = self.space.hypotheses[hid].get(feature)

            if val is True or val == "Si" or val == 1:
                yes_probs[hid] = p
                yes_count += p
            else:
                no_probs[hid] = p
                no_count += p

        yes_entropy = 0.0
        if yes_count > 1e-10:
            yes_entropy = -sum(
                (p / yes_count) * math.log2(p / yes_count)
                for p in yes_probs.values()
                if p > 1e-10
            )

        no_entropy = 0.0
        if no_count > 1e-10:
            no_entropy = -sum(
                (p / no_count) * math.log2(p / no_count)
                for p in no_probs.values()
                if p > 1e-10
            )

        expected_entropy = (yes_count * yes_entropy) + (no_count * no_entropy)
        return current_entropy - expected_entropy

    def best_question(self, features: List[str]) -> Optional[str]:
        if not features:
            return None
        return max(features, key=lambda f: self.calculate(f))


class QuestionReasoner:
    def __init__(
        self,
        space: HypothesisSpace,
        max_iterations: int = 10,
        confidence_threshold: float = 0.90,
    ):
        self.space = space
        self.gen = QuestionGenerator(space)
        self.sel = InformationGain(space)
        self.max_iterations = max_iterations
        self.confidence_threshold = confidence_threshold
        self.history = []

    def run(self, answers: Dict[str, bool]) -> Dict[str, Any]:
        for iteration in range(self.max_iterations):
            top = self.space.get_top_hypothesis()

            if top and top["probability"] >= self.confidence_threshold:
                return {
                    "status": "SUCCESS",
                    "answer": top["name"],
                    "confidence": top["probability"],
                    "iterations": iteration + 1,
                }

            if self.space.remaining_count() == 1:
                top = self.space.get_top_hypothesis()
                return {
                    "status": "SUCCESS",
                    "answer": top["name"],
                    "confidence": top["probability"],
                    "iterations": iteration + 1,
                }

            features = self.gen.generate()
            best_feature = self.sel.best_question(features)

            if best_feature is None:
                return {
                    "status": "NO_MORE_QUESTIONS",
                    "answer": None,
                    "confidence": 0.0,
                    "iterations": iteration + 1,
                }

            value = answers.get(best_feature, False)
            self.space.filter(best_feature, value)

            self.history.append(
                {
                    "iteration": iteration + 1,
                    "feature": best_feature,
                    "answer": value,
                    "probabilities": self.space.get_probabilities(),
                }
            )

        top = self.space.get_top_hypothesis()
        return {
            "status": "MAX_ITERATIONS",
            "answer": top["name"] if top else None,
            "confidence": top["probability"] if top else 0.0,
            "iterations": self.max_iterations,
        }


if __name__ == "__main__":
    legal_hypotheses = {
        "legittimo": {
            "contestazione_scritta": True,
            "audizione_difensiva": True,
            "recidiva": True,
            "sproporzione_sanzione": False,
        },
        "illegittimo": {
            "contestazione_scritta": True,
            "audizione_difensiva": False,
            "recidiva": False,
            "sproporzione_sanzione": True,
        },
        "nullo_procedura": {
            "contestazione_scritta": True,
            "audizione_difensiva": False,
            "recidiva": False,
            "sproporzione_sanzione": False,
        },
        "giustificato_oggettivo": {
            "contestazione_scritta": True,
            "audizione_difensiva": True,
            "recidiva": False,
            "sproporzione_sanzione": False,
        },
    }

    priors = {
        "legittimo": 0.42,
        "illegittimo": 0.28,
        "nullo_procedura": 0.15,
        "giustificato_oggettivo": 0.10,
    }

    space = HypothesisSpace(legal_hypotheses, priors)

    print("=== STATO INIZIALE ===")
    for hid, prob in space.get_probabilities().items():
        print(f"  {hid}: {prob:.1%}")
    print(f"Entropia: {space.entropy():.4f} bit\n")

    features = space.features()
    print("=== INFORMATION GAIN ===")
    sel = InformationGain(space)
    for f in features:
        ig = sel.calculate(f)
        print(f"  {f}: {ig:.4f}")

    best = sel.best_question(features)
    print(f"\nMigliore domanda: {best}\n")

    print("=== SIMULAZIONE RISPOSTE ===")
    answers = {"audizione_difensiva": False, "sproporzione_sanzione": True}
    print(f"Risposte: {answers}")

    space2 = HypothesisSpace(legal_hypotheses, priors)
    reasoner = QuestionReasoner(space2)
    result = reasoner.run(answers)

    print(f"\n=== RISULTATO ===")
    print(f"Status: {result['status']}")
    print(f"Conclusione: {result['answer']}")
    print(f"Confidenza: {result['confidence']:.1%}")
    print(f"Iterazioni: {result['iterations']}")
