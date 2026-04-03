class Explainer:
    def __init__(self):
        self.trace = []

    def log(self, q, a, r, p):
        self.trace.append(
            {
                "question": q,
                "answer": a,
                "remaining": list(r),
                "probabilities": dict(p),
            }
        )

    def build(self, space):
        remaining = space.remaining()
        if len(remaining) == 1:
            final = remaining[0]
        elif remaining:
            final = max(remaining, key=lambda h: space.priors.get(h, 0.0))
        else:
            final = None
        return {
            "final_hypothesis": final,
            "final_probabilities": dict(space.priors),
            "trace": self.trace,
            "num_steps": len(self.trace),
        }
