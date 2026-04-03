"""
InformationGain - Selezione domanda migliore usando entropia

Calcola l'information gain per ogni domanda:
- entropia iniziale
- entropia dopo la domanda
- guadagno = differenza

Seleziona la domanda con il massimo guadagno (riduce più incertezza).
"""

import math


class InformationGain:
    """
    Selects the best question using entropy-based information gain.
    
    Entropy measures uncertainty. The best question is the one that
    reduces the most uncertainty (highest information gain).
    """
    
    def __init__(self, space):
        """
        Args:
            space: HypothesisSpace instance
        """
        self.space = space
    
    def entropy(self, hypotheses: set) -> float:
        """
        Calcola l'entropia di Shannon per un gruppo di ipotesi.
        
        Args:
            hypotheses: Set of hypothesis names
            
        Returns:
            Entropy value (0 = certezza, 1+ = incertezza)
        """
        # Peso totale delle ipotesi
        total = sum(self.space.priors[h] for h in hypotheses)
        if total == 0:
            return 0.0
        
        # Calcolo entropia
        e = 0.0
        for h in hypotheses:
            p = self.space.priors[h] / total
            if p > 0:
                e -= p * math.log2(p)
        
        return e
    
    def expected_entropy(self, feature: str) -> float:
        """
        Calcola l'entropia attesa dopo una domanda.
        
        Args:
            feature: Feature da chiedere
            
        Returns:
            Entropia attesa pesata
        """
        # Gruppa ipotesi per valore della feature
        groups = {}
        for h in self.space.active:
            v = self.space.hypotheses[h].get(feature)
            if v not in groups:
                groups[v] = set()
            groups[v].add(h)
        
        # Entropia attesa = somma pesata
        total = sum(self.space.priors[h] for h in self.space.active)
        if total == 0:
            return 0.0
        
        expected = 0.0
        for group in groups.values():
            weight = sum(self.space.priors[h] for h in group)
            expected += (weight / total) * self.entropy(group)
        
        return expected
    
    def gain(self, feature: str) -> float:
        """
        Calcola l'information gain per una feature.
        
        Args:
            feature: Feature da valutare
            
        Returns:
            Information gain (quanto si riduce l'incertezza)
        """
        base = self.entropy(self.space.active)
        expected = self.expected_entropy(feature)
        return base - expected
    
    def best_question(self, questions: list = None) -> str:
        """
        Seleziona la domanda migliore.
        
        Args:
            questions: Lista di feature da valutare (opzionale)
            
        Returns:
            Nome della feature migliore
        """
        if not questions:
            return None
        
        if len(questions) == 1:
            return questions[0]
        
        base_entropy = self.entropy(self.space.active)
        best_q = None
        best_gain = -1
        
        for q in questions:
            # Gruppa per valore
            groups = {}
            for h in self.space.active:
                v = self.space.hypotheses[h].get(q)
                groups.setdefault(v, set()).add(h)
            
            # Calcola entropia attesa
            total = sum(self.space.priors[h] for h in self.space.active)
            if total == 0:
                continue
            
            expected = 0.0
            for group in groups.values():
                weight = sum(self.space.priors[h] for h in group)
                expected += (weight / total) * self.entropy(group)
            
            gain = base_entropy - expected
            
            if gain > best_gain:
                best_gain = gain
                best_q = q
        
        return best_q
    
    def rank_questions(self, questions: list) -> list:
        """
        Ordina le domande per utilità decrescente.
        
        Args:
            questions: Lista di feature
            
        Returns:
            Lista di (feature, gain) ordinata
        """
        ranked = []
        for q in questions:
            ranked.append((q, self.gain(q)))
        
        ranked.sort(key=lambda x: x[1], reverse=True)
        return ranked
    
    def __repr__(self):
        return f"InformationGain(active={len(self.space.active)})"