"""
StateManager — Gestione dello stato, ispirata a Claude Code.

Claude Code ha due livelli di stato:
1. Bootstrap Singleton — stato globale iniziale
2. Reactive Store — stato reattivo con listener

Noi facciamo lo stesso per il ReasoningEngine.
"""

from dataclasses import dataclass, field
from typing import Optional, Any, Callable
from datetime import datetime
import json
import hashlib


@dataclass
class SessionState:
    """Stato della sessione di ragionamento."""
    session_id: str = ""
    created_at: str = ""
    updated_at: str = ""
    
    # Contatori
    total_turns: int = 0
    total_tool_calls: int = 0
    total_reasoning_steps: int = 0
    total_errors: int = 0
    
    # Contesto
    current_question: str = ""
    current_confidence: float = 0.0
    reasoning_chain: list = field(default_factory=list)
    
    # Memoria
    memories_created: int = 0
    memories_recalled: int = 0
    
    # Flags
    is_complete: bool = False
    has_errors: bool = False
    llm_used: bool = False


class StateManager:
    """
    Gestisce lo stato del ReasoningEngine.
    
    Come Claude Code:
    - Bootstrap state: stato iniziale
    - Reactive store: stato con listener
    - Session persistence: salva/carica sessioni
    """
    
    def __init__(self):
        # Bootstrap state
        self.bootstrap = self._init_bootstrap()
        
        # Reactive store
        self._state = SessionState()
        self._listeners = set()
        self._on_change = None
        
        # Session history
        self.session_history = []
        
        # Genera session ID
        self._state.session_id = self._generate_session_id()
        self._state.created_at = datetime.now().isoformat()
        self._state.updated_at = self._state.created_at
    
    def _init_bootstrap(self) -> dict:
        """Inizializza lo stato bootstrap."""
        return {
            "version": "1.0.0",
            "name": "ReasoningEngine",
            "created_at": datetime.now().isoformat(),
            "total_sessions": 0,
            "total_questions": 0,
            "total_reasoning_steps": 0
        }
    
    def _generate_session_id(self) -> str:
        """Genera un ID sessione univoco."""
        data = f"{datetime.now().isoformat()}-{id(self)}"
        return hashlib.md5(data.encode()).hexdigest()[:12]
    
    # === REACTIVE STORE ===
    
    def get_state(self) -> SessionState:
        """Ottieni lo stato corrente."""
        return self._state
    
    def update_state(self, updater: Callable[[SessionState], SessionState]):
        """
        Aggiorna lo stato (con notifica ai listener).
        
        Come Claude Code's reactive store:
        1. Calcola il nuovo stato
        2. Notifica i listener
        3. Chiama onChange
        """
        old_state = self._state
        self._state = updater(self._state)
        self._state.updated_at = datetime.now().isoformat()
        
        # Notifica listener
        for listener in self._listeners:
            try:
                listener(self._state)
            except Exception:
                pass
        
        # Chiama onChange
        if self._on_change:
            try:
                self._on_change(old_state, self._state)
            except Exception:
                pass
    
    def subscribe(self, listener: Callable[[SessionState], None]):
        """Sottoscrivi un listener ai cambiamenti di stato."""
        self._listeners.add(listener)
        return lambda: self._listeners.discard(listener)
    
    def set_on_change(self, callback: Callable[[SessionState, SessionState], None]):
        """Imposta il callback onChange."""
        self._on_change = callback
    
    # === STATE UPDATES ===
    
    def increment_turns(self):
        """Incrementa il contatore turni."""
        self.update_state(lambda s: self._replace(s, total_turns=s.total_turns + 1))
        self.bootstrap["total_questions"] += 1
    
    def increment_tool_calls(self):
        """Incrementa il contatore tool calls."""
        self.update_state(lambda s: self._replace(s, total_tool_calls=s.total_tool_calls + 1))
    
    def increment_reasoning_steps(self):
        """Incrementa il contatore reasoning steps."""
        self.update_state(lambda s: self._replace(s, total_reasoning_steps=s.total_reasoning_steps + 1))
        self.bootstrap["total_reasoning_steps"] += 1
    
    def increment_errors(self):
        """Incrementa il contatore errori."""
        self.update_state(lambda s: self._replace(s, 
            total_errors=s.total_errors + 1,
            has_errors=True
        ))
    
    def set_question(self, question: str):
        """Imposta la domanda corrente."""
        self.update_state(lambda s: self._replace(s, current_question=question))
    
    def set_confidence(self, confidence: float):
        """Imposta la confidenza corrente."""
        self.update_state(lambda s: self._replace(s, current_confidence=confidence))
    
    def add_reasoning_step(self, step: dict):
        """Aggiungi un passo alla catena di ragionamento."""
        self.update_state(lambda s: self._replace(s, 
            reasoning_chain=s.reasoning_chain + [step]
        ))
    
    def mark_complete(self):
        """Marca la sessione come completa."""
        self.update_state(lambda s: self._replace(s, is_complete=True))
        self.session_history.append(self._state)
        self.bootstrap["total_sessions"] += 1
    
    def mark_llm_used(self):
        """Marca che è stato usato l'LLM."""
        self.update_state(lambda s: self._replace(s, llm_used=True))
    
    def increment_memories_created(self):
        """Incrementa contatore memorie create."""
        self.update_state(lambda s: self._replace(s, memories_created=s.memories_created + 1))
    
    def increment_memories_recalled(self):
        """Incrementa contatore memorie richiamate."""
        self.update_state(lambda s: self._replace(s, memories_recalled=s.memories_recalled + 1))
    
    def _replace(self, state: SessionState, **kwargs) -> SessionState:
        """Crea una copia dello stato con campi aggiornati."""
        new_state = SessionState(
            session_id=state.session_id,
            created_at=state.created_at,
            updated_at=datetime.now().isoformat(),
            total_turns=kwargs.get('total_turns', state.total_turns),
            total_tool_calls=kwargs.get('total_tool_calls', state.total_tool_calls),
            total_reasoning_steps=kwargs.get('total_reasoning_steps', state.total_reasoning_steps),
            total_errors=kwargs.get('total_errors', state.total_errors),
            current_question=kwargs.get('current_question', state.current_question),
            current_confidence=kwargs.get('current_confidence', state.current_confidence),
            reasoning_chain=kwargs.get('reasoning_chain', state.reasoning_chain),
            memories_created=kwargs.get('memories_created', state.memories_created),
            memories_recalled=kwargs.get('memories_recalled', state.memories_recalled),
            is_complete=kwargs.get('is_complete', state.is_complete),
            has_errors=kwargs.get('has_errors', state.has_errors),
            llm_used=kwargs.get('llm_used', state.llm_used)
        )
        return new_state
    
    # === PERSISTENCE ===
    
    def export_session(self) -> dict:
        """Esporta la sessione corrente."""
        return {
            "session_id": self._state.session_id,
            "created_at": self._state.created_at,
            "updated_at": self._state.updated_at,
            "state": {
                "total_turns": self._state.total_turns,
                "total_tool_calls": self._state.total_tool_calls,
                "total_reasoning_steps": self._state.total_reasoning_steps,
                "total_errors": self._state.total_errors,
                "current_question": self._state.current_question,
                "current_confidence": self._state.current_confidence,
                "reasoning_chain": self._state.reasoning_chain,
                "memories_created": self._state.memories_created,
                "memories_recalled": self._state.memories_recalled,
                "is_complete": self._state.is_complete,
                "has_errors": self._state.has_errors,
                "llm_used": self._state.llm_used
            },
            "bootstrap": self.bootstrap
        }
    
    def import_session(self, data: dict):
        """Importa una sessione."""
        state_data = data.get("state", {})
        
        self._state = SessionState(
            session_id=data.get("session_id", ""),
            created_at=data.get("created_at", ""),
            updated_at=data.get("updated_at", ""),
            **state_data
        )
        
        if "bootstrap" in data:
            self.bootstrap.update(data["bootstrap"])
    
    def get_stats(self) -> dict:
        """Statistiche globali."""
        return {
            "current_session": {
                "id": self._state.session_id,
                "turns": self._state.total_turns,
                "tool_calls": self._state.total_tool_calls,
                "errors": self._state.total_errors,
                "confidence": self._state.current_confidence
            },
            "global": {
                "total_sessions": self.bootstrap["total_sessions"],
                "total_questions": self.bootstrap["total_questions"],
                "total_reasoning_steps": self.bootstrap["total_reasoning_steps"]
            },
            "history": len(self.session_history)
        }
