import math
import random
from typing import Dict, List, Any, Optional, Callable


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
        return {
            "id": top_id,
            "name": self.names[top_id],
            "probability": probs[top_id],
            "features": self.hypotheses[top_id],
        }

    def features(self) -> List[str]:
        feat_set = set()
        for hid in self.active:
            feat_set.update(self.hypotheses[hid].keys())
        return list(feat_set)


class QuestionGenerator:
    """Genera domande basate sulle feature dello spazio delle ipotesi."""

    def __init__(self, space: HypothesisSpace):
        self.space = space
        self.feature_names = {
            "contestazione_scritta": "È stata inviata la contestazione scritta?",
            "audizione_difensiva": "Il lavoratore è stato sentito in audizione difensiva?",
            "recidiva": "C'è recidiva specifica documentata?",
            "sproporzione_sanzione": "Esiste sproporzione tra fatto e sanzione?",
            "crisi_aziendale": "C'è una crisi aziendale documentata?",
        }

    def generate(self) -> List[str]:
        """Genera domande per tutte le feature che variano tra le ipotesi."""
        questions = []
        for feature in self.space.features():
            questions.append(feature)
        return questions

    def get_question_text(self, feature: str) -> str:
        return self.feature_names.get(
            feature, feature.replace("_", " ").capitalize() + "?"
        )


class InformationGain:
    """Calcola Information Gain per selezionare la migliore domanda."""

    def __init__(self, space: HypothesisSpace):
        self.space = space

    def calculate(self, feature: str) -> float:
        current_entropy = self.space.entropy()

        yes_count = 0.0
        no_count = 0.0
        yes_probs: Dict[str, float] = {}
        no_probs: Dict[str, float] = {}

        for hid in self.space.active:
            p = self.space.priors[hid]
            val = self.space.hypotheses[hid].get(feature)

            if val is True or val == "Sì" or val == 1:
                yes_probs[hid] = p
                yes_count += p
            else:
                no_probs[hid] = p
                no_count += p

        if yes_count > 1e-10:
            yes_entropy = -sum(
                (p / yes_count) * math.log2(p / yes_count)
                for p in yes_probs.values()
                if p > 1e-10
            )
        else:
            yes_entropy = 0.0

        if no_count > 1e-10:
            no_entropy = -sum(
                (p / no_count) * math.log2(p / no_count)
                for p in no_probs.values()
                if p > 1e-10
            )
        else:
            no_entropy = 0.0

        expected_entropy = (yes_count * yes_entropy) + (no_count * no_entropy)
        return current_entropy - expected_entropy

    def best_question(self, features: List[str]) -> Optional[str]:
        if not features:
            return None
        best = max(features, key=lambda f: self.calculate(f))
        return best


class ProbabilityUpdater:
    """Aggiorna le probabilità dopo una risposta."""

    def __init__(self, space: HypothesisSpace):
        self.space = space

    def update(self, feature: str, value: Any):
        self.space.filter(feature, value)


class QuestionReasoner:
    """
    Motore principale di ragionamento basato su domande.
    Alterna generazione domande → selezione (IG) → risposta → aggiornamento.
    """

    def __init__(
        self,
        space: HypothesisSpace,
        max_iterations: int = 10,
        confidence_threshold: float = 0.90,
    ):
        self.space = space
        self.gen = QuestionGenerator(space)
        self.sel = InformationGain(space)
        self.upd = ProbabilityUpdater(space)
        self.max_iterations = max_iterations
        self.confidence_threshold = confidence_threshold
        self.history: List[Dict[str, Any]] = []

    def run(self, answer_callback: Callable[[str], Any]) -> Dict[str, Any]:
        """
        Esegue il loop di ragionamento.

        Args:
            answer_callback: Funzione che riceve la domanda e restituisce la risposta.
                           Può restituire:
                           - bool/str (es. True, "Sì", "No")
                           - tuple (valore, confidence) es. (True, 0.95)

        Returns:
            Dict con status, risposta finale, confidenza, storia
        """
        for iteration in range(self.max_iterations):
            top = self.space.get_top_hypothesis()

            if top and top["probability"] >= self.confidence_threshold:
                return {
                    "status": "SUCCESS",
                    "answer": top["name"],
                    "confidence": top["probability"],
                    "hypothesis_id": top["id"],
                    "iterations": iteration + 1,
                    "history": self.history,
                }

            if self.space.remaining_count() == 1:
                top = self.space.get_top_hypothesis()
                return {
                    "status": "SUCCESS",
                    "answer": top["name"],
                    "confidence": top["probability"],
                    "hypothesis_id": top["id"],
                    "iterations": iteration + 1,
                    "history": self.history,
                }

            features = self.gen.generate()
            best_feature = self.sel.best_question(features)

            if best_feature is None:
                return {
                    "status": "NO_MORE_QUESTIONS",
                    "answer": self.space.get_top_hypothesis()["name"]
                    if self.space.get_top_hypothesis()
                    else None,
                    "confidence": self.space.get_top_hypothesis()["probability"]
                    if self.space.get_top_hypothesis()
                    else 0.0,
                    "iterations": iteration + 1,
                    "history": self.history,
                }

            question = self.gen.get_question_text(best_feature)

            raw_answer = answer_callback(question)

            value, confidence = self._parse_answer(raw_answer)

            self.history.append(
                {
                    "iteration": iteration + 1,
                    "question": question,
                    "feature": best_feature,
                    "answer": value,
                    "confidence": confidence,
                    "probabilities": self.space.get_probabilities(),
                }
            )

            self.upd.update(best_feature, value)

        top = self.space.get_top_hypothesis()
        return {
            "status": "MAX_ITERATIONS",
            "answer": top["name"] if top else None,
            "confidence": top["probability"] if top else 0.0,
            "iterations": self.max_iterations,
            "history": self.history,
        }

    def _parse_answer(self, answer: Any) -> tuple[Any, float]:
        """Parse della risposta in (valore, confidence)."""
        if isinstance(answer, tuple) and len(answer) == 2:
            return answer[0], float(answer[1])

        if isinstance(answer, bool):
            return answer, 1.0

        if isinstance(answer, str):
            lower = answer.lower().strip()
            if lower in ("sì", "si", "yes", "true", "1", "vero"):
                return True, 1.0
            elif lower in ("no", "false", "0", "falso"):
                return False, 1.0

        return answer, 0.5


def simula_risposta(query: str) -> Any:
    """Simula risposte dell'utente (per test)."""
    print(f"\n>>> DOMANDA: {query}")
    risposta = input("   Risposta (Sì/No): ").strip()
    return risposta


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
    reasoner = QuestionReasoner(space, max_iterations=10, confidence_threshold=0.90)

    print("=" * 60)
    print("SISTEMA ESPERTO LEGALE - LICENZIAMENTO DISCIPLINARE")
    print("=" * 60)
    print(f"\nIpotesi iniziali ({space.remaining_count()}):")
    for hid, prob in space.get_probabilities().items():
        print(f"  - {hid}: {prob:.1%}")
    print(f"Entropia: {space.entropy():.4f} bit\n")

    result = reasoner.run(simula_risposta)

    print("\n" + "=" * 60)
    print("RISULTATO")
    print("=" * 60)
    print(f"Status: {result['status']}")
    print(f"Conclusione: {result['answer']}")
    print(f"Confidenza: {result['confidence']:.1%}")
    print(f"Iterazioni: {result['iterations']}")
