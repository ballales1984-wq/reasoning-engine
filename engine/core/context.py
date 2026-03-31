"""
Context Manager v2 — Gestione contesto, come Claude Code.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class CompactionStrategy(Enum):
    NONE = "none"
    TRUNCATE = "truncate"
    SUMMARIZE = "summarize"
    MEMORY_REPLACE = "memory_replace"
    FULL = "full"


@dataclass
class ContextStats:
    total_messages: int = 0
    estimated_tokens: int = 0
    max_tokens: int = 10000
    usage_percent: float = 0.0
    pressure_level: str = "low"
    compactions_done: int = 0


class ContextManager:
    """Gestione contesto, ispirata a Claude Code."""
    
    def __init__(self, max_tokens: int = 10000, 
                 pressure_threshold: float = 0.7,
                 critical_threshold: float = 0.9):
        self.max_tokens = max_tokens
        self.pressure_threshold = pressure_threshold
        self.critical_threshold = critical_threshold
        self.stats = ContextStats(max_tokens=max_tokens)
    
    def estimate_tokens(self, messages: list) -> int:
        total = 0
        for msg in messages:
            content = msg.get("content", "")
            if isinstance(content, str):
                total += len(content) // 4
        return total
    
    def get_pressure_level(self, messages: list) -> dict:
        tokens = self.estimate_tokens(messages)
        usage = tokens / self.max_tokens
        
        if usage < self.pressure_threshold:
            level = "low"
        elif usage < self.critical_threshold:
            level = "medium"
        elif usage < 0.95:
            level = "high"
        else:
            level = "critical"
        
        self.stats.estimated_tokens = tokens
        self.stats.usage_percent = usage * 100
        self.stats.pressure_level = level
        self.stats.total_messages = len(messages)
        
        return {
            "level": level,
            "usage_percent": usage * 100,
            "tokens_used": tokens,
            "should_compact": usage >= self.critical_threshold
        }
    
    def compact(self, messages: list, strategy: CompactionStrategy = CompactionStrategy.FULL) -> list:
        if strategy == CompactionStrategy.NONE:
            return messages
        
        if strategy == CompactionStrategy.TRUNCATE:
            return self._truncate(messages)
        elif strategy == CompactionStrategy.SUMMARIZE:
            return self._summarize(messages)
        elif strategy == CompactionStrategy.FULL:
            compacted = self._summarize(messages)
            if self.get_pressure_level(compacted)["should_compact"]:
                compacted = self._truncate(compacted)
            return compacted
        
        return messages
    
    def _truncate(self, messages: list, keep_last: int = 10) -> list:
        if len(messages) <= keep_last:
            return messages
        return [{"role": "system", "content": "[Contesto compattato]"}] + messages[-keep_last:]
    
    def _summarize(self, messages: list) -> list:
        if len(messages) <= 5:
            return messages
        old = messages[:-5]
        recent = messages[-5:]
        summary = "[Riassunto] " + " | ".join([m.get("content", "")[:50] for m in old[:5]])
        return [{"role": "system", "content": summary}] + recent
    
    def should_compact(self, messages: list) -> bool:
        return self.get_pressure_level(messages)["should_compact"]
    
    def get_stats(self) -> dict:
        return {
            "total_messages": self.stats.total_messages,
            "estimated_tokens": self.stats.estimated_tokens,
            "max_tokens": self.stats.max_tokens,
            "usage_percent": self.stats.usage_percent,
            "pressure_level": self.stats.pressure_level
        }
