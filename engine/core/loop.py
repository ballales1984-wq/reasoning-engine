"""
ReasoningLoop v2 — Agent Loop completo, come query.ts di Claude Code.
"""

from dataclasses import dataclass, field
from typing import Optional, Any, Generator
from enum import Enum
import traceback


class Transition(Enum):
    NEXT_TURN = "next_turn"
    TOOL_REQUESTED = "tool_requested"
    RETRY = "retry"
    VERIFICATION_FAILED = "verification_failed"
    LLM_FALLBACK = "llm_fallback"
    COMPACTION_NEEDED = "compaction_needed"
    MAX_TURNS = "max_turns"
    COMPLETED = "completed"
    ERROR = "error"


@dataclass
class ReasoningEvent:
    type: str
    content: Any
    confidence: float = 1.0
    metadata: dict = field(default_factory=dict)


class ReasoningLoop:
    """Loop principale di ragionamento, ispirato a query.ts."""
    
    def __init__(self, engine, max_turns: int = 10):
        self.engine = engine
        self.max_turns = max_turns
        self.tools = self._register_tools()
    
    def _register_tools(self) -> dict:
        """Registra tutti i tool disponibili."""
        return {
            "knowledge_lookup": {
                "description": "Cerca nel knowledge graph",
                "function": self._tool_knowledge_lookup,
                "permission": "read"
            },
            "apply_rule": {
                "description": "Applica regola logica",
                "function": self._tool_apply_rule,
                "permission": "execute"
            },
            "math_solve": {
                "description": "Risolvi problema matematico",
                "function": self._tool_math_solve,
                "permission": "execute"
            },
            "finance_solve": {
                "description": "Calcolo finanziario",
                "function": self._tool_finance_solve,
                "permission": "execute"
            },
            "verify": {
                "description": "Verifica risultato",
                "function": self._tool_verify,
                "permission": "execute"
            },
            "deduce": {
                "description": "Deduzione logica",
                "function": self._tool_deduce,
                "permission": "execute"
            },
            "induce": {
                "description": "Induzione da esempi",
                "function": self._tool_induce,
                "permission": "execute"
            },
            "find_analogy": {
                "description": "Trova analogie",
                "function": self._tool_find_analogy,
                "permission": "execute"
            },
            "recall_memory": {
                "description": "Richiama dalla memoria",
                "function": self._tool_recall_memory,
                "permission": "read"
            },
            "store_memory": {
                "description": "Salva in memoria",
                "function": self._tool_store_memory,
                "permission": "write"
            },
            "self_learn": {
                "description": "Impara da solo",
                "function": self._tool_self_learn,
                "permission": "execute"
            },
            "llm_query": {
                "description": "Chiedi all'LLM",
                "function": self._tool_llm_query,
                "permission": "execute"
            }
        }
    
    def run(self, question: str) -> Generator[ReasoningEvent, None, None]:
        """Esegue il loop di ragionamento."""
        
        yield ReasoningEvent(type="start", content=f"Analizzo: {question}")
        
        turn = 0
        reasoning_chain = []
        tools_used = []
        
        while turn < self.max_turns:
            turn += 1
            
            # PRE-PROCESSING
            yield ReasoningEvent(type="thought", content=f"Turno {turn}: preparo...")
            
            # PARSING
            parsed = self.engine._parse_question(question)
            yield ReasoningEvent(type="parsed", content={
                "intent": parsed["intent"],
                "operation": parsed["operation"]
            })
            
            reasoning_chain.append({"step": "parse", "result": parsed})
            
            # DECIDI TOOL
            tool_name = None
            tool_args = {}
            
            if parsed["operation"] in ["addition", "subtraction", "multiplication", "division"]:
                tool_name = "math_solve"
                tool_args = {"expression": question}
            elif parsed["intent"] == "define":
                tool_name = "knowledge_lookup"
                tool_args = {"query": question}
            elif parsed["intent"] == "verify":
                tool_name = "verify"
                tool_args = {"statement": question}
            else:
                # Prova deduzione
                tool_name = "deduce"
                tool_args = {"query": question}
            
            # ESEGUI TOOL
            if tool_name:
                yield ReasoningEvent(type="tool_call", content={"tool": tool_name, "args": tool_args})
                
                tool_func = self.tools[tool_name]["function"]
                try:
                    result = tool_func(**tool_args)
                    tools_used.append(tool_name)
                    
                    yield ReasoningEvent(type="tool_result", content=result)
                    
                    # VERIFICA
                    yield ReasoningEvent(type="verification", content="Verifico...")
                    
                    # SE HA RISPOSTA, È FINALE
                    if result.get("answer") is not None:
                        yield ReasoningEvent(
                            type="answer",
                            content=result["answer"],
                            confidence=result.get("confidence", 0.9),
                            metadata={
                                "reasoning_chain": reasoning_chain,
                                "tools_used": tools_used,
                                "turns": turn
                            }
                        )
                        return
                    
                    # SE HA CONCLUSION, È FINALE  
                    if result.get("conclusion"):
                        yield ReasoningEvent(
                            type="answer",
                            content=result["conclusion"],
                            confidence=result.get("confidence", 0.8),
                            metadata={
                                "reasoning_chain": reasoning_chain,
                                "tools_used": tools_used,
                                "turns": turn
                            }
                        )
                        return
                
                except Exception as e:
                    yield ReasoningEvent(type="error", content=str(e))
            
            # POST-PROCESSING
            yield ReasoningEvent(type="thought", content="Aggiorno memoria...")
            
            if hasattr(self.engine, 'memory'):
                self.engine.memory.remember(
                    f"Turno {turn}: {question}",
                    memory_type="episodic",
                    tags=["ragionamento"]
                )
        
        # MAX TURNS
        yield ReasoningEvent(
            type="terminal",
            content="Raggiunto limite turni",
            metadata={"state": "max_turns"}
        )
    
    # === TOOL FUNCTIONS ===
    
    def _tool_knowledge_lookup(self, query: str) -> dict:
        results = self.engine.knowledge.search(query)
        return {"found": len(results) > 0, "results": [{"name": r.name, "description": r.description} for r in results[:3]]}
    
    def _tool_apply_rule(self, rule_name: str, **kwargs) -> dict:
        rule = self.engine.rules.get_rule(rule_name)
        if rule:
            return {"success": True, "result": rule.apply(**kwargs)}
        return {"success": False, "error": f"Regola '{rule_name}' non trovata"}
    
    def _tool_math_solve(self, expression: str) -> dict:
        return self.engine.math.solve(expression)
    
    def _tool_finance_solve(self, operation: str, **kwargs) -> dict:
        result = self.engine.finance.calculate(operation, **kwargs)
        return {"answer": result.result, "explanation": result.explanation}
    
    def _tool_verify(self, statement: str) -> dict:
        return {"verified": True, "statement": statement}
    
    def _tool_deduce(self, query: str) -> dict:
        words = query.lower().split()
        for word in words:
            if self.engine.knowledge.get(word):
                result = self.engine.deductive.deduce(word)
                return {"found": result.found, "conclusion": result.conclusion, "confidence": result.confidence}
        return {"found": False, "conclusion": None}
    
    def _tool_induce(self, examples: list) -> dict:
        result = self.engine.inductive.induce_from_examples(examples)
        return {"found": result.found, "patterns": [p.description for p in result.patterns]}
    
    def _tool_find_analogy(self, concept: str) -> dict:
        result = self.engine.analogical.find_analogies(concept)
        return {"found": result.found, "analogies": [a.explanation for a in result.analogies] if result.found else []}
    
    def _tool_recall_memory(self, query: str) -> dict:
        results = self.engine.memory.recall(query)
        return {"found": len(results) > 0, "results": [r.content for r in results[:3]]}
    
    def _tool_store_memory(self, content: str, memory_type: str = "episodic", **kwargs) -> dict:
        memory_id = self.engine.memory.remember(content, memory_type=memory_type, **kwargs)
        return {"success": True, "memory_id": memory_id}
    
    def _tool_self_learn(self, examples: list) -> dict:
        hypotheses = self.engine.self_learning.observe(examples)
        return {"hypotheses": len(hypotheses), "details": [h.description for h in hypotheses[:3]]}
    
    def _tool_llm_query(self, query: str) -> dict:
        return {"success": False, "error": "LLM non configurato"}
