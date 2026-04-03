import json
import math
from typing import Dict, List, Tuple

from engine.data.graph import KnowledgeGraph
from engine.question_based import (
    HypothesisSpace,
    QuestionReasoner,
    AnswerConfidence,
    LLMFeatureExtractor,
)


class MockLLM:
    """Deterministic mock for reproducible master test runs."""

    DB = {
        "cane": {"domestico": True, "coda_lunga": False, "rosso": False, "ulula": False},
        "gatto": {"domestico": True, "coda_lunga": True, "rosso": False, "ulula": False},
        "volpe": {"domestico": False, "coda_lunga": True, "rosso": True, "ulula": False},
        "lupo": {"domestico": False, "coda_lunga": True, "rosso": False, "ulula": True},
    }

    def chat(self, prompt: str):
        concept = ""
        lowered = prompt.lower()
        for c in self.DB:
            if c in lowered:
                concept = c
                break
        payload = self.DB.get(concept, {})
        return {"message": {"content": json.dumps(payload)}}


def _normalize_bool(value):
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    if text in {"true", "yes", "y", "1", "si", "s"}:
        return True
    if text in {"false", "no", "n", "0"}:
        return False
    return False


def _get_feature_from_graph(kg: KnowledgeGraph, concept: str, feature: str):
    obj = kg.get(concept)
    if not obj:
        return None
    rels = getattr(obj, "relations", {}) or {}
    vals = rels.get(feature, [])
    if not vals:
        return None
    first = vals[0]
    target = first[0] if isinstance(first, tuple) else first
    return _normalize_bool(target)


def _set_feature_in_graph(kg: KnowledgeGraph, concept: str, feature: str, value: bool):
    obj = kg.add(concept, description=f"{concept} feature set", category="animal", channel="system")
    obj.add_relation(feature, "true" if value else "false", channel="system")


def _entropy(active: List[str], priors: Dict[str, float]) -> float:
    total = sum(priors.get(h, 0.0) for h in active)
    if total <= 0:
        return 0.0
    e = 0.0
    for h in active:
        p = priors.get(h, 0.0)
        if p <= 0:
            continue
        r = p / total
        e -= r * math.log2(r)
    return e


def run_master_test() -> Tuple[str, dict]:
    required_features = ["domestico", "coda_lunga", "rosso", "ulula"]
    concepts = ["cane", "gatto", "volpe", "lupo"]

    # 1) Knowledge Graph with partial data
    kg = KnowledgeGraph()
    _set_feature_in_graph(kg, "cane", "domestico", True)
    _set_feature_in_graph(kg, "cane", "coda_lunga", False)

    _set_feature_in_graph(kg, "gatto", "domestico", True)
    _set_feature_in_graph(kg, "gatto", "coda_lunga", True)

    _set_feature_in_graph(kg, "volpe", "domestico", False)
    _set_feature_in_graph(kg, "volpe", "rosso", True)

    # 2) Fill missing features with LLM extractor
    extractor = LLMFeatureExtractor(llm=MockLLM())
    properties_used = {}

    for concept in concepts:
        llm_props = extractor.extract_features(concept=concept, others=[c for c in concepts if c != concept])
        row = {}
        for f in required_features:
            current = _get_feature_from_graph(kg, concept, f)
            if current is None:
                current = _normalize_bool(llm_props.get(f, False))
                _set_feature_in_graph(kg, concept, f, current)
            row[f] = current
        properties_used[concept] = row

    # 3) Build hypothesis space using graph-derived properties only
    hypotheses = {c: properties_used[c] for c in concepts}
    space = HypothesisSpace(hypotheses)
    reasoner = QuestionReasoner(space, confidence_threshold=0.95, ambiguity_threshold=0.10, max_iterations=20)

    # 4) Simulated answers
    answers = {"domestico": True, "coda_lunga": True, "rosso": False, "ulula": False}

    audit = []
    generated_questions = []
    chosen_questions = []
    choice_motivation = []
    seen_states = set()
    incoherences = []

    for i in range(reasoner.max_iterations):
        qs = reasoner.gen.generate()
        generated_questions.append(list(qs))
        if not qs:
            break

        q = reasoner.sel.best_question(qs)
        if q is None:
            break

        before_active = sorted(reasoner.space.remaining())
        before_entropy = _entropy(before_active, reasoner.space.priors)

        ans = answers.get(q, "unknown")
        conf = AnswerConfidence.HIGH if ans in (True, False) else AnswerConfidence.UNKNOWN
        reasoner.step(q, (ans, conf))

        after_active = sorted(reasoner.space.remaining())
        after_entropy = _entropy(after_active, reasoner.space.priors)

        chosen_questions.append(q)
        choice_motivation.append({
            "selected": q,
            "candidates": list(qs),
            "entropy_before": before_entropy,
            "entropy_after": after_entropy,
            "reduced_uncertainty": after_entropy <= before_entropy + 1e-9,
        })

        state_key = tuple(after_active)
        if state_key in seen_states:
            incoherences.append(f"possible_cycle_at_step_{i + 1}")
            break
        seen_states.add(state_key)

        audit.append(
            {
                "step": i + 1,
                "question": q,
                "answer": ans,
                "remaining": after_active,
                "probabilities": {h: reasoner.space.priors.get(h, 0.0) for h in after_active},
                "entropy_before": before_entropy,
                "entropy_after": after_entropy,
            }
        )

        if len(after_active) <= 1:
            break
        if after_active:
            if max(reasoner.space.priors.get(h, 0.0) for h in after_active) >= reasoner.conf:
                break

    final_result = reasoner.exp.build(reasoner.space)
    final_result.update(reasoner._status_payload())

    remaining = reasoner.space.remaining()
    probs = final_result.get("final_probabilities", {})
    prob_sum = sum(probs.values())
    if remaining and abs(prob_sum - 1.0) > 1e-6:
        incoherences.append(f"probability_sum_not_1:{prob_sum}")

    for m in choice_motivation:
        if not m["reduced_uncertainty"]:
            incoherences.append(f"non_reducing_question:{m['selected']}")

    if not audit:
        incoherences.append("no_reasoning_steps")

    report = {
        "status": final_result.get("status"),
        "message": final_result.get("message"),
        "final_hypothesis": final_result.get("final_hypothesis"),
        "final_probabilities": probs,
        "properties_used": properties_used,
        "generated_questions": generated_questions,
        "chosen_questions": chosen_questions,
        "choice_motivation": choice_motivation,
        "audit_trail": audit,
        "incoherences": incoherences,
    }

    ok = len(incoherences) == 0 and final_result.get("final_hypothesis") is not None
    return ("MASTER TEST OK" if ok else "MASTER TEST ERROR"), report


def main():
    label, report = run_master_test()
    print(json.dumps(report, ensure_ascii=False, indent=2))
    print(label)


if __name__ == "__main__":
    main()
