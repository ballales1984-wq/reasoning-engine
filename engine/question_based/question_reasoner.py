from typing import List, Dict, Any, Optional, Callable
import json
from .hypothesis_space import HypothesisSpace, Hypothesis
from .question_generator import QuestionGenerator
from .information_gain import InformationGainSelector
from .probability_updater import ProbabilityUpdater
from .explainer import Explainer


class QuestionReasoner:
    def __init__(
        self,
        domain: str = "general",
        max_iterations: int = 10,
        confidence_threshold: float = 0.85,
        llm_provider: Optional[Callable] = None,
    ):
        self.domain = domain
        self.max_iterations = max_iterations
        self.confidence_threshold = confidence_threshold
        self.llm_provider = llm_provider

        self.hypothesis_space = HypothesisSpace(domain)
        self.question_generator = QuestionGenerator(domain)
        self.selector = InformationGainSelector()
        self.updater = ProbabilityUpdater()
        self.explainer = Explainer()

        self.trace: List[Dict[str, Any]] = []

    def add_hypotheses(self, hypotheses: List[Dict[str, Any]]):
        for h in hypotheses:
            hypothesis = Hypothesis(
                id=h["id"],
                name=h["name"],
                probability=h.get("probability", 1.0 / len(hypotheses)),
                features=h.get("features", {}),
                evidence=h.get("evidence", []),
            )
            self.hypothesis_space.add_hypothesis(hypothesis)
        self.hypothesis_space.renormalize()

    def step(self, question: str, answer: bool) -> Dict[str, Any]:
        top = self.hypothesis_space.get_top_hypothesis()
        confidence = top.probability if top else 0

        self.updater.soft_update(self.hypothesis_space, question, answer, strength=0.5)

        new_top = self.hypothesis_space.get_top_hypothesis()
        new_confidence = new_top.probability if new_top else 0

        step_result = {
            "question": question,
            "answer": answer,
            "top_hypothesis": new_top.name if new_top else None,
            "confidence": new_confidence,
            "entropy": self.hypothesis_space.get_entropy(),
        }

        self.trace.append(step_result)
        self.explainer.add_step(step_result)

        return step_result

    def generate_next_question(self) -> Optional[str]:
        candidates = self.question_generator.get_questions(self.domain)

        if not candidates:
            return None

        if self.llm_provider and self.hypothesis_space.all_hypotheses():
            features = list(self.hypothesis_space.all_hypotheses()[0].features.keys())
            if features:
                return self.question_generator.generate_question(
                    features[0], self.domain
                )

        return candidates[len(self.trace) % len(candidates)]

    def run(self, ask_callback: Callable[[str], bool]) -> Dict[str, Any]:
        for i in range(self.max_iterations):
            top = self.hypothesis_space.get_top_hypothesis()

            if top and top.probability >= self.confidence_threshold:
                return {
                    "result": top,
                    "iterations": i + 1,
                    "trace": self.trace,
                    "explanation": self.explainer.get_summary(),
                }

            question = self.generate_next_question()
            if not question:
                break

            answer = ask_callback(question)
            self.step(question, answer)

        return {
            "result": self.hypothesis_space.get_top_hypothesis(),
            "iterations": self.max_iterations,
            "trace": self.trace,
            "explanation": self.explainer.get_summary(),
        }

    def to_dict(self) -> Dict[str, Any]:
        return {
            "domain": self.domain,
            "max_iterations": self.max_iterations,
            "confidence_threshold": self.confidence_threshold,
            "hypothesis_space": self.hypothesis_space.to_dict(),
            "trace": self.trace,
        }
