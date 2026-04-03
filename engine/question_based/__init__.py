from .hypothesis_space import HypothesisSpace, Hypothesis
from .question_generator import QuestionGenerator
from .information_gain import InformationGain, InformationGainSelector
from .probability_updater import (
    ProbabilityUpdater,
    SoftProbabilityUpdater,
    AnswerConfidence,
)
from .question_reasoner import QuestionReasoner, ReasoningStatus
from .explainer import Explainer
from .kg_bridge import KnowledgeGraphBridge
from .kg_bridge import KGBridge
from .llm_extractor import LLMFeatureExtractor, LLMExtractor
from .auto_researcher import AutoResearcher


def create_space_from_knowledge(kg, names, features=None):
    bridge = KnowledgeGraphBridge(kg)
    return bridge.build_hypothesis_space(names, features=features)


__all__ = [
    "HypothesisSpace",
    "Hypothesis",
    "QuestionGenerator",
    "InformationGain",
    "InformationGainSelector",
    "QuestionReasoner",
    "Explainer",
    "ProbabilityUpdater",
    "SoftProbabilityUpdater",
    "AnswerConfidence",
    "ReasoningStatus",
    "KnowledgeGraphBridge",
    "KGBridge",
    "LLMFeatureExtractor",
    "LLMExtractor",
    "AutoResearcher",
    "create_space_from_knowledge",
]
