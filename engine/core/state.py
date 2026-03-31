"""
State Manager v2 — Come lo state management di Claude Code.
"""

from dataclasses import dataclass, field
from typing import Optional, Any, Callable
from datetime import datetime
import hashlib


@dataclass
class SessionState:
    session_id: str = ""
    created_at: str = ""
    updated_at: str = ""
    total_turns: int = 0
    total_tool_calls: int = 0
    total_reasoning_steps: int = 0
    total_errors: int = 0
    current_question: str = ""
    current_confidence: float = 0.0
    reasoning_chain: list = field(default_factory=list)
    memories_created: int = 0
    memories_recalled: int = 0
    is_complete: bool = False
    has_errors: bool = False
    llm_used: bool = False


class StateManager:
    """Gestione stato, ispirata a Claude Code."""
    
    def __init__(self):
        self.bootstrap = {
            "version": "2.0.0",
            "name": "ReasoningEngine",
            "created_at": datetime.now().isoformat(),
            "total_sessions": 0,
            "total_questions": 0
        }
        self._state = SessionState()
        self._state.session_id = hashlib.md5(datetime.now().isoformat().encode()).hexdigest()[:12]
        self._state.created_at = datetime.now().isoformat()
        self._listeners = set()
        self.session_history = []
    
    def get_state(self) -> SessionState:
        return self._state
    
    def update_state(self, **kwargs):
        old = self._state
        for k, v in kwargs.items():
            if hasattr(self._state, k):
                setattr(self._state, k, v)
        self._state.updated_at = datetime.now().isoformat()
        for listener in self._listeners:
            try:
                listener(self._state)
            except:
                pass
    
    def set_question(self, question: str):
        self.update_state(current_question=question)
    
    def set_confidence(self, confidence: float):
        self.update_state(current_confidence=confidence)
    
    def increment_turns(self):
        self.update_state(total_turns=self._state.total_turns + 1)
        self.bootstrap["total_questions"] += 1
    
    def increment_tool_calls(self):
        self.update_state(total_tool_calls=self._state.total_tool_calls + 1)
    
    def increment_errors(self):
        self.update_state(total_errors=self._state.total_errors + 1, has_errors=True)
    
    def increment_memories_created(self):
        self.update_state(memories_created=self._state.memories_created + 1)
    
    def increment_memories_recalled(self):
        self.update_state(memories_recalled=self._state.memories_recalled + 1)
    
    def mark_complete(self):
        self.update_state(is_complete=True)
        self.session_history.append(self._state)
        self.bootstrap["total_sessions"] += 1
    
    def mark_llm_used(self):
        self.update_state(llm_used=True)
    
    def add_reasoning_step(self, step: dict):
        chain = self._state.reasoning_chain + [step]
        self.update_state(reasoning_chain=chain)
    
    def get_stats(self) -> dict:
        return {
            "current_session": {
                "id": self._state.session_id,
                "turns": self._state.total_turns,
                "tool_calls": self._state.total_tool_calls,
                "confidence": self._state.current_confidence
            },
            "global": {
                "total_sessions": self.bootstrap["total_sessions"],
                "total_questions": self.bootstrap["total_questions"]
            }
        }
    
    def export_session(self) -> dict:
        return {
            "session_id": self._state.session_id,
            "state": self._state.__dict__,
            "bootstrap": self.bootstrap
        }
