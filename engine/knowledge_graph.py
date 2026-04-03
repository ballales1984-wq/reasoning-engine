"""
Backward-compatible alias module.

Legacy scripts import:
    from engine.knowledge_graph import KnowledgeGraph

Current implementation lives in:
    engine.data.graph
"""

from .data.graph import KnowledgeGraph, Concept

__all__ = ["KnowledgeGraph", "Concept"]

