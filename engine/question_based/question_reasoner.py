"""
QuestionReasoner - Ciclo completo di ragionamento

Il cuore del sistema:
1. Genera domande utili
2. Seleziona la migliore (information gain)
3. Chiede la risposta (callback)
4. Aggiorna ipotesi e probabilità
5. Verifica confidence threshold
6. Ripete finché non ci sono più domande utili o soglia raggiunta
7. Restituisce la conclusione finale + trace
"""

from enum import Enum

from .question_generator import QuestionGenerator
from .information_gain import InformationGain
from .probability_updater import ProbabilityUpdater, AnswerConfidence
from .explainer import Explainer


class AnswerType(Enum):
    """Tipi di risposta supportati."""
    TRUE = True
    FALSE = False
    UNKNOWN = "unknown"
    MAYBE = "maybe"


class ReasoningStatus(Enum):
    """Stato finale del ragionamento."""
    SUCCESS = "success"              # Una sola ipotesi chiara
    AMBIGUOUS = "ambiguous"          # Più ipotesi con probabilità simile
    UNDECIDABLE = "undecidable"       # Nessuna domanda utile rimasta
    INCONSISTENT = "inconsistent"     # 0 ipotesi (risposte contraddittorie)


class QuestionReasoner:
    """
    Main reasoning loop: asks questions until a conclusion is reached.
    
    Features:
    - Confidence threshold per stop condition
    - Supporto risposte unknown/maybe
    - Rilevamento stati ambigui/inconsistenti
    - Spiegazione completa del percorso
    """
    
    def __init__(
        self,
        space,
        confidence_threshold: float = 0.95,
        ambiguity_threshold: float = 0.1
    ):
        """
        Args:
            space: HypothesisSpace instance
            confidence_threshold: Soglia per dichiarare successo (default 0.95)
            ambiguity_threshold: Differenza massima per considerare ambiguità (default 0.1)
        """
        self.space = space
        self.confidence_threshold = confidence_threshold
        self.ambiguity_threshold = ambiguity_threshold
        
        self.generator = QuestionGenerator(space)
        self.selector = InformationGain(space)
        self.updater = SoftProbabilityUpdater(space)
        self.explainer = Explainer()
    
    def run(
        self,
        answer_callback,
        max_iterations: int = 20,
        allow_unknown: bool = True
    ):
        """
        Esegue il ciclo di ragionamento.
        
        Args:
            answer_callback: Funzione che riceve la domanda e ritorna la risposta
                           Formato: (value, confidence) o solo value
            max_iterations: Limite massimo di domande (safety)
            allow_unknown: Se True, accetta risposte unknown
            
        Returns:
            dict con:
            - final_hypothesis: ipotesi finale o None
            - status: ReasoningStatus
            - trace: log completo del ragionamento
            - final_probabilities: probabilità finali
            - message: messaggio esplicativo
        """
        iteration = 0
        status = None
        message = ""
        
        while iteration < max_iterations:
            iteration += 1
            
            # 1. Genera domande
            questions = self.generator.generate()
            
            # Se non ci sono più domande, fermati
            if not questions:
                break
            
            # 2. Seleziona la migliore
            best_q = self.selector.best_question(questions)
            if not best_q:
                break
            
            # 3. Chiedi la risposta
            try:
                result = answer_callback(best_q)
                
                # Supporta formati: solo valore o (valore, confidenza)
                if isinstance(result, tuple):
                    answer, confidence = result
                else:
                    answer = result
                    confidence = AnswerConfidence.HIGH
                    
            except Exception:
                # Se il callback fallisce, termina
                break
            
            # 4. Gestisci risposte speciali
            if allow_unknown and answer in [AnswerType.UNKNOWN, AnswerType.MAYBE, "unknown", "maybe", "non_so", "ns"]:
                # Risposta incerta: riduci pesi ma non azzerare
                self.updater.update(best_q, answer, AnswerConfidence.UNKNOWN)
            else:
                # Risposta normale: usa confidenza specificata
                self.updater.update(best_q, answer, confidence)
            
            # 5. Log
            self.explainer.log(
                question=best_q,
                answer=answer,
                remaining=self.space.remaining(),
                priors=dict(self.space.priors)
            )
            
            # 6. Aggiorna stato ipotesi
            if confidence == AnswerConfidence.HIGH:
                self.space.filter(best_q, answer)
            
            # 7. Verifica confidence threshold
            status, message = self._check_stopping_conditions()
            if status != ReasoningStatus.AMBIGUOUS:  # Continua solo se ambiguo
                break
        
        if status is None:
            status, message = self._check_stopping_conditions()
        if status is None:
            status = ReasoningStatus.UNDECIDABLE
            message = "Ragionamento terminato senza conclusione certa"

        # Costruisci risultato finale
        return self._build_result(status, message)
    
    def _check_stopping_conditions(self):
        """
        Verifica le condizioni di stop.
        
        Returns:
            (ReasoningStatus, message)
        """
        active = self.space.remaining()
        
        # Caso 1: 0 ipotesi (inconsistente)
        if len(active) == 0:
            return ReasoningStatus.INCONSISTENT, "Risposte contraddittorie: nessuna ipotesi compatibile"
        
        # Caso 2: 1 ipotesi con alta confidenza
        if len(active) == 1:
            h = active[0]
            if self.space.priors[h] >= self.confidence_threshold:
                return ReasoningStatus.SUCCESS, f"Conclusione: {h}"
        
        # Caso 3: più ipotesi, verifica se ambigue
        if len(active) > 1:
            sorted_h = sorted(active, key=lambda h: self.space.priors[h], reverse=True)
            top_prob = self.space.priors[sorted_h[0]]
            second_prob = self.space.priors[sorted_h[1]] if len(sorted_h) > 1 else 0
            
            # Se la differenza è piccola → ambiguo
            if top_prob - second_prob < self.ambiguity_threshold:
                return ReasoningStatus.AMBIGUOUS, f"Più ipotesi plausibili: {active}"
            
            # Se la top è sopra soglia → success
            if top_prob >= self.confidence_threshold:
                return ReasoningStatus.SUCCESS, f"Conclusione: {sorted_h[0]}"
        
        # Caso 4: non ci sono più domande utili
        questions = self.generator.generate()
        if not questions:
            return ReasoningStatus.UNDECIDABLE, "Nessuna domanda utile per distinguere le ipotesi rimanenti"
        
        # Nessuna condizione di stop soddisfatta → continua
        return None, None
    
    def _build_result(self, status: ReasoningStatus, message: str):
        """Costruisce il risultato finale."""
        active = self.space.remaining()
        
        # Determina final_hypothesis basato sullo stato
        if status == ReasoningStatus.SUCCESS:
            final_hypothesis = active[0] if active else None
        elif status == ReasoningStatus.AMBIGUOUS:
            final_hypothesis = active  # Lista di ipotesi
        else:
            final_hypothesis = None
        
        return {
            "final_hypothesis": final_hypothesis,
            "status": status.value,
            "message": message,
            "trace": self.explainer.trace,
            "final_probabilities": dict(self.space.priors),
            "num_steps": len(self.explainer.trace)
        }
    
    def run_interactive(self, ask_func=None):
        """
        Esegue in modalità interattiva (per testing/demo).
        
        Args:
            ask_func: Funzione custom per fare domande
                     Se None, usa input()
        """
        def default_handler(feature):
            readable = feature.replace("_", " ")
            response = input(f"Ha la caratteristica '{readable}'? (s/n/?): ")
            
            if response.lower() in ["s", "si", "y", "yes", "true"]:
                return True, AnswerConfidence.HIGH
            elif response.lower() in ["n", "no", "false"]:
                return False, AnswerConfidence.HIGH
            elif response in ["?", "non_so", "ns", "unknown"]:
                return "unknown", AnswerConfidence.UNKNOWN
            else:
                return "maybe", AnswerConfidence.LOW
        
        handler = ask_func or default_handler
        return self.run(handler)
    
    def __repr__(self):
        active = len(self.space.remaining())
        return f"QuestionReasoner(active={active}, threshold={self.confidence_threshold})"


# Import SoftProbabilityUpdater for the updater in __init__
from .probability_updater import SoftProbabilityUpdater
