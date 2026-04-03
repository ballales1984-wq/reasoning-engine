from typing import List, Dict, Any, Optional
from datetime import datetime


class Explainer:
    def __init__(self):
        self.steps: List[Dict[str, Any]] = []
        self.start_time: Optional[datetime] = None

    def add_step(self, step: Dict[str, Any]):
        if not self.start_time:
            self.start_time = datetime.now()
        step["timestamp"] = datetime.now().isoformat()
        self.steps.append(step)

    def get_summary(self) -> str:
        if not self.steps:
            return "Nessun ragionamento effettuato."

        lines = ["=== TRACE DEL RAGIONAMENTO ==="]

        for i, step in enumerate(self.steps, 1):
            answer_str = "SI" if step.get("answer") else "NO"
            lines.append(f"\nStep {i}:")
            lines.append(f"  Domanda: {step.get('question', 'N/A')}")
            lines.append(f"  Risposta: {answer_str}")
            lines.append(f"  Top ipotesi: {step.get('top_hypothesis', 'N/A')}")
            lines.append(f"  Confidenza: {step.get('confidence', 0):.2%}")
            lines.append(f"  Entropia: {step.get('entropy', 0):.4f}")

        final = self.steps[-1]
        lines.append(f"\n=== RISULTATO FINALE ===")
        lines.append(f"Ipotesi: {final.get('top_hypothesis', 'N/A')}")
        lines.append(f"Confidenza: {final.get('confidence', 0):.2%}")

        return "\n".join(lines)

    def get_trace(self) -> List[Dict[str, Any]]:
        return self.steps.copy()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "steps": self.steps,
            "total_steps": len(self.steps),
            "start_time": self.start_time.isoformat() if self.start_time else None,
        }
