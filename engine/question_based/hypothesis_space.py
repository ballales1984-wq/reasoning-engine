"""
HypothesisSpace - Gestione ipotesi, caratteristiche e probabilità

Gestisce:
- ipotesi (possibili soluzioni)
- caratteristiche (feature che distinguono le ipotesi)
- probabilità a priori
- stato attivo (ipotesi non ancora eliminate)
"""


class HypothesisSpace:
    """
    Manages hypotheses, their features, and probabilities.
    
    Example:
        space = HypothesisSpace(
            hypotheses={
                "cane": {"domestico": True, "coda_lunga": False, "verso": "bau"},
                "gatto": {"domestico": True, "coda_lunga": True, "verso": "miao"},
                "volpe": {"domestico": False, "coda_lunga": True, "verso": "bau"},
            },
            priors={"cane": 0.4, "gatto": 0.35, "volpe": 0.25}
        )
    """
    
    def __init__(self, hypotheses: dict, priors: dict = None):
        """
        Args:
            hypotheses: Dict of {hypothesis: {feature: value}}
            priors: Dict of {hypothesis: probability} (optional)
        """
        self.hypotheses = hypotheses
        self.active = set(hypotheses.keys())
        
        # Initialize priors (uniform if not provided)
        if priors:
            self.priors = priors
        else:
            n = len(hypotheses)
            self.priors = {h: 1.0 / n for h in hypotheses}
    
    def filter(self, feature: str, value):
        """
        Elimina ipotesi incompatibili con la risposta.
        
        Args:
            feature: Feature a cui è stata data la risposta
            value: Valore della risposta
        """
        self.active = {
            h for h in self.active
            if self.hypotheses[h].get(feature) == value
        }
    
    def eliminate(self, hypothesis: str):
        """
        Rimuovi manualmente un'ipotesi.
        
        Args:
            hypothesis: Nome ipotesi da eliminare
        """
        if hypothesis in self.active:
            self.active.remove(hypothesis)
    
    def remaining(self):
        """Ritorna la lista delle ipotesi ancora attive."""
        return list(self.active)
    
    def features(self):
        """Ritorna tutte le caratteristiche disponibili."""
        if not self.hypotheses:
            return []
        sample = next(iter(self.hypotheses.values()))
        return list(sample.keys())
    
    def get(self, hypothesis: str, default=None):
        """Ritorna le feature di un'ipotesi specifica."""
        return self.hypotheses.get(hypothesis, default)
    
    def probability(self, hypothesis: str) -> float:
        """Ritorna la probabilità di un'ipotesi."""
        return self.priors.get(hypothesis, 0.0)
    
    def __len__(self):
        return len(self.active)
    
    def __repr__(self):
        return f"HypothesisSpace(active={len(self.active)}, hypotheses={len(self.hypotheses)})"