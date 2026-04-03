"""
QuestionGenerator - Genera domande utili basate sulle differenze

Analizza le ipotesi attive e genera solo domande che:
-区分ano le ipotesi (hanno valori diversi)
- sono utili (riducono lo spazio delle ipotesi)
"""


class QuestionGenerator:
    """
    Generates useful questions based on differences between active hypotheses.
    
    A question is "useful" if it distinguishes between at least two hypotheses
    (i.e., different features values exist for that feature).
    """
    
    def __init__(self, space):
        """
        Args:
            space: HypothesisSpace instance
        """
        self.space = space
    
    def generate(self):
        """
        Genera tutte le domande utili.
        
        Returns:
            List of feature names that can be asked about
        """
        active = self.space.remaining()
        
        # Se c'è una sola ipotesi, non servono domande
        if len(active) <= 1:
            return []
        
        questions = []
        for feature in self.space.features():
            # Trova i valori unici per questa feature tra le ipotesi attive
            values = {self.space.hypotheses[h][feature] for h in active}
            
            # Se c'è più di un valore possibile, la domanda è utile
            if len(values) > 1:
                questions.append(feature)
        
        return questions
    
    def generate_yes_no(self):
        """
        Genera domande sì/no pronte per l'utente.
        
        Returns:
            List of {"feature": name, "question": text}
        """
        questions = self.generate()
        result = []
        
        for feature in questions:
            # Genera una domanda leggibile
            readable = feature.replace("_", " ")
            result.append({
                "feature": feature,
                "question": f"Ha la caratteristica '{readable}'?"
            })
        
        return result
    
    def __repr__(self):
        active = len(self.space.remaining())
        return f"QuestionGenerator(active_hypotheses={active})"