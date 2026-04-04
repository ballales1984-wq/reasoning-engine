import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from engine.agents.critic import (
    CriticAgent,
    _keyword_overlap_score,
    _entity_match_score,
    _grounding_score,
    _tokenize,
    _extract_entities_from_text,
)


def test_keyword_overlap_high():
    query = "Qual è la capitale della Francia"
    answer = "La capitale della Francia è Parigi"
    score = _keyword_overlap_score(query, answer)
    assert score > 0.5, f"Overlap alto atteso, ottenuto {score}"


def test_keyword_overlap_low():
    query = "Qual è la capitale del Giappone"
    answer = "Il meteo oggi è soleggiato a Milano"
    score = _keyword_overlap_score(query, answer)
    assert score < 0.2, f"Overlap basso atteso, ottenuto {score}"


def test_entity_match():
    query = "Tokyo è la capitale del Giappone"
    answer = "Giappone ha Tokyo come capitale"
    score = _entity_match_score(query, answer)
    assert score > 0.3, f"Entity match atteso, ottenuto {score}"


def test_critic_approves_good_answer():
    critic = CriticAgent()
    input_data = {
        "query": "Qual è la capitale della Francia?",
        "draft_answer": "La capitale della Francia è Parigi.",
        "accumulated_data": [
            {
                "source": "knowledge_graph",
                "content": {
                    "Francia": _mock_concept(
                        "Francia", "Stato europeo", {"capitale": "Parigi"}
                    ),
                },
            }
        ],
    }
    result = critic.process(input_data)
    assert result["status"] == "approved", (
        f"Expected approved, got {result['status']}: {result['critic_feedback']}"
    )
    assert result["final_confidence"] >= 0.6


def test_critic_rejects_generic():
    critic = CriticAgent()
    input_data = {
        "query": "Qual è la capitale della Francia?",
        "draft_answer": "Non ho trovato informazioni dirette.",
        "accumulated_data": [],
    }
    result = critic.process(input_data)
    assert result["status"] == "rejected"


def test_critic_needs_retry_low_pertinence():
    critic = CriticAgent()
    input_data = {
        "query": "Qual è la capitale del Giappone?",
        "draft_answer": "Il meteo oggi è bello a Roma e fa caldo.",
        "accumulated_data": [
            {
                "source": "knowledge_graph",
                "content": {
                    "Giappone": _mock_concept(
                        "Giappone", "Stato asiatico", {"capitale": "Tokyo"}
                    ),
                },
            }
        ],
    }
    result = critic.process(input_data)
    assert result["status"] in ("needs_retry", "rejected"), (
        f"Expected retry/reject, got {result['status']}"
    )


def test_critic_needs_retry_too_short():
    critic = CriticAgent()
    input_data = {
        "query": "Spiega la teoria della relatività",
        "draft_answer": "E=mc²",
        "accumulated_data": [
            {
                "source": "vector_memory",
                "content": [
                    {"text": "La relatività di Einstein rivoluzionò la fisica moderna"}
                ],
            },
        ],
    }
    result = critic.process(input_data)
    assert result["status"] == "needs_retry"


def test_grounding_with_kg():
    draft = "La capitale della Francia è Parigi"
    accumulated = [
        {
            "source": "knowledge_graph",
            "content": {
                "Francia": _mock_concept(
                    "Francia", "Stato europeo con capitale Parigi"
                ),
            },
        }
    ]
    score = _grounding_score(draft, accumulated)
    assert score > 0.1, f"Grounding atteso da KG, ottenuto {score}"


def test_grounding_empty():
    score = _grounding_score("La risposta è nulla", [])
    assert score == 0.0


def _mock_concept(name: str, description: str, relations: dict = None):
    class _MockConcept:
        def __init__(self, n, d, r=None):
            self.name = n
            self._description = d
            self._examples = []
            self.relations = r or {}

        def get_best_info(self):
            return {
                "description": self._description,
                "examples": self._examples,
                "category": "test",
            }

    return _MockConcept(name, description, relations)
