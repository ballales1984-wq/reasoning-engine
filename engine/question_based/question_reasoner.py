from enum import Enum

from .question_generator import QuestionGenerator
from .information_gain import InformationGain
from .probability_updater import ProbabilityUpdater, AnswerConfidence
from .explainer import Explainer
from .hypothesis_space import HypothesisSpace


class ReasoningStatus(Enum):
    SUCCESS = "success"
    AMBIGUOUS = "ambiguous"
    UNDECIDABLE = "undecidable"
    INCONSISTENT = "inconsistent"


class QuestionReasoner:
    def __init__(
        self,
        space=None,
        confidence_threshold=0.95,
        ambiguity_threshold=0.15,
        domain=None,
        max_iterations=20,
    ):
        # Backward compatible: QuestionReasoner(domain="animals", ...)
        if isinstance(space, HypothesisSpace):
            self.space = space
        else:
            self.space = HypothesisSpace(domain or "default")
        self.conf = float(confidence_threshold)
        self.ambiguity_threshold = float(ambiguity_threshold)
        self.max_iterations = int(max_iterations)
        self.gen = QuestionGenerator(self.space)
        self.sel = InformationGain(self.space)
        self.upd = ProbabilityUpdater(self.space)
        self.exp = Explainer()
        self.trace = []
        self.hypothesis_space = self.space

    def add_hypotheses(self, hypotheses):
        for item in hypotheses:
            h_id = item.get("id") or item.get("name")
            if not h_id:
                continue
            self.space.hypotheses[h_id] = dict(item.get("features", {}))
            self.space.names[h_id] = item.get("name", h_id)
            self.space.priors[h_id] = float(item.get("probability", 0.0))
            self.space.active.add(h_id)
        self.space.renormalize()
        self.hypothesis_space = self.space

    def generate_next_question(self):
        questions = self.gen.generate()
        return self.sel.best_question(questions)

    def step(self, question, answer, confidence=AnswerConfidence.HIGH):
        value = answer
        conf = confidence
        if isinstance(answer, tuple) and len(answer) == 2:
            value, conf = answer
        if value not in ("unknown", "maybe"):
            self.space.filter(question, value)
        self.upd.update(question, value, conf if isinstance(conf, AnswerConfidence) else AnswerConfidence.HIGH)
        top = self.space.get_top_hypothesis()
        snap = {
            "question": question,
            "answer": value,
            "top_hypothesis": top.name if top else None,
            "confidence": top.probability if top else 0.0,
        }
        self.trace.append(snap)
        self.exp.log(question, value, self.space.active, self.space.priors)
        return snap

    def run(self, answer_callback, max_iter=None):
        limit = max_iter if max_iter is not None else self.max_iterations
        for _ in range(limit):
            questions = self.gen.generate()
            if not questions:
                break

            q = self.sel.best_question(questions)
            if q is None:
                break

            a = answer_callback(q)
            self.step(q, a)

            if len(self.space.remaining()) <= 1:
                break

        result = self.exp.build(self.space)
        result.update(self._status_payload())
        top = self.space.get_top_hypothesis()
        result["result"] = top
        return result

    def _status_payload(self):
        remaining = self.space.remaining()
        if not remaining:
            return {"status": ReasoningStatus.INCONSISTENT.value, "message": "Nessuna ipotesi compatibile con le risposte."}

        top = self.space.get_top_hypothesis()
        if top is None:
            return {"status": ReasoningStatus.UNDECIDABLE.value, "message": "Impossibile determinare un'ipotesi finale."}

        if top.probability >= self.conf or len(remaining) == 1:
            return {"status": ReasoningStatus.SUCCESS.value, "message": "Conclusione raggiunta con confidenza sufficiente."}

        if len(remaining) > 1:
            sorted_probs = sorted([self.space.priors.get(h, 0.0) for h in remaining], reverse=True)
            if len(sorted_probs) >= 2 and (sorted_probs[0] - sorted_probs[1]) <= self.ambiguity_threshold:
                return {"status": ReasoningStatus.AMBIGUOUS.value, "message": "Più ipotesi restano plausibili con probabilità simili."}
        return {"status": ReasoningStatus.UNDECIDABLE.value, "message": "Ragionamento terminato senza confidenza sufficiente."}
