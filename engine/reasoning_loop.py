"""
ReasoningLoop — Il cuore del ReasoningEngine, ispirato all'Agent Loop di Claude Code.

Architettura:
1. Riceve input (domanda/comando)
2. Assembla il contesto (prompt, memoria, regole)
3. Esegue il loop di ragionamento
4. Usa tool per risolvere
5. Verifica i risultati
6. Aggiorna la memoria
7. Restituisce la risposta con spiegazione

Come il query.ts di Claude Code:
- È un loop while(true) che ripete finché serve
- Ogni iterazione: pre-processing → reasoning → tool execution → post-processing
- Ha un campo 'transition' che ricorda perché siamo in quello stato
- Gestisce errori e recovery
"""

from dataclasses import dataclass, field
from typing import Optional, Any, Generator
from enum import Enum
import traceback


class Transition(Enum):
    """Perché il loop ha continuato all'iterazione successiva."""
    NEXT_TURN = "next_turn"                    # Tutto ok, prossimo turno
    TOOL_REQUESTED = "tool_requested"          # L'engine ha chiesto un tool
    RETRY = "retry"                            # Riprova dopo errore
    VERIFICATION_FAILED = "verification_failed"  # Verifica fallita, riprova
    LLM_FALLBACK = "llm_fallback"             # Usa LLM come fallback
    COMPACTION_NEEDED = "compaction_needed"    # Contesto troppo pieno
    MAX_TURNS = "max_turns"                    # Raggiunto limite turni
    COMPLETED = "completed"                    # Finito con successo
    ERROR = "error"                            # Errore fatale


class TerminalState(Enum):
    """Stati terminali del loop."""
    COMPLETED = "completed"
    MAX_TURNS = "max_turns"
    ERROR = "error"
    VERIFICATION_FAILED = "verification_failed"
    ABORTED = "aborted"


@dataclass
class ReasoningState:
    """Stato del loop di ragionamento."""
    messages: list = field(default_factory=list)      # Cronologia messaggi
    context: dict = field(default_factory=dict)       # Contesto corrente
    turn_count: int = 0                               # Contatore turni
    max_turns: int = 10                               # Limite turni
    transition: Optional[Transition] = None           # Perché siamo qui
    tools_used: list = field(default_factory=list)    # Tool usati
    errors: list = field(default_factory=list)        # Errori incontrati
    verification_results: list = field(default_factory=list)  # Risultati verifiche
    reasoning_chain: list = field(default_factory=list)  # Catena di ragionamento
    confidence: float = 0.0                           # Confidenza totale


@dataclass
class ReasoningEvent:
    """Evento emesso durante il loop."""
    type: str                    # "thought", "tool_call", "tool_result", "verification", "answer"
    content: Any                 # Contenuto dell'evento
    confidence: float = 1.0      # Confidenza
    metadata: dict = field(default_factory=dict)


class ReasoningLoop:
    """
    Il loop principale di ragionamento.
    
    Segue l'architettura di Claude Code:
    1. Pre-processing: pulisci e prepara il contesto
    2. Reasoning: ragiona sulla domanda
    3. Tool execution: usa tool se necessario
    4. Verification: verifica i risultati
    5. Post-processing: aggiorna memoria, genera spiegazione
    """
    
    def __init__(self, engine, max_turns: int = 10):
        """
        engine: l'istanza di ReasoningEngine
        max_turns: numero massimo di turni di ragionamento
        """
        self.engine = engine
        self.max_turns = max_turns
        self.state = ReasoningState(max_turns=max_turns)
        
        # Tool registry (come Claude Code)
        self.tools = self._register_tools()
        
        # Callback per eventi
        self._on_event = None
    
    def _register_tools(self) -> dict:
        """Registra i tool disponibili (come il Tool System di Claude Code)."""
        return {
            "knowledge_lookup": {
                "description": "Cerca concetti nel knowledge graph",
                "function": self._tool_knowledge_lookup,
                "permission": "read"
            },
            "apply_rule": {
                "description": "Applica una regola logica",
                "function": self._tool_apply_rule,
                "permission": "execute"
            },
            "math_solve": {
                "description": "Risolvi un problema matematico",
                "function": self._tool_math_solve,
                "permission": "execute"
            },
            "verify": {
                "description": "Verifica un risultato",
                "function": self._tool_verify,
                "permission": "execute"
            },
            "deduce": {
                "description": "Fai una deduzione",
                "function": self._tool_deduce,
                "permission": "execute"
            },
            "induce": {
                "description": "Trova pattern da esempi",
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
            "llm_query": {
                "description": "Chiedi all'LLM (fallback)",
                "function": self._tool_llm_query,
                "permission": "execute"
            }
        }
    
    def run(self, question: str) -> Generator[ReasoningEvent, None, None]:
        """
        Esegue il loop di ragionamento.
        
        È un generator (come query.ts di Claude Code):
        - Yied eventi man mano che accadono
        - Ritorna lo stato terminale alla fine
        
        Uso:
            for event in loop.run("quanto fa 2+3?"):
                print(f"{event.type}: {event.content}")
        """
        # Reset stato
        self.state = ReasoningState(max_turns=self.max_turns)
        self.state.messages.append({"role": "user", "content": question})
        
        # Yield evento iniziale
        yield ReasoningEvent(
            type="start",
            content=f"Ragiono su: {question}",
            metadata={"turn": 0}
        )
        
        # Il loop principale (come query.ts)
        while True:
            self.state.turn_count += 1
            
            # === CHECK TERMINAL CONDITIONS ===
            if self.state.turn_count > self.max_turns:
                self.state.transition = Transition.MAX_TURNS
                yield ReasoningEvent(
                    type="terminal",
                    content="Raggiunto limite turni",
                    metadata={"state": TerminalState.MAX_TURNS.value}
                )
                return
            
            # === PRE-PROCESSING ===
            yield from self._pre_processing()
            
            # === REASONING ===
            reasoning_result = yield from self._reasoning_step()
            
            # === TOOL EXECUTION (se necessario) ===
            if reasoning_result.get("needs_tool"):
                tool_result = yield from self._execute_tool(
                    reasoning_result["tool_name"],
                    reasoning_result.get("tool_args", {})
                )
                
                if not tool_result.get("success"):
                    self.state.errors.append(tool_result.get("error"))
                    self.state.transition = Transition.RETRY
                    continue
                
                # Se il tool ha dato una risposta, è finale
                if tool_result.get("result", {}).get("answer") is not None:
                    reasoning_result["answer"] = tool_result["result"]["answer"]
                    reasoning_result["is_final"] = True
                    reasoning_result["confidence"] = tool_result["result"].get("confidence", 0.9)
            
            # === VERIFICATION ===
            verification = yield from self._verification_step(reasoning_result)
            
            if not verification.get("verified"):
                self.state.transition = Transition.VERIFICATION_FAILED
                yield ReasoningEvent(
                    type="verification_failed",
                    content=verification.get("reason", "Verifica fallita"),
                    confidence=verification.get("confidence", 0.0)
                )
                
                # Retry se non abbiamo superato il limite
                if self.state.turn_count < self.max_turns:
                    continue
            
            # === POST-PROCESSING ===
            yield from self._post_processing(reasoning_result, verification)
            
            # === CHECK SE FINITO ===
            if reasoning_result.get("is_final"):
                self.state.transition = Transition.COMPLETED
                yield ReasoningEvent(
                    type="answer",
                    content=reasoning_result.get("answer"),
                    confidence=reasoning_result.get("confidence", 0.0),
                    metadata={
                        "reasoning_chain": self.state.reasoning_chain,
                        "tools_used": self.state.tools_used,
                        "turns": self.state.turn_count
                    }
                )
                return
            
            # Prossimo turno
            self.state.transition = Transition.NEXT_TURN
    
    def _pre_processing(self) -> Generator[ReasoningEvent, None, None]:
        """
        Pre-processing: prepara il contesto per il ragionamento.
        
        Come il pre-processing di Claude Code:
        - Carica memoria rilevante
        - Controlla limiti contesto
        - Prepara tool disponibili
        """
        yield ReasoningEvent(
            type="thought",
            content=f"Turno {self.state.turn_count}: preparo il contesto...",
            metadata={"phase": "pre_processing"}
        )
        
        # Carica memoria rilevante
        if hasattr(self.engine, 'memory'):
            context = self.engine.memory.get_context()
            self.state.context.update(context)
        
        yield ReasoningEvent(
            type="context",
            content={
                "working_memory": len(self.state.context.get("working_memory", [])),
                "tools_available": list(self.tools.keys())
            }
        )
    
    def _reasoning_step(self) -> Generator[ReasoningEvent, None, dict]:
        """
        Step di ragionamento.
        
        Analizza la domanda e decide:
        - Risposta diretta (se sa già)
        - Usa un tool (se serve)
        - Chiede all'LLM (fallback)
        """
        question = self.state.messages[-1]["content"]
        
        yield ReasoningEvent(
            type="thought",
            content=f"Analizzo: {question}",
            metadata={"phase": "reasoning"}
        )
        
        # Parsa la domanda
        parsed = self.engine._parse_question(question)
        
        yield ReasoningEvent(
            type="parsed",
            content={
                "intent": parsed.get("intent"),
                "operation": parsed.get("operation"),
                "entities": parsed.get("entities")
            }
        )
        
        # Aggiungi alla catena di ragionamento
        self.state.reasoning_chain.append({
            "step": "parse",
            "result": parsed
        })
        
        # Decidi cosa fare
        if parsed.get("operation") in ["addition", "subtraction", "multiplication", "division"]:
            return {
                "needs_tool": True,
                "tool_name": "math_solve",
                "tool_args": {"expression": question},
                "is_final": False
            }
        
        elif parsed.get("intent") == "define":
            return {
                "needs_tool": True,
                "tool_name": "knowledge_lookup",
                "tool_args": {"query": question},
                "is_final": False
            }
        
        elif parsed.get("intent") == "verify":
            return {
                "needs_tool": True,
                "tool_name": "verify",
                "tool_args": {"statement": question},
                "is_final": False
            }
        
        else:
            # Prova con deduction
            return {
                "needs_tool": True,
                "tool_name": "deduce",
                "tool_args": {"query": question},
                "is_final": False
            }
    
    def _execute_tool(self, tool_name: str, args: dict) -> Generator[ReasoningEvent, None, dict]:
        """Esegue un tool (come il Tool System di Claude Code)."""
        
        yield ReasoningEvent(
            type="tool_call",
            content={"tool": tool_name, "args": args},
            metadata={"phase": "tool_execution"}
        )
        
        if tool_name not in self.tools:
            return {"success": False, "error": f"Tool '{tool_name}' non trovato"}
        
        try:
            tool = self.tools[tool_name]
            result = tool["function"](**args)
            
            self.state.tools_used.append(tool_name)
            
            yield ReasoningEvent(
                type="tool_result",
                content=result,
                metadata={"tool": tool_name}
            )
            
            return {"success": True, "result": result}
        
        except Exception as e:
            error_msg = f"Errore tool {tool_name}: {str(e)}"
            return {"success": False, "error": error_msg}
    
    def _verification_step(self, reasoning_result: dict) -> Generator[ReasoningEvent, None, dict]:
        """Verifica il risultato (come il Verification Layer di Claude Code)."""
        
        yield ReasoningEvent(
            type="verification",
            content="Verifico il risultato...",
            metadata={"phase": "verification"}
        )
        
        answer = reasoning_result.get("answer")
        
        if answer is None:
            return {"verified": False, "reason": "Nessuna risposta da verificare", "confidence": 0.0}
        
        # Verifica base: il risultato è sensato?
        is_valid = True
        confidence = 0.9
        
        if isinstance(answer, (int, float)):
            if answer != answer:  # NaN check
                is_valid = False
                confidence = 0.0
        
        self.state.verification_results.append({
            "answer": answer,
            "verified": is_valid,
            "confidence": confidence
        })
        
        return {
            "verified": is_valid,
            "confidence": confidence,
            "reason": "Verificato" if is_valid else "Verifica fallita"
        }
    
    def _post_processing(self, reasoning_result: dict, verification: dict) -> Generator[ReasoningEvent, None, None]:
        """Post-processing: aggiorna memoria, genera spiegazione."""
        
        yield ReasoningEvent(
            type="thought",
            content="Aggiorno memoria e genero spiegazione...",
            metadata={"phase": "post_processing"}
        )
        
        # Salva in memoria episodica
        if hasattr(self.engine, 'memory'):
            question = self.state.messages[-1]["content"]
            answer = reasoning_result.get("answer")
            
            self.engine.memory.remember(
                f"Domanda: {question} → Risposta: {answer}",
                memory_type="episodic",
                tags=["ragionamento"],
                importance=verification.get("confidence", 0.5)
            )
        
        # Aggiorna confidenza
        self.state.confidence = verification.get("confidence", 0.0)
    
    # === TOOL FUNCTIONS ===
    
    def _tool_knowledge_lookup(self, query: str) -> dict:
        """Cerca nel knowledge graph."""
        results = self.engine.knowledge.search(query)
        return {
            "found": len(results) > 0,
            "results": [{"name": r.name, "description": r.description} for r in results[:3]]
        }
    
    def _tool_apply_rule(self, rule_name: str, **kwargs) -> dict:
        """Applica una regola."""
        rule = self.engine.rules.get_rule(rule_name)
        if rule:
            result = rule.apply(**kwargs)
            return {"success": True, "result": result}
        return {"success": False, "error": f"Regola '{rule_name}' non trovata"}
    
    def _tool_math_solve(self, expression: str) -> dict:
        """Risolvi un problema matematico."""
        result = self.engine.math.solve(expression)
        return result
    
    def _tool_verify(self, statement: str) -> dict:
        """Verifica un'affermazione."""
        # Implementazione base
        return {"verified": True, "statement": statement}
    
    def _tool_deduce(self, query: str) -> dict:
        """Fai una deduzione."""
        if hasattr(self.engine, 'deductive'):
            # Estrai il soggetto dalla query
            words = query.lower().split()
            for word in words:
                if self.engine.knowledge.get(word):
                    result = self.engine.deductive.deduce(word)
                    return {
                        "found": result.found,
                        "conclusion": result.conclusion,
                        "confidence": result.confidence
                    }
        return {"found": False, "conclusion": "Non riesco a dedurre"}
    
    def _tool_induce(self, examples: list) -> dict:
        """Trova pattern da esempi."""
        if hasattr(self.engine, 'inductive'):
            result = self.engine.inductive.induce_from_examples(examples)
            return {
                "found": result.found,
                "patterns": [p.description for p in result.patterns]
            }
        return {"found": False}
    
    def _tool_find_analogy(self, concept: str) -> dict:
        """Trova analogie."""
        if hasattr(self.engine, 'analogical'):
            result = self.engine.analogical.find_analogies(concept)
            return {
                "found": result.found,
                "analogies": [a.explanation for a in result.analogies] if result.found else []
            }
        return {"found": False}
    
    def _tool_recall_memory(self, query: str) -> dict:
        """Richiama dalla memoria."""
        if hasattr(self.engine, 'memory'):
            results = self.engine.memory.recall(query)
            return {
                "found": len(results) > 0,
                "results": [r.content for r in results[:3]]
            }
        return {"found": False}
    
    def _tool_store_memory(self, content: str, memory_type: str = "episodic", **kwargs) -> dict:
        """Salva in memoria."""
        if hasattr(self.engine, 'memory'):
            memory_id = self.engine.memory.remember(content, memory_type=memory_type, **kwargs)
            return {"success": True, "memory_id": memory_id}
        return {"success": False}
    
    def _tool_llm_query(self, query: str) -> dict:
        """Chiedi all'LLM (fallback)."""
        if hasattr(self.engine, 'llm'):
            return self.engine.llm.query(query)
        return {"success": False, "error": "LLM non configurato"}
