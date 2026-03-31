"""
MemoryModule — Memoria completa per il ReasoningEngine.

Come la memoria umana:
- Memoria a breve termine: cosa sto pensando ora
- Memoria a lungo termine: cose che so da sempre
- Memoria episodica: esperienze specifiche (cosa è successo)
- Memoria semantica: conoscenza generale (cosa so)
- Memoria procedurale: come fare le cose (abilità)

La memoria permette all'engine di:
1. Imparare dalle esperienze passate
2. Riconoscere situazioni simili
3. Evitare errori già fatti
4. Costruire conoscenza nel tempo
5. Contestualizzare le risposte
"""

from dataclasses import dataclass, field
from typing import Optional, Any
from collections import defaultdict
from datetime import datetime
import json
import hashlib


@dataclass
class MemoryItem:
    """Un singolo elemento di memoria."""
    id: str
    content: str
    memory_type: str  # "episodic", "semantic", "procedural", "working"
    tags: list[str] = field(default_factory=list)
    importance: float = 0.5  # 0 = poco importante, 1 = molto importante
    access_count: int = 0
    created_at: str = ""
    last_accessed: str = ""
    associations: list[str] = field(default_factory=list)  # IDs di elementi collegati
    metadata: dict = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.last_accessed:
            self.last_accessed = self.created_at
    
    def access(self):
        """Registra un accesso a questo elemento."""
        self.access_count += 1
        self.last_accessed = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "content": self.content,
            "memory_type": self.memory_type,
            "tags": self.tags,
            "importance": self.importance,
            "access_count": self.access_count,
            "created_at": self.created_at,
            "last_accessed": self.last_accessed,
            "associations": self.associations,
            "metadata": self.metadata
        }


class MemoryModule:
    """
    Sistema di memoria completo.
    
    Gerarchia:
    ┌─────────────────────────────────────┐
    │        MEMORIA A BREVE TERMINE      │
    │  (working memory - buffer limitato) │
    └──────────────┬──────────────────────┘
                   │ consolidazione
    ┌──────────────▼──────────────────────┐
    │       MEMORIA A LUNGO TERMINE       │
    │                                     │
    │  ┌─────────────┐ ┌───────────────┐  │
    │  │  Episodica  │ │   Semantica   │  │
    │  │ (eventi)    │ │ (conoscenza)  │  │
    │  └─────────────┘ └───────────────┘  │
    │                                     │
    │  ┌─────────────────────────────┐    │
    │  │       Procedurale           │    │
    │  │  (abilità, come fare)       │    │
    │  └─────────────────────────────┘    │
    └─────────────────────────────────────┘
    """
    
    def __init__(self, max_working_memory: int = 10):
        # Working memory (breve termine) — buffer limitato
        self.working_memory = []  # Lista di MemoryItem
        self.max_working_memory = max_working_memory
        
        # Long-term memory (lungo termine)
        self.episodic_memory = {}   # {id: MemoryItem} — eventi specifici
        self.semantic_memory = {}   # {id: MemoryItem} — conoscenza generale
        self.procedural_memory = {} # {id: MemoryItem} — abilità
        
        # Indici per ricerca rapida
        self.tag_index = defaultdict(set)       # {tag: set(ids)}
        self.association_graph = defaultdict(set) # {id: set(associated_ids)}
        
        # Statistiche
        self.total_items = 0
        self.consolidations = 0
        
        # Callback per consolidamento
        self._on_consolidate = None
    
    def remember(self, content: str, memory_type: str = "episodic",
                 tags: list[str] = None, importance: float = 0.5,
                 metadata: dict = None, associations: list[str] = None) -> str:
        """
        Memorizza qualcosa.
        
        memory_type:
        - "episodic": evento specifico ("oggi ho imparato che...")
        - "semantic": conoscenza generale ("i gatti sono mammiferi")
        - "procedural": abilità ("per fare X, fai Y")
        - "working": temporaneo (cosa sto pensando ora)
        
        Ritorna l'ID della memoria.
        """
        # Genera ID univoco
        memory_id = self._generate_id(content, memory_type)
        
        # Crea l'item
        item = MemoryItem(
            id=memory_id,
            content=content,
            memory_type=memory_type,
            tags=tags or [],
            importance=importance,
            associations=associations or [],
            metadata=metadata or {}
        )
        
        # Salva nel tipo corretto di memoria
        if memory_type == "working":
            self._add_to_working_memory(item)
        elif memory_type == "episodic":
            self.episodic_memory[memory_id] = item
        elif memory_type == "semantic":
            self.semantic_memory[memory_id] = item
        elif memory_type == "procedural":
            self.procedural_memory[memory_id] = item
        
        # Aggiorna indici
        for tag in item.tags:
            self.tag_index[tag].add(memory_id)
        
        for assoc_id in item.associations:
            self.association_graph[memory_id].add(assoc_id)
            self.association_graph[assoc_id].add(memory_id)
        
        self.total_items += 1
        return memory_id
    
    def _add_to_working_memory(self, item: MemoryItem):
        """Aggiunge alla working memory (con limite)."""
        self.working_memory.append(item)
        
        # Se supera il limite, consolida il meno importante
        if len(self.working_memory) > self.max_working_memory:
            self._consolidate_least_important()
    
    def _consolidate_least_important(self):
        """
        Consolida l'elemento meno importante dalla working memory
        alla memoria a lungo termine.
        
        Come nel cervello umano: le cose importanti vengono
        trasferite dalla memoria a breve a quella a lungo termine.
        """
        if not self.working_memory:
            return
        
        # Trova il meno importante (meno accessi + bassa importanza)
        least_important = min(
            self.working_memory,
            key=lambda x: (x.importance, x.access_count)
        )
        
        # Rimuovi dalla working memory
        self.working_memory.remove(least_important)
        
        # Decidi in quale memoria a lungo termine metterlo
        if least_important.importance >= 0.7:
            # Importante → memoria semantica
            least_important.memory_type = "semantic"
            self.semantic_memory[least_important.id] = least_important
        else:
            # Meno importante → memoria episodica
            least_important.memory_type = "episodic"
            self.episodic_memory[least_important.id] = least_important
        
        self.consolidations += 1
    
    def recall(self, query: str, memory_type: str = None,
               tags: list[str] = None, limit: int = 5) -> list[MemoryItem]:
        """
        Richiama dalla memoria.
        
        Cerca in tutti i tipi di memoria e restituisce
        i risultati più rilevanti.
        """
        candidates = []
        query_lower = query.lower()
        
        # Cerca in tutti i tipi di memoria
        memories = []
        if memory_type is None or memory_type == "working":
            memories.extend(self.working_memory)
        if memory_type is None or memory_type == "episodic":
            memories.extend(self.episodic_memory.values())
        if memory_type is None or memory_type == "semantic":
            memories.extend(self.semantic_memory.values())
        if memory_type is None or memory_type == "procedural":
            memories.extend(self.procedural_memory.values())
        
        # Filtra per query
        for item in memories:
            score = 0
            
            # Match nel contenuto
            if query_lower in item.content.lower():
                score += 2.0
            
            # Match nei tag
            if tags:
                matching_tags = set(tags) & set(item.tags)
                score += len(matching_tags) * 1.5
            
            # Match parziale
            for word in query_lower.split():
                if word in item.content.lower():
                    score += 0.5
            
            # Bonus per importanza e accessi
            score += item.importance * 0.5
            score += min(item.access_count * 0.1, 1.0)
            
            if score > 0:
                candidates.append((score, item))
        
        # Ordina per rilevanza
        candidates.sort(key=lambda x: x[0], reverse=True)
        
        # Ritorna i top risultati
        results = [item for _, item in candidates[:limit]]
        
        # Registra gli accessi
        for item in results:
            item.access()
        
        return results
    
    def recall_associated(self, memory_id: str, limit: int = 5) -> list[MemoryItem]:
        """
        Richiama elementi ASSOCIATI a un dato elemento.
        
        Come il cervello umano: quando pensi a qualcosa,
        ti vengono in mente cose collegate.
        """
        associated_ids = self.association_graph.get(memory_id, set())
        
        results = []
        for item_id in list(associated_ids)[:limit]:
            item = self._get_item_by_id(item_id)
            if item:
                item.access()
                results.append(item)
        
        return results
    
    def strengthen(self, memory_id: str, amount: float = 0.1):
        """
        Rafforza una memoria (aumenta importanza).
        
        Come nel cervello: più usi una memoria,
        più diventa forte e facile da richiamare.
        """
        item = self._get_item_by_id(memory_id)
        if item:
            item.importance = min(1.0, item.importance + amount)
            item.access()
    
    def weaken(self, memory_id: str, amount: float = 0.1):
        """
        Indebolisce una memoria (diminuisce importanza).
        
        Come nel cervello: le memorie non usate si indeboliscono.
        """
        item = self._get_item_by_id(memory_id)
        if item:
            item.importance = max(0.0, item.importance - amount)
    
    def associate(self, id1: str, id2: str):
        """
        Crea un'associazione tra due elementi di memoria.
        
        Come nel cervello: le cose che si presentano insieme
        si collegano tra loro.
        """
        self.association_graph[id1].add(id2)
        self.association_graph[id2].add(id1)
        
        # Aggiorna anche le liste di associazioni negli item
        item1 = self._get_item_by_id(id1)
        item2 = self._get_item_by_id(id2)
        
        if item1 and id2 not in item1.associations:
            item1.associations.append(id2)
        if item2 and id1 not in item2.associations:
            item2.associations.append(id1)
    
    def get_context(self) -> dict:
        """
        Ottiene il contesto corrente (cosa sta pensando ora).
        
        Basato sulla working memory e gli accessi recenti.
        """
        return {
            "working_memory": [item.content for item in self.working_memory],
            "recent_topics": [item.tags for item in self.working_memory],
            "focus": self.working_memory[-1].content if self.working_memory else None
        }
    
    def _get_item_by_id(self, item_id: str) -> Optional[MemoryItem]:
        """Cerca un item per ID in tutte le memorie."""
        if item_id in self.semantic_memory:
            return self.semantic_memory[item_id]
        if item_id in self.episodic_memory:
            return self.episodic_memory[item_id]
        if item_id in self.procedural_memory:
            return self.procedural_memory[item_id]
        for item in self.working_memory:
            if item.id == item_id:
                return item
        return None
    
    def _generate_id(self, content: str, memory_type: str) -> str:
        """Genera un ID univoco per un elemento di memoria."""
        hash_input = f"{content}:{memory_type}:{datetime.now().isoformat()}"
        return hashlib.md5(hash_input.encode()).hexdigest()[:8]
    
    def get_stats(self) -> dict:
        """Statistiche sulla memoria."""
        return {
            "working_memory": len(self.working_memory),
            "episodic_memory": len(self.episodic_memory),
            "semantic_memory": len(self.semantic_memory),
            "procedural_memory": len(self.procedural_memory),
            "total_items": self.total_items,
            "consolidations": self.consolidations,
            "associations": len(self.association_graph),
            "tags": len(self.tag_index)
        }
    
    def export(self) -> dict:
        """Esporta tutta la memoria come dizionario."""
        return {
            "working_memory": [item.to_dict() for item in self.working_memory],
            "episodic_memory": {k: v.to_dict() for k, v in self.episodic_memory.items()},
            "semantic_memory": {k: v.to_dict() for k, v in self.semantic_memory.items()},
            "procedural_memory": {k: v.to_dict() for k, v in self.procedural_memory.items()},
            "stats": self.get_stats()
        }
    
    def import_data(self, data: dict):
        """Importa memoria da un dizionario."""
        for item_data in data.get("working_memory", []):
            item = MemoryItem(**item_data)
            self.working_memory.append(item)
        
        for k, v in data.get("episodic_memory", {}).items():
            self.episodic_memory[k] = MemoryItem(**v)
        
        for k, v in data.get("semantic_memory", {}).items():
            self.semantic_memory[k] = MemoryItem(**v)
        
        for k, v in data.get("procedural_memory", {}).items():
            self.procedural_memory[k] = MemoryItem(**v)
        
        # Ricostruisci indici
        for memory in [self.episodic_memory, self.semantic_memory, self.procedural_memory]:
            for item in memory.values():
                for tag in item.tags:
                    self.tag_index[tag].add(item.id)
                for assoc_id in item.associations:
                    self.association_graph[item.id].add(assoc_id)
