"""
Critic Agent — Controllo qualità e verifica della verità.
"""

import re
from typing import Any, Dict, List, Set
from .base import BaseAgent


_STOPWORDS_IT: Set[str] = {
    "il",
    "lo",
    "la",
    "i",
    "gli",
    "le",
    "un",
    "uno",
    "una",
    "di",
    "a",
    "da",
    "in",
    "con",
    "su",
    "per",
    "tra",
    "fra",
    "e",
    "o",
    "che",
    "è",
    "del",
    "della",
    "delle",
    "dei",
    "degli",
    "al",
    "alla",
    "ai",
    "agli",
    "dal",
    "dalla",
    "dai",
    "dagli",
    "nel",
    "nella",
    "nei",
    "negli",
    "sul",
    "sulla",
    "sui",
    "sulle",
    "non",
    "si",
    "no",
    "mi",
    "ti",
    "ci",
    "vi",
    "lo",
    "la",
    "li",
    "le",
    "ne",
    "un",
    "una",
    "uno",
    "e",
    "ed",
    "o",
    "od",
    "ma",
    "se",
    "perché",
    "come",
    "dove",
    "quando",
    "quanto",
    "quale",
    "quali",
    "cosa",
    "chi",
    "cui",
    "sono",
    "ho",
    "hai",
    "ha",
    "abbiamo",
    "avete",
    "hanno",
    "fatto",
    "dire",
    "fare",
    "essere",
    "avere",
    "puoi",
    "sai",
    "so",
    "sta",
    "sto",
    "stai",
    "the",
    "is",
    "are",
    "was",
    "were",
    "of",
    "and",
    "or",
    "a",
    "an",
    "in",
    "to",
    "for",
    "on",
    "at",
    "by",
    "with",
    "from",
    "it",
    "this",
    "that",
    "what",
    "who",
    "how",
    "when",
    "where",
    "why",
    "do",
    "does",
    "did",
    "can",
    "could",
    "will",
    "would",
    "not",
    "no",
    "yes",
}


def _tokenize(text: str) -> List[str]:
    cleaned = re.sub(r"[^\w\s]", " ", text.lower())
    return [t for t in cleaned.split() if t and t not in _STOPWORDS_IT]


def _extract_entities_from_text(text: str) -> Set[str]:
    return {
        w.capitalize()
        for w in _tokenize(text)
        if len(w) > 2 and w[0].isalpha() and w[0].islower() is False or len(w) > 3
    }


def _keyword_overlap_score(query: str, answer: str) -> float:
    q_tokens = set(_tokenize(query))
    a_tokens = set(_tokenize(answer))
    if not q_tokens:
        return 0.0
    overlap = q_tokens & a_tokens
    return len(overlap) / len(q_tokens)


def _entity_match_score(query: str, answer: str) -> float:
    q_entities = _extract_entities_from_text(query)
    a_entities = _extract_entities_from_text(answer)
    if not q_entities:
        return 0.5
    matched = q_entities & a_entities
    return len(matched) / len(q_entities)


def _grounding_score(draft_answer: str, accumulated_data: List[dict]) -> float:
    if not accumulated_data:
        return 0.0

    answer_lower = draft_answer.lower()
    evidence_snippets = []

    for item in accumulated_data:
        source = item.get("source", "")
        content = item.get("content", "")

        if source == "knowledge_graph" and isinstance(content, dict):
            for concept_name, concept in content.items():
                if concept:
                    best = (
                        concept.get_best_info()
                        if hasattr(concept, "get_best_info")
                        else {}
                    )
                    if best:
                        desc = best.get("description", "")
                        if desc:
                            evidence_snippets.append(desc)
                        for ex in best.get("examples", []):
                            evidence_snippets.append(str(ex))
                    rels = getattr(concept, "relations", {}) or {}
                    for rel_name, targets in rels.items():
                        for target in targets:
                            target_value = (
                                target[0] if isinstance(target, tuple) else target
                            )
                            evidence_snippets.append(
                                f"{concept_name} {rel_name} {target_value}"
                            )
        elif source == "vector_memory" and isinstance(content, list):
            for match in content:
                text = match.get("text", "") if isinstance(match, dict) else str(match)
                if text:
                    evidence_snippets.append(text)
        elif source == "web_search" and isinstance(content, dict):
            results = content.get("results", [])
            for r in results:
                snippet = r.get("content", "") if isinstance(r, dict) else str(r)
                if snippet:
                    evidence_snippets.append(snippet[:500])
        elif source == "web_browsing" and isinstance(content, dict):
            web_content = content.get("content", "")
            if web_content:
                evidence_snippets.append(web_content[:1000])

    if not evidence_snippets:
        return 0.3

    answer_tokens = set(_tokenize(draft_answer))
    if not answer_tokens:
        return 0.0

    max_overlap = 0.0
    for snippet in evidence_snippets:
        snippet_tokens = set(_tokenize(snippet))
        if snippet_tokens:
            overlap = len(answer_tokens & snippet_tokens) / len(answer_tokens)
            max_overlap = max(max_overlap, overlap)

    return max_overlap


class CriticAgent(BaseAgent):
    """
    Agente specializzato nel trovare errori e allucinazioni.
    """

    PERTINENCE_THRESHOLD = 0.25
    GROUNDING_THRESHOLD = 0.15
    MIN_ANSWER_LENGTH = 15

    def __init__(self, engine=None):
        super().__init__("Critic", "Quality Control", engine)

    def process(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Critica il lavoro dell'Analyst."""
        draft = input_data.get("draft_answer", "")
        accumulated_data = input_data.get("accumulated_data", [])
        query = input_data.get("query", "")
        steps = []

        pertinence_score = (
            _keyword_overlap_score(query, draft) * 0.5
            + _entity_match_score(query, draft) * 0.5
        )
        grounding = _grounding_score(draft, accumulated_data)

        is_too_short = len(draft.strip()) < self.MIN_ANSWER_LENGTH
        has_no_evidence = not accumulated_data
        is_generic = any(
            p in draft.lower()
            for p in [
                "non ho trovato",
                "non ho abbastanza",
                "non posso rispondere",
                "non so",
            ]
        )

        constraints = {}
        if is_generic:
            status = "rejected"
            feedback = "Risposta generica: nessuna informazione utile fornita."
            final_score = 0.1
        elif is_too_short and not has_no_evidence:
            status = "needs_retry"
            feedback = "La risposta è troppo sintetica rispetto ai dati disponibili. Espandi con dettagli dalle evidenze."
            constraints = {
                "expand_with": "evidence_details",
                "min_length": 50,
                "reason": "too_short",
            }
            final_score = 0.4
        elif pertinence_score < self.PERTINENCE_THRESHOLD:
            status = "needs_retry"
            feedback = (
                f"Pertinenza bassa ({pertinence_score:.2f}). "
                f"La risposta non affronta direttamente la domanda. "
                f"Concentrati su: {query}"
            )
            constraints = {
                "focus_on": query,
                "reason": "low_pertinence",
                "suggested_sources": ["knowledge_graph", "web_search"],
            }
            final_score = 0.3
        elif grounding < self.GROUNDING_THRESHOLD and not has_no_evidence:
            status = "needs_retry"
            feedback = (
                f"Grounding insufficiente ({grounding:.2f}). "
                f"La risposta non è supportata dalle evidenze raccolte. "
                f"Usa i dati dal knowledge graph o dalla memoria."
            )
            constraints = {
                "use_sources": ["knowledge_graph", "vector_memory"],
                "reason": "low_grounding",
            }
            final_score = 0.35
        else:
            status = "approved"
            feedback = (
                "La risposta è coerente con la domanda e supportata dalle evidenze."
            )
            final_score = max(pertinence_score * 0.3 + grounding * 0.4 + 0.3, 0.6)

        steps.append(
            self.create_step(
                f"Verifica completata: {status}",
                {
                    "feedback": feedback,
                    "score": round(final_score, 3),
                    "pertinence": round(pertinence_score, 3),
                    "grounding": round(grounding, 3),
                },
            )
        )

        return {
            "final_answer": draft,
            "critic_feedback": feedback,
            "critic_constraints": constraints,
            "critic_steps": steps,
            "status": status,
            "final_confidence": round(final_score, 3),
            "pertinence_score": round(pertinence_score, 3),
            "grounding_score": round(grounding, 3),
        }
