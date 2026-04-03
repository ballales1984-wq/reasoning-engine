from typing import List, Dict, Any, Optional
import random


class QuestionGenerator:
    def __init__(self, domain: str = "general"):
        self.domain = domain
        self.question_templates: Dict[str, List[str]] = {
            "animals": [
                "E' un animale domestico?",
                "Ha la coda lunga?",
                "E' di colore rosso?",
                "Pes piu di 10kg?",
                "Vive in acqua?",
                "E' un predatore?",
                "Ha le ali?",
                "E' notturno?",
                "Vive in gruppo?",
            ],
            "colors": [
                "E' un colore primario?",
                "E' un colore caldo?",
                "E' piu chiaro del blu?",
                "Contiene rosso?",
                "E' un colore metallico?",
            ],
            "sports": [
                "Si gioca in team?",
                "Si pratica all'aperto?",
                "usa una palla?",
                "E' uno sport Olimpico?",
                "richiede contatto fisico?",
            ],
            "general": [
                "Hai pensato a {feature}?",
                "La risposta ha la proprieta {property}?",
                "E' classificabile come {category}?",
            ],
        }

    def get_questions(self, domain: Optional[str] = None) -> List[str]:
        d = domain or self.domain
        return self.question_templates.get(d, self.question_templates["general"])

    def generate_question(self, feature: str, domain: Optional[str] = None) -> str:
        d = domain or self.domain
        templates = self.get_questions(d)
        if templates:
            return random.choice(templates).format(
                feature=feature, property=feature, category=feature
            )
        return f"La risposta ha la proprieta {feature}?"

    def extract_features_from_llm(self, llm_response: str) -> List[str]:
        features = []
        lines = llm_response.strip().split("\n")
        for line in lines:
            line = line.strip()
            if line and not line.startswith("#"):
                if ":" in line:
                    feature = line.split(":", 1)[1].strip()
                else:
                    feature = line
                if feature and len(feature) > 2:
                    features.append(feature)
        return features[:10]

    def to_dict(self) -> Dict[str, Any]:
        return {"domain": self.domain, "available_questions": self.get_questions()}
