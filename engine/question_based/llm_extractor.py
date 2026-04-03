import json
import re


class LLMFeatureExtractor:
    def __init__(self, llm=None):
        self.llm = llm

    def extract_features(self, concept, others):
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
