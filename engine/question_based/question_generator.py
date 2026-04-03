class QuestionGenerator:
    def __init__(self, space):
        self.space = space

    def generate(self):
        if not hasattr(self.space, "remaining"):
            return self.get_questions()
        active = self.space.remaining()
        if len(active) <= 1:
            return []

        questions = []
        for feature in self.space.features():
            values = {self.space.hypotheses.get(h, {}).get(feature) for h in active}
            if len(values) > 1:
                questions.append(feature)
        return questions

    # Backward-compatible helpers used by old tests/scripts.
    def get_questions(self):
        return [
            "domestico",
            "coda_lunga",
            "caldo",
            "primario",
            "team",
            "palla",
        ]

    def generate_question(self, feature, domain=None):
        feature = str(feature).replace("_", " ")
        return f"E' {feature}?"
