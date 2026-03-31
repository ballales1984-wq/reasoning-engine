"""
Memory System v2 — Sistema di memoria completo.
"""

from dataclasses import dataclass, field
from typing import Optional
from collections import defaultdict
from datetime import datetime
import hashlib


@dataclass
class MemoryItem:
    id: str
    content: str
    memory_type: str  # working, semantic, episodic, procedural
    tags: list = field(default_factory=list)
    importance: float = 0.5
    access_count: int = 0
    created_at: str = ""
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()


class MemorySystem:
    """Sistema di memoria completo."""
    
    def __init__(self, max_working: int = 10):
        self.max_working = max_working
        self.working = []
        self.semantic = {}
        self.episodic = {}
        self.procedural = {}
        self.tag_index = defaultdict(set)
    
    def remember(self, content: str, memory_type: str = "episodic",
                 tags: list = None, importance: float = 0.5) -> str:
        """Memorizza qualcosa."""
        memory_id = hashlib.md5(f"{content}:{datetime.now()}".encode()).hexdigest()[:8]
        item = MemoryItem(id=memory_id, content=content, memory_type=memory_type,
                         tags=tags or [], importance=importance)
        
        if memory_type == "working":
            self.working.append(item)
            if len(self.working) > self.max_working:
                self.working.pop(0)
        elif memory_type == "semantic":
            self.semantic[memory_id] = item
        elif memory_type == "episodic":
            self.episodic[memory_id] = item
        elif memory_type == "procedural":
            self.procedural[memory_id] = item
        
        for tag in (tags or []):
            self.tag_index[tag].add(memory_id)
        
        return memory_id
    
    def recall(self, query: str, limit: int = 5) -> list:
        """Richiama dalla memoria."""
        results = []
        query_lower = query.lower()
        
        for item in list(self.working) + list(self.semantic.values()) + \
                    list(self.episodic.values()) + list(self.procedural.values()):
            if query_lower in item.content.lower():
                results.append(item)
        
        return results[:limit]
    
    def get_stats(self) -> dict:
        return {
            "working": len(self.working),
            "semantic": len(self.semantic),
            "episodic": len(self.episodic),
            "procedural": len(self.procedural),
            "total": len(self.working) + len(self.semantic) + len(self.episodic) + len(self.procedural)
        }
