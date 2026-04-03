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

    # Backward-compatible helpers used in legacy tests.
    def add_step(self, step):
        self.trace.append(dict(step))

    def get_trace(self):
        return list(self.trace)

    def get_summary(self):
        parts = []
        for i, step in enumerate(self.trace, 1):
            parts.append(f"{i}. {step.get('question', '?')} -> {step.get('answer', '?')}")
        return "\n".join(parts)

    def build(self, space):
        remaining = space.remaining()
        if len(remaining) == 1:
            final = remaining[0]
        elif remaining:
            final = max(remaining, key=lambda h: space.priors.get(h, 0.0))
        else:
            final = None
        final_probs = {h: space.priors.get(h, 0.0) for h in remaining}
        return {
            "final_hypothesis": final,
            "final_probabilities": final_probs,
            "trace": self.trace,
            "num_steps": len(self.trace),
        }
