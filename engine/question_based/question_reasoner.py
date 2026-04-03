from enum import Enum

from .question_generator import QuestionGenerator
from .information_gain import InformationGain
from .probability_updater import ProbabilityUpdater
from .explainer import Explainer


class ReasoningStatus(Enum):
    SUCCESS = "success"
    AMBIGUOUS = "ambiguous"
    UNDECIDABLE = "undecidable"
    INCONSISTENT = "inconsistent"


class QuestionReasoner:
    def __init__(self, space, confidence_threshold=0.95):
        self.space = space
        self.conf = confidence_threshold
        self.gen = QuestionGenerator(space)
        self.sel = InformationGain(space)
        self.upd = ProbabilityUpdater(space)
        self.exp = Explainer()

    def run(self, answer_callback, max_iter=20):
        for _ in range(max_iter):
            questions = self.gen.generate()
            if not questions:
                break

            q = self.sel.best_question(questions)
            if q is None:
                break

            a = answer_callback(q)
            self.exp.log(q, a, self.space.active, self.space.priors)

            self.space.filter(q, a)
            self.upd.update(q, a)

            if len(self.space.remaining()) <= 1:
                break

        return self.exp.build(self.space)
