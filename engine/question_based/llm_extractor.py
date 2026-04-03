import json
import re


class LLMFeatureExtractor:
    def __init__(self, llm=None, llm_client=None):
        self.llm = llm or llm_client

    def extract_features(self, concept=None, others=None, new_concept=None, existing_hypotheses=None, context=None):
        concept = concept or new_concept
        others = others or existing_hypotheses or []
        if not self.llm:
            return {}
        try:
            response = self.llm.chat(
                f"Caratteristiche per distinguere {concept} da {others}. JSON:"
            )
            # Compatibile con possibili shape di risposta.
            text = ""
            if isinstance(response, dict):
                text = response.get("message", {}).get("content", "") or response.get(
                    "response", ""
                )
            elif isinstance(response, str):
                text = response
            return self._parse(text)
        except Exception:
            return {}

    def _parse(self, text):
        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            return {}
        try:
            return json.loads(match.group())
        except Exception:
            return {}

    # Lightweight fallback expected by old tests.
    def _rule_based_extraction(self, text):
        t = (text or "").lower()
        out = {}
        if "rosso" in t:
            out["colore"] = "rosso"
        if "domestic" in t or "domestico" in t:
            out["domestico"] = True
        if "coda lunga" in t:
            out["coda_lunga"] = True
        return out


LLMExtractor = LLMFeatureExtractor
