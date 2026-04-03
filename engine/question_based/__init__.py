"""
Question-Based Reasoner Module

A reasoning engine that thinks by asking questions, eliminating hypotheses,
and arriving at a single conclusion through iterative inquiry.

Components:
- HypothesisSpace: manages hypotheses, features, probabilities
- QuestionGenerator: generates useful questions based on differences
- InformationGain: selects best question using entropy
- ProbabilityUpdater: updates probabilities (soft Bayesian)
- QuestionReasoner: main loop (generate → select → answer → update → repeat)
- Explainer: tracks reasoning path and produces final explanation
- KnowledgeGraphBridge: connects to existing KnowledgeGraph

Features:
- Soft probability updates (not brutal elimination)
- Confidence threshold for stop conditions
- Support for unknown/maybe answers
- Ambiguous/inconsistent state detection
- Integration with KnowledgeGraph
"""

from .hypothesis_space import HypothesisSpace
from .question_generator import QuestionGenerator
from .information_gain import InformationGain
from .probability_updater import ProbabilityUpdater, SoftProbabilityUpdater, AnswerConfidence
from .question_reasoner import QuestionReasoner, ReasoningStatus, AnswerType
from .explainer import Explainer
from .kg_bridge import KnowledgeGraphBridge, create_space_from_knowledge
from .llm_extractor import LLMFeatureExtractor, FeatureType
from .auto_researcher import AutoResearcher

__all__ = [
    # Core
    "HypothesisSpace",
    "QuestionGenerator",
    "InformationGain",
    "QuestionReasoner",
    "Explainer",
    # Probability (soft update)
    "ProbabilityUpdater",
    "SoftProbabilityUpdater",
    "AnswerConfidence",
    # Status enums
    "ReasoningStatus",
    "AnswerType",
    # Knowledge Graph Bridge
    "KnowledgeGraphBridge",
    "create_space_from_knowledge",
    # LLM Feature Extractor
    "LLMFeatureExtractor",
    "FeatureType",
    # Auto Researcher
    "AutoResearcher",
]