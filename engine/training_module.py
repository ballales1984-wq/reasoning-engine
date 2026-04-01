"""
TrainingModule — Modulo di addestramento per il ReasoningEngine.

Permette di:
1. Addestrare con dati strutturati (Q&A pairs)
2. Fine-tuning con feedback utente
3. Apprendimento da conversazioni
4. Esportare/importare training data
5. Valutare la qualità delle risposte
6. Training incrementale
"""

from dataclasses import dataclass, field
from typing import Optional, Any
from datetime import datetime
import json
import os


@dataclass
class TrainingExample:
    """Un esempio di training."""
    input: str                    # Domanda/input
    expected_output: str          # Risposta attesa
    category: str = "general"     # Categoria
    difficulty: float = 0.5       # 0=facile, 1=difficile
    verified: bool = False        # Verificato?
    source: str = "manual"        # Fonte (manual, user, generated)
    created_at: str = ""
    metadata: dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


@dataclass
class TrainingResult:
    """Risultato di un training."""
    examples_processed: int = 0
    rules_created: int = 0
    concepts_added: int = 0
    accuracy_before: float = 0.0
    accuracy_after: float = 0.0
    improvement: float = 0.0
    details: list = field(default_factory=list)


@dataclass
class EvaluationResult:
    """Risultato di una valutazione."""
    total_tests: int = 0
    passed: int = 0
    failed: int = 0
    accuracy: float = 0.0
    details: list = field(default_factory=list)


class TrainingModule:
    """Modulo di addestramento completo."""
    
    def __init__(self, engine):
        self.engine = engine
        self.training_data = []
        self.training_history = []
        self.feedback_log = []
        
        # Carica training data se esiste
        self._load_training_data()
    
    def add_example(self, input_text: str, expected_output: str,
                    category: str = "general", difficulty: float = 0.5,
                    verified: bool = True) -> str:
        """
        Aggiunge un esempio di training.
        
        Args:
            input_text: la domanda o l'input
            expected_output: la risposta corretta attesa
            category: categoria (math, finance, reasoning, etc.)
            difficulty: difficoltà (0-1)
            verified: se l'esempio è verificato come corretto
        """
        example = TrainingExample(
            input=input_text,
            expected_output=expected_output,
            category=category,
            difficulty=difficulty,
            verified=verified
        )
        
        self.training_data.append(example)
        self._save_training_data()
        
        return f"Esempio aggiunto: {input_text[:50]}..."
    
    def add_examples_batch(self, examples: list[dict]) -> int:
        """
        Aggiunge multipli esempi.
        
        Args:
            examples: lista di dict con 'input', 'output', 'category'
        """
        count = 0
        for ex in examples:
            self.add_example(
                input_text=ex.get('input', ''),
                expected_output=ex.get('output', ''),
                category=ex.get('category', 'general'),
                difficulty=ex.get('difficulty', 0.5),
                verified=ex.get('verified', True)
            )
            count += 1
        
        return count
    
    def train(self, examples: list[TrainingExample] = None,
              epochs: int = 1) -> TrainingResult:
        """
        Esegue il training con gli esempi forniti.
        
        Args:
            examples: esempi da usare (default: tutti i dati salvati)
            epochs: numero di epoche
        """
        examples = examples or self.training_data
        
        if not examples:
            return TrainingResult(
                details=["Nessun esempio di training disponibile"]
            )
        
        result = TrainingResult()
        result.examples_processed = len(examples)
        
        # Valuta accuracy prima del training
        result.accuracy_before = self.evaluate().accuracy
        
        for epoch in range(epochs):
            for example in examples:
                if not example.verified:
                    continue
                
                # Analizza l'esempio
                parsed = self.engine._parse_question(example.input)
                
                # Crea regole o concetti basati sull'esempio
                if example.category == "math":
                    # Per matematica, impara la formula
                    self.engine.learn(
                        f"math_{example.input[:20]}",
                        examples=[example.input],
                        description=example.expected_output,
                        category="training/math"
                    )
                    result.rules_created += 1
                
                elif example.category == "finance":
                    # Per finanza, impara il concetto
                    self.engine.learn(
                        f"finance_{example.input[:20]}",
                        examples=[example.input],
                        description=example.expected_output,
                        category="training/finance"
                    )
                    result.concepts_added += 1
                
                elif example.category == "reasoning":
                    # Per ragionamento, impara la relazione
                    self.engine.learn(
                        f"reasoning_{example.input[:20]}",
                        examples=[example.input],
                        description=example.expected_output,
                        category="training/reasoning"
                    )
                    result.concepts_added += 1
                
                else:
                    # Generale, impara come concetto
                    self.engine.learn(
                        f"general_{example.input[:20]}",
                        examples=[example.input],
                        description=example.expected_output,
                        category="training/general"
                    )
                    result.concepts_added += 1
                
                result.details.append(f"Imparato: {example.input[:30]}...")
        
        # Valuta accuracy dopo il training
        result.accuracy_after = self.evaluate().accuracy
        result.improvement = result.accuracy_after - result.accuracy_before
        
        # Salva nella history
        self.training_history.append(result)
        
        return result
    
    def learn_from_feedback(self, input_text: str, actual_output: str,
                           correct: bool, correct_answer: str = None) -> dict:
        """
        Apprende dal feedback dell'utente.
        
        Args:
            input_text: la domanda originale
            actual_output: la risposta data dall'engine
            correct: se la risposta era corretta
            correct_answer: la risposta corretta (se sbagliata)
        """
        feedback = {
            "input": input_text,
            "output": actual_output,
            "correct": correct,
            "correct_answer": correct_answer,
            "timestamp": datetime.now().isoformat()
        }
        
        self.feedback_log.append(feedback)
        
        if not correct and correct_answer:
            # Impara dalla correzione
            self.add_example(
                input_text=input_text,
                expected_output=correct_answer,
                category="feedback",
                verified=True
            )
            
            # Ritraing con il nuovo esempio
            self.train()
            
            return {
                "learned": True,
                "message": f"Imparato: {input_text[:50]} → {correct_answer[:50]}"
            }
        
        return {
            "learned": False,
            "message": "Risposta corretta, nessun apprendimento necessario"
        }
    
    def evaluate(self, test_data: list[TrainingExample] = None) -> EvaluationResult:
        """
        Valuta le performance dell'engine.
        
        Args:
            test_data: dati di test (default: usa training_data)
        """
        test_data = test_data or self.training_data
        
        if not test_data:
            return EvaluationResult(
                total_tests=0,
                details=["Nessun dato di test disponibile"]
            )
        
        result = EvaluationResult(total_tests=len(test_data))
        
        for example in test_data:
            # Esegui l'engine
            engine_result = self.engine.reason(example.input)
            actual = str(engine_result.get('answer', ''))
            
            # Confronta con l'output atteso
            if actual and example.expected_output.lower() in actual.lower():
                result.passed += 1
                result.details.append(f"✅ {example.input[:30]}")
            else:
                result.failed += 1
                result.details.append(f"❌ {example.input[:30]} (atteso: {example.expected_output})")
        
        result.accuracy = result.passed / result.total_tests if result.total_tests > 0 else 0
        
        return result
    
    def export_training_data(self, filepath: str = "training_data.json") -> str:
        """Esporta i dati di training."""
        data = [
            {
                "input": ex.input,
                "expected_output": ex.expected_output,
                "category": ex.category,
                "difficulty": ex.difficulty,
                "verified": ex.verified
            }
            for ex in self.training_data
        ]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return f"Esportati {len(data)} esempi in {filepath}"
    
    def import_training_data(self, filepath: str) -> int:
        """Importa dati di training."""
        if not os.path.exists(filepath):
            return 0
        
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return self.add_examples_batch(data)
    
    def _save_training_data(self):
        """Salva i dati di training su disco."""
        try:
            data = [
                {
                    "input": ex.input,
                    "expected_output": ex.expected_output,
                    "category": ex.category,
                    "difficulty": ex.difficulty,
                    "verified": ex.verified,
                    "source": ex.source
                }
                for ex in self.training_data
            ]
            
            with open("training_data.json", 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except:
            pass
    
    def _load_training_data(self):
        """Carica i dati di training da disco."""
        try:
            if os.path.exists("training_data.json"):
                with open("training_data.json", 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for item in data:
                    example = TrainingExample(
                        input=item.get('input', ''),
                        expected_output=item.get('expected_output', ''),
                        category=item.get('category', 'general'),
                        difficulty=item.get('difficulty', 0.5),
                        verified=item.get('verified', False),
                        source=item.get('source', 'imported')
                    )
                    self.training_data.append(example)
        except:
            pass
    
    def get_stats(self) -> dict:
        """Statistiche del training."""
        return {
            "total_examples": len(self.training_data),
            "verified_examples": sum(1 for ex in self.training_data if ex.verified),
            "categories": list(set(ex.category for ex in self.training_data)),
            "training_runs": len(self.training_history),
            "feedback_count": len(self.feedback_log)
        }
