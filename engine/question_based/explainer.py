"""
Explainer - Tracciamento e spiegazione del ragionamento

Tiene traccia di:
- ogni domanda fatta
- ogni risposta ricevuta
- ipotesi rimanenti dopo ogni passo
- probabilità dopo ogni passo

Genera una spiegazione completa del percorso logico.
"""


class Explainer:
    """
    Tracks reasoning path and produces final explanation.
    
    Maintains a trace of all questions, answers, and state updates.
    """
    
    def __init__(self):
        self.trace = []
    
    def log(self, question: str, answer, remaining: list, priors: dict):
        """
        Registra un passo del ragionamento.
        
        Args:
            question: Feature chiesto
            answer: Risposta ricevuta
            remaining: Ipotesi rimaste
            priors: Probabilità attuali
        """
        self.trace.append({
            "question": question,
            "answer": answer,
            "remaining": list(remaining),
            "probabilities": dict(priors)
        })
    
    def build(self, space):
        """
        Costruisce il risultato finale.
        
        Args:
            space: HypothesisSpace finale
            
        Returns:
            dict con final_hypothesis, trace, final_probabilities
        """
        final_remaining = space.remaining()
        
        # Se una sola ipotesi, quella è la conclusione
        if len(final_remaining) == 1:
            final_hypothesis = final_remaining[0]
        else:
            # Se più ipotesi, restituisci la più probabile
            final_hypothesis = max(
                final_remaining,
                key=lambda h: space.priors.get(h, 0)
            )
        
        return {
            "final_hypothesis": final_hypothesis,
            "final_probabilities": dict(space.priors),
            "trace": self.trace,
            "num_steps": len(self.trace)
        }
    
    def summary(self) -> str:
        """
        Genera un summary leggibile.
        
        Returns:
            Stringa con il trace formattato
        """
        if not self.trace:
            return "Nessun passo registrato."
        
        lines = ["📋 Reasoning Trace:", ""]
        
        for i, step in enumerate(self.trace, 1):
            q = step["question"].replace("_", " ")
            a = step["answer"]
            r = len(step["remaining"])
            lines.append(f"{i}. Domanda: '{q}' → Risposta: {a}")
            lines.append(f"   Ipotesi rimanenti: {r}")
            lines.append("")
        
        return "\n".join(lines)
    
    def clear(self):
        """Pulisce il trace."""
        self.trace = []
    
    def __len__(self):
        return len(self.trace)
    
    def __repr__(self):
        return f"Explainer(steps={len(self.trace)})"