"""
ProbabilityUpdater - Aggiornamento probabilità morbido (Bayesian)

Supporta:
- Risposte uncertain/unknown/maybe
- Update morbido invece di azzeramento brutale
- Confidence threshold per stop condition
"""

from enum import Enum


class AnswerConfidence(Enum):
    """Livelli di affidabilità della risposta."""
    HIGH = 1.0      # Risposta sicura
    MEDIUM = 0.7    # Risposta abbastanza sicura
    LOW = 0.4       # Risposta incerta
    UNKNOWN = 0.2   # "non so"


class SoftProbabilityUpdater:
    """
    Aggiornamento probabilità morbido.
    
    Invece di azzerare brutalmente:
    - Riduce il peso delle ipotesi incompatibili
    - Tiene traccia delle ipotesi "debolmente compatibili"
    - Supporta risposte uncertain/unknown
    """
    
    # Fattore di riduzione per ogni livello di confidenza
    PENALTY_FACTOR = {
        AnswerConfidence.HIGH: 0.0,      # Azzera completamente
        AnswerConfidence.MEDIUM: 0.1,    # Riduce a 10%
        AnswerConfidence.LOW: 0.3,       # Riduce a 30%
        AnswerConfidence.UNKNOWN: 0.8,   # Riduce a 80% (quasi nulla)
    }
    
    def __init__(self, space):
        """
        Args:
            space: HypothesisSpace instance
        """
        self.space = space
        self.original_priors = dict(space.priors)  # Backup per reset
    
    def update(self, feature: str, value, confidence: AnswerConfidence = AnswerConfidence.HIGH):
        """
        Aggiorna le probabilità con logica morbida.
        
        Args:
            feature: Feature a cui è stata data la risposta
            value: Valore della risposta (True/False/unknown)
            confidence: Livello di affidabilità della risposta
        """
        penalty = self.PENALTY_FACTOR[confidence]
        
        # Se unknown, riduci tutti i pesi di un po'
        if confidence == AnswerConfidence.UNKNOWN:
            for h in self.space.hypotheses:
                self.space.priors[h] *= 0.5
            self._normalize()
            return
        
        # Per ogni ipotesi: riduci peso se incompatibile
        for h in list(self.space.active):
            hypothesis_value = self.space.hypotheses[h].get(feature)
            
            # Se valore noto e diverso dalla risposta
            if hypothesis_value is not None and hypothesis_value != value:
                # Applica penalità (non azzera completamente se confidence bassa)
                self.space.priors[h] *= penalty
        
        # Rimuovi dalla lista attiva solo quelle con peso quasi zero
        self.space.active = {
            h for h in self.space.active
            if self.space.priors[h] > 0.01  # Soglia per rimozione
        }
        
        # Normalizza
        self._normalize()
    
    def _normalize(self):
        """Normalizza le probabilità (somma = 1)."""
        total = sum(self.space.priors[h] for h in self.space.active)
        
        if total > 0:
            for h in self.space.active:
                self.space.priors[h] /= total
    
    def is_consistent(self) -> bool:
        """Controlla se lo stato è inconsistente (tutti pesi a 0)."""
        total = sum(self.space.priors[h] for h in self.space.hypotheses)
        return total > 0
    
    def restore(self):
        """Ripristina allo stato originale."""
        self.space.priors = dict(self.original_priors)
        self.space.active = set(self.space.hypotheses.keys())
    
    def reset(self, priors: dict = None):
        """Resetta le probabilità ai valori iniziali."""
        if priors:
            self.space.priors = priors
            self.original_priors = dict(priors)
        else:
            n = len(self.space.hypotheses)
            self.space.priors = {h: 1.0 / n for h in self.space.hypotheses}
            self.original_priors = dict(self.space.priors)
        
        self.space.active = set(self.space.hypotheses.keys())
    
    def __repr__(self):
        active = len(self.space.active)
        return f"SoftProbabilityUpdater(active={active})"


# Alias per retrocompatibilità
class ProbabilityUpdater(SoftProbabilityUpdater):
    """Legacy wrapper - usa SoftProbabilityUpdater."""
    pass