class QuestionGenerator:
    def __init__(self, space):
        self.space = space

    def generate(self):
        active = self.space.remaining()
        if len(active) <= 1:
            return []

        questions = []
        for feature in self.space.features():
            values = {self.space.hypotheses[h].get(feature) for h in active}
            if len(values) > 1:
                questions.append(feature)
        return questions
