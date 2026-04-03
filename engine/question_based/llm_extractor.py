from typing import Dict, Any, List, Optional, Callable


class LLMExtractor:
    def __init__(self, llm_provider: Optional[Callable] = None):
        self.llm_provider = llm_provider

    def extract_features(
        self, text: str, prompt: Optional[str] = None
    ) -> Dict[str, Any]:
        if not self.llm_provider:
            return self._rule_based_extraction(text)

        default_prompt = f"""Estrai le feature rilevanti dal seguente testo:
{text}

Elenca le feature in formato:
feature1: valore1
feature2: valore2"""

        response = self.llm_provider(prompt or default_prompt)
        return self._parse_llm_response(response)

    def _rule_based_extraction(self, text: str) -> Dict[str, Any]:
        words = text.lower().split()
        features = {}

        common_features = {
            "colore": ["rosso", "blu", "verde", "giallo", "nero", "bianco"],
            "dimensione": ["grande", "piccolo", "medio"],
            "habitat": ["acqua", "terra", "aria"],
            "tipo": ["domestico", "selvatico"],
        }

        for feature, keywords in common_features.items():
            for kw in keywords:
                if kw in words:
                    features[feature] = kw

        return features

    def _parse_llm_response(self, response: str) -> Dict[str, Any]:
        features = {}
        lines = response.strip().split("\n")

        for line in lines:
            line = line.strip()
            if ":" in line:
                key, value = line.split(":", 1)
                key = key.strip().lower()
                value = value.strip()
                if key and value:
                    features[key] = value

        return features

    def generate_hypotheses(
        self, llm_response: str, domain: str = "general"
    ) -> List[Dict[str, Any]]:
        hypotheses = []
        lines = llm_response.strip().split("\n")

        current_id = None
        current_name = None
        current_features = {}

        for line in lines:
            line = line.strip()
            if not line:
                continue

            if line[0].isdigit() and "." in line:
                if current_name:
                    hypotheses.append(
                        {
                            "id": current_id,
                            "name": current_name,
                            "probability": 1.0,
                            "features": current_features,
                            "evidence": [],
                        }
                    )
                parts = line.split(".", 1)
                current_id = parts[0].strip()
                current_name = parts[1].strip() if len(parts) > 1 else line
                current_features = {}
            elif ":" in line:
                key, value = line.split(":", 1)
                current_features[key.strip()] = value.strip()

        if current_name:
            hypotheses.append(
                {
                    "id": current_id,
                    "name": current_name,
                    "probability": 1.0,
                    "features": current_features,
                    "evidence": [],
                }
            )

        return hypotheses

    def to_dict(self) -> Dict[str, Any]:
        return {
            "extractor": "LLMExtractor",
            "has_llm_provider": self.llm_provider is not None,
        }
