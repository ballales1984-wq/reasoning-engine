from typing import Dict, List, Any, Optional
import math


class HypothesisSpace:
    def __init__(
        self, hypotheses: Dict[str, Dict[str, Any]], priors: Dict[str, float] = None
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
            if self.hypotheses[hid].get(feature) != value:
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


class Question:
    def __init__(
        self,
        feature: str,
        text: str,
        qtype: str,
        possible_values: List[Any],
        importance: float,
    ):
        self.feature = feature
        self.text = text
        self.type = qtype
        self.possible_values = possible_values
        self.importance = importance


class QuestionGenerator:
    def __init__(self, space: HypothesisSpace):
        self.space = space
        self.templates = {
            "contestazione_scritta": "E stata inviata la contestazione scritta al lavoratore?",
            "audizione_difensiva": "Il lavoratore e stato sentito in audizione difensiva?",
            "recidiva": "Esiste recidiva specifica e documentata?",
            "sproporzione_sanzione": "Esiste sproporzione tra il fatto e la sanzione?",
            "termine_5_giorni": "La contestazione e stata notificata entro 5 giorni?",
            "prova_grave": "Esistono prove gravi e concordanti?",
            "crisi_aziendale": "Il licenziamento e per crisi aziendale?",
        }

    def generate(self, max_questions: int = 6) -> List[Question]:
        questions = []
        varying = self._get_varying_features()

        for feat in varying[:max_questions]:
            text = self.templates.get(feat, feat.replace("_", " ").capitalize() + "?")
            values = self._get_values(feat)
            qtype = "yes_no" if self._is_bool(values) else "choice"
            importance = self._importance(feat)
            questions.append(Question(feat, text, qtype, values, importance))

        return sorted(questions, key=lambda q: q.importance, reverse=True)

    def _get_varying_features(self) -> List[str]:
        all_feats = set()
        for hid in self.space.active:
            all_feats.update(self.space.hypotheses[hid].keys())
        varying = []
        for f in all_feats:
            vals = {self.space.hypotheses[hid].get(f) for hid in self.space.active}
            if len(vals) > 1:
                varying.append(f)
        return varying

    def _get_values(self, feature: str) -> List[Any]:
        vals = set()
        for hid in self.space.active:
            v = self.space.hypotheses[hid].get(feature)
            if v is not None:
                vals.add(v)
        return sorted(list(vals), key=str)

    def _is_bool(self, values: List[Any]) -> bool:
        return all(v in [True, False, 1, 0] for v in values)

    def _importance(self, feature: str) -> float:
        m = {
            "audizione_difensiva": 0.95,
            "contestazione_scritta": 0.90,
            "sproporzione_sanzione": 0.75,
            "recidiva": 0.70,
        }
        return m.get(feature, 0.5)

    def get_best_question(self) -> Optional[Question]:
        qs = self.generate(8)
        return qs[0] if qs else None


class InformationGain:
    def __init__(self, space: HypothesisSpace):
        self.space = space

    def calculate(self, feature: str) -> float:
        current = self.space.entropy()

        yes_cnt = 0.0
        no_cnt = 0.0
        yes_p = {}
        no_p = {}

        for hid in self.space.active:
            p = self.space.priors[hid]
            v = self.space.hypotheses[hid].get(feature)

            if v is True or v == 1:
                yes_p[hid] = p
                yes_cnt += p
            else:
                no_p[hid] = p
                no_cnt += p

        yes_entropy = 0.0
        if yes_cnt > 1e-10:
            yes_entropy = -sum(
                (p / yes_cnt) * math.log2(p / yes_cnt)
                for p in yes_p.values()
                if p > 1e-10
            )

        no_entropy = 0.0
        if no_cnt > 1e-10:
            no_entropy = -sum(
                (p / no_cnt) * math.log2(p / no_cnt) for p in no_p.values() if p > 1e-10
            )

        return current - (yes_cnt * yes_entropy + no_cnt * no_entropy)

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

    def run(self, answer_callback) -> Dict[str, Any]:
        for iteration in range(self.max_iterations):
            top = self.space.get_top_hypothesis()

            if top and top["probability"] >= self.confidence_threshold:
                return {
                    "status": "SUCCESS",
                    "answer": top["name"],
                    "confidence": top["probability"],
                    "iterations": iteration + 1,
                    "history": self.history,
                }

            if self.space.remaining_count() == 1:
                top = self.space.get_top_hypothesis()
                return {
                    "status": "SUCCESS",
                    "answer": top["name"],
                    "confidence": top["probability"],
                    "iterations": iteration + 1,
                    "history": self.history,
                }

            features = [q.feature for q in self.gen.generate(8)]
            best_feat = self.sel.best_question(features)

            if best_feat is None:
                return {
                    "status": "NO_QUESTIONS",
                    "answer": None,
                    "confidence": 0.0,
                    "iterations": iteration + 1,
                    "history": self.history,
                }

            question = self.templates.get(
                best_feat, best_feat.replace("_", " ").capitalize() + "?"
            )
            answer = answer_callback(question, best_feat)

            self.space.filter(best_feat, answer)
            self.history.append(
                {"iteration": iteration + 1, "feature": best_feat, "answer": answer}
            )

        return {
            "status": "MAX_ITERATIONS",
            "answer": self.space.get_top_hypothesis()["name"],
            "confidence": self.space.get_top_hypothesis()["probability"],
            "iterations": self.max_iterations,
            "history": self.history,
        }

    @property
    def templates(self) -> Dict[str, str]:
        return self.gen.templates


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
    reasoner = QuestionReasoner(space, confidence_threshold=0.90)

    print("=== SISTEMA ESPERTO LEGALE ===")
    print(
        f"Stato iniziale: {space.remaining_count()} ipotesi, entropia {space.entropy():.4f} bit\n"
    )

    questions = reasoner.gen.generate(5)
    print("Domande generate:")
    for q in questions:
        print(f"  - [{q.type}] {q.text} (importanza: {q.importance:.2f})")

    print("\n=== CALCOLO INFORMATION GAIN ===")
    for q in questions:
        ig = reasoner.sel.calculate(q.feature)
        print(f"  {q.feature}: IG = {ig:.4f}")

    print("\n=== SIMULAZIONE (risposte chiuse) ===")
    answers = {"audizione_difensiva": False, "sproporzione_sanzione": True}
    result = reasoner.run(lambda q, f: answers.get(f, False))
    print(f"Risultato: {result['status']}")
    print(f"Conclusione: {result['answer']}")
    print(f"Confidenza: {result['confidence']:.1%}")
