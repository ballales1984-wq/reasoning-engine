"""
ContextManager — Gestione del contesto, ispirata a Claude Code.

Problema: il contesto si riempie (Claude Code ha 200K token, noi abbiamo limiti diversi).
Soluzione: compaction, compression, memory-based replacement.

Come Claude Code:
1. Token counting (stima precisa)
2. Context pressure detection (quando si sta riempiendo)
3. Auto-compaction (comprimi automaticamente)
4. Memory replacement (sostituisci vecchi messaggi con memoria)
"""

from dataclasses import dataclass, field
from typing import Optional, Any
from enum import Enum
import json


class CompactionStrategy(Enum):
    """Strategie di compaction."""
    NONE = "none"                    # Non compattare
    TRUNCATE = "truncate"            # Taglia i vecchi messaggi
    SUMMARIZE = "summarize"          # Riassumi i vecchi messaggi
    MEMORY_REPLACE = "memory_replace"  # Sostituisci con memoria
    FULL = "full"                    # Combina tutte le strategie


@dataclass
class ContextStats:
    """Statistiche sul contesto."""
    total_messages: int = 0
    estimated_tokens: int = 0
    max_tokens: int = 10000         # Limite massimo
    usage_percent: float = 0.0      # 0-100
    pressure_level: str = "low"     # low, medium, high, critical
    compactions_done: int = 0
    messages_removed: int = 0


class ContextManager:
    """
    Gestisce il contesto della conversazione.
    
    Come Claude Code, monitora la pressione del contesto
    e compatta automaticamente quando necessario.
    """
    
    def __init__(self, max_tokens: int = 10000, 
                 pressure_threshold: float = 0.7,
                 critical_threshold: float = 0.9):
        """
        max_tokens: limite massimo di token
        pressure_threshold: soglia per iniziare a monitorare (0.7 = 70%)
        critical_threshold: soglia per compattare (0.9 = 90%)
        """
        self.max_tokens = max_tokens
        self.pressure_threshold = pressure_threshold
        self.critical_threshold = critical_threshold
        
        # Statistiche
        self.stats = ContextStats(max_tokens=max_tokens)
        
        # Cronologia compattazioni
        self.compaction_log = []
    
    def estimate_tokens(self, messages: list[dict]) -> int:
        """
        Stima i token di una lista di messaggi.
        
        Come Claude Code, usa una stima approssimativa (4 char ≈ 1 token)
        invece di chiamare l'API del tokenizer.
        """
        total = 0
        
        for msg in messages:
            content = msg.get("content", "")
            if isinstance(content, str):
                # Stima: ~4 caratteri per token
                total += len(content) // 4
            elif isinstance(content, list):
                for item in content:
                    if isinstance(item, str):
                        total += len(item) // 4
                    elif isinstance(item, dict):
                        total += len(str(item)) // 4
        
        return total
    
    def get_pressure_level(self, messages: list[dict]) -> dict:
        """
        Calcola il livello di pressione del contesto.
        
        Come Claude Code, ritorna:
        - level: "low", "medium", "high", "critical"
        - usage_percent: percentuale usata
        - should_compact: se serve compattare
        """
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
        
        # Aggiorna stats
        self.stats.estimated_tokens = tokens
        self.stats.usage_percent = usage * 100
        self.stats.pressure_level = level
        self.stats.total_messages = len(messages)
        
        return {
            "level": level,
            "usage_percent": usage * 100,
            "tokens_used": tokens,
            "tokens_available": self.max_tokens - tokens,
            "should_compact": usage >= self.critical_threshold
        }
    
    def compact(self, messages: list[dict], 
                strategy: CompactionStrategy = CompactionStrategy.FULL,
                memory_module = None) -> list[dict]:
        """
        Compatta i messaggi per liberare spazio.
        
        Come Claude Code, diverse strategie:
        1. TRUNCATE: rimuovi i messaggi più vecchi
        2. SUMMARIZE: riassumi i messaggi vecchi
        3. MEMORY_REPLACE: sostituisci con memoria
        4. FULL: combina tutto
        """
        if strategy == CompactionStrategy.NONE:
            return messages
        
        original_count = len(messages)
        
        if strategy == CompactionStrategy.TRUNCATE:
            compacted = self._truncate(messages)
        
        elif strategy == CompactionStrategy.SUMMARIZE:
            compacted = self._summarize(messages)
        
        elif strategy == CompactionStrategy.MEMORY_REPLACE:
            compacted = self._memory_replace(messages, memory_module)
        
        elif strategy == CompactionStrategy.FULL:
            # Prima riassumi, poi tronca se necessario
            compacted = self._summarize(messages)
            pressure = self.get_pressure_level(compacted)
            if pressure["should_compact"]:
                compacted = self._truncate(compacted)
        
        else:
            compacted = messages
        
        # Log della compattazione
        removed = original_count - len(compacted)
        self.stats.compactions_done += 1
        self.stats.messages_removed += removed
        
        self.compaction_log.append({
            "strategy": strategy.value,
            "original_messages": original_count,
            "compacted_messages": len(compacted),
            "messages_removed": removed
        })
        
        return compacted
    
    def _truncate(self, messages: list[dict], keep_last: int = 10) -> list[dict]:
        """
        Tronca i messaggi, tenendo solo gli ultimi N.
        
        Come Claude Code: preserva sempre i messaggi recenti.
        """
        if len(messages) <= keep_last:
            return messages
        
        # Tieni il primo messaggio (system/user iniziale) + gli ultimi N
        first = messages[0] if messages else None
        last = messages[-keep_last:]
        
        result = []
        if first:
            # Aggiungi un marker di compattazione
            result.append({
                "role": "system",
                "content": f"[Contesto compattato: {len(messages) - keep_last - 1} messaggi rimossi]"
            })
            if first.get("role") != "system":
                result.append(first)
        result.extend(last)
        
        return result
    
    def _summarize(self, messages: list[dict]) -> list[dict]:
        """
        Riassumi i messaggi vecchi.
        
        Come Claude Code: crea un riassunto dei messaggi vecchi
        e lo sostituisce agli originali.
        """
        if len(messages) <= 5:
            return messages
        
        # Separa vecchi e recenti
        old_messages = messages[:-5]
        recent_messages = messages[-5:]
        
        # Crea riassunto dei vecchi
        summary_parts = []
        for msg in old_messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            if isinstance(content, str):
                # Prendi solo le prime 100 parole
                words = content.split()[:100]
                summary_parts.append(f"{role}: {' '.join(words)}...")
        
        summary = "[Riassunto conversazione precedente]\n" + "\n".join(summary_parts)
        
        result = [
            {"role": "system", "content": summary},
            *recent_messages
        ]
        
        return result
    
    def _memory_replace(self, messages: list[dict], memory_module) -> list[dict]:
        """
        Sostituisci messaggi vecchi con memoria.
        
        Come Claude Code: usa MEMORY.md per sostituire la storia.
        """
        if not memory_module or len(messages) <= 5:
            return messages
        
        # Separa vecchi e recenti
        old_messages = messages[:-5]
        recent_messages = messages[-5:]
        
        # Estrai punti chiave dai vecchi messaggi
        key_points = []
        for msg in old_messages:
            content = msg.get("content", "")
            if isinstance(content, str) and len(content) > 50:
                # Salva in memoria episodica
                memory_id = memory_module.remember(
                    content[:200],
                    memory_type="episodic",
                    tags=["conversation"],
                    importance=0.3
                )
                key_points.append(f"Memoria {memory_id}: {content[:100]}...")
        
        memory_content = "[Memoria dalla conversazione]\n" + "\n".join(key_points[:10])
        
        result = [
            {"role": "system", "content": memory_content},
            *recent_messages
        ]
        
        return result
    
    def get_stats(self) -> dict:
        """Statistiche sul contesto."""
        return {
            "total_messages": self.stats.total_messages,
            "estimated_tokens": self.stats.estimated_tokens,
            "max_tokens": self.stats.max_tokens,
            "usage_percent": self.stats.usage_percent,
            "pressure_level": self.stats.pressure_level,
            "compactions_done": self.stats.compactions_done,
            "messages_removed": self.stats.messages_removed
        }
    
    def should_compact(self, messages: list[dict]) -> bool:
        """Verifica se serve compattare."""
        pressure = self.get_pressure_level(messages)
        return pressure["should_compact"]
