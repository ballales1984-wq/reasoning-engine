"""
Core Engine — Il motore principale, come Claude Code.

Architettura completa:
1. Loop di ragionamento (come query.ts)
2. State management (bootstrap + reactive store)
3. Context management (pressione + compaction)
4. Tool system (40+ tool)
5. Memory system (4 tipi)
6. Permission system
7. LLM bridge
8. MCP integration
9. Persistence
10. UI layer
"""

from .loop import ReasoningLoop
from .state import StateManager
from .context import ContextManager

# Import parent modules
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from knowledge_graph import KnowledgeGraph
from rule_engine import RuleEngine
from learner import Learner
from verifier import Verifier
from explainer import Explainer
from math_module import MathModule
from nlp_parser import parse as nlp_parse
from deductive import DeductiveReasoner
from inductive import InductiveReasoner
from analogical import AnalogicalReasoner
from memory_old import MemoryModule
from self_learning import SelfLearningEngine
from finance_module import FinanceModule
from prompt_builder import PromptBuilder


class ReasoningEngine:
    """
    Motore di ragionamento completo.
    
    Come Claude Code, integra tutti i sistemi:
    - Knowledge Graph
    - Rule Engine
    - NLP Parser
    - Reasoning (deductive, inductive, analogical)
    - Math Module
    - Finance Module
    - Memory System
    - Self Learning
    - LLM Bridge
    - Context Management
    - State Management
    - Prompt Builder
    """
    
    def __init__(self, llm_api_key: str = None, llm_model: str = "gpt-4o-mini"):
        # === CORE SYSTEMS ===
        self.knowledge = KnowledgeGraph()
        self.rules = RuleEngine()
        self.learner = Learner(self.knowledge)
        self.verifier = Verifier(self.rules)
        self.explainer = Explainer()
        
        # === REASONING SYSTEMS ===
        self.math = MathModule(self.rules, self.knowledge)
        self.deductive = DeductiveReasoner(self.knowledge, self.rules)
        self.inductive = InductiveReasoner(self.knowledge, self.rules)
        self.analogical = AnalogicalReasoner(self.knowledge)
        self.self_learning = SelfLearningEngine(self.knowledge, self.rules)
        
        # === MEMORY ===
        self.memory = MemoryModule(max_working_memory=10)
        
        # === FINANCE ===
        self.finance = FinanceModule(self.knowledge, self.rules)
        
        # === MANAGEMENT ===
        self.state = StateManager()
        self.context = ContextManager(max_tokens=10000)
        self.prompt_builder = PromptBuilder()
        
        # === LOOP ===
        self.loop = ReasoningLoop(self, max_turns=10)
        
        # === LLM (opzionale) ===
        self.llm_api_key = llm_api_key
        self.llm_model = llm_model
    
    def reason(self, question: str) -> dict:
        """
        Punto di ingresso principale.
        
        Usa il ReasoningLoop per ragionare sulla domanda.
        """
        # Imposta la domanda nello stato
        self.state.set_question(question)
        
        # Esegui il loop
        result = None
        for event in self.loop.run(question):
            if event.type == "answer":
                result = {
                    "answer": event.content,
                    "confidence": event.confidence,
                    "reasoning_chain": event.metadata.get("reasoning_chain", []),
                    "tools_used": event.metadata.get("tools_used", []),
                    "turns": event.metadata.get("turns", 0)
                }
                self.state.set_confidence(event.confidence)
                self.state.mark_complete()
        
        if result is None:
            result = {
                "answer": None,
                "confidence": 0.0,
                "reasoning_chain": [],
                "tools_used": [],
                "turns": 0
            }
        
        return result
    
    def learn(self, concept: str, examples: list[str] = None,
              description: str = None, category: str = "general"):
        """Insegna un concetto."""
        self.learner.add_concept(concept, examples or [], description, category)
        self.state.increment_memories_created()
        self.memory.remember(
            f"Imparato: {concept}",
            memory_type="semantic",
            tags=[category, "apprendimento"],
            importance=0.7
        )
    
    def what_do_you_know(self) -> dict:
        """Cosa sa l'engine."""
        return {
            "concepts": self.knowledge.list_all(),
            "rules": self.rules.list_all(),
            "memory_stats": self.memory.get_stats(),
            "state_stats": self.state.get_stats(),
            "context_stats": self.context.get_stats()
        }
    
    def _parse_question(self, question: str) -> dict:
        """Analizza una domanda."""
        question = question.strip().lower()
        
        import re
        
        # Rileva operazioni matematiche
        if "quanto fa" in question or "calcola" in question:
            numbers = [float(x) for x in re.findall(r'-?\d+\.?\d*', question)]
            
            if "+" in question or "più" in question:
                return {"intent": "calculate", "operation": "addition", "entities": [str(n) for n in numbers], "numbers": numbers}
            elif "-" in question or "meno" in question:
                return {"intent": "calculate", "operation": "subtraction", "entities": [str(n) for n in numbers], "numbers": numbers}
            elif "×" in question or "*" in question or "per" in question:
                return {"intent": "calculate", "operation": "multiplication", "entities": [str(n) for n in numbers], "numbers": numbers}
            elif "÷" in question or "/" in question or "diviso" in question:
                return {"intent": "calculate", "operation": "division", "entities": [str(n) for n in numbers], "numbers": numbers}
            
            return {"intent": "calculate", "operation": "unknown", "entities": [str(n) for n in numbers], "numbers": numbers}
        
        # Rileva definizioni
        if "cosa è" in question or "cos'è" in question or "definisci" in question:
            match = re.search(r"cos['']è\s+(\w+)|cosa\s+è\s+(\w+)|definisci\s+(\w+)", question)
            concept = match.group(1) or match.group(2) or match.group(3) if match else question
            return {"intent": "define", "operation": "lookup", "entities": [concept], "numbers": []}
        
        # Default
        return {"intent": "unknown", "operation": "unknown", "entities": question.split(), "numbers": []}
