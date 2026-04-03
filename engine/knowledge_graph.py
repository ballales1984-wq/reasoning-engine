"""
Backward-compatible alias module for legacy imports.
"""

from .data.graph import KnowledgeGraph as _NewKnowledgeGraph, Concept


class KnowledgeGraph(_NewKnowledgeGraph):
    """
    Compatibility wrapper.

    Legacy call style observed in old tests:
        add(name, description, category, relations_list)

    New style:
        add(name, description="", examples=None, category="general", channel="local")
    """

    def add(
        self,
        name: str,
        description: str = "",
        examples=None,
        category: str = "general",
        channel: str = "local",
        trust_score: float = None,
    ):
        # Legacy signature adaptation:
        # if examples is actually a category string and category is a list of relations.
        relations_list = None
        if isinstance(examples, str) and isinstance(category, list):
            legacy_category = examples
            relations_list = category
            examples = []
            category = legacy_category

        concept = super().add(
            name=name,
            description=description,
            examples=examples if isinstance(examples, list) else [],
            category=category if isinstance(category, str) else "general",
            channel=channel,
            trust_score=trust_score,
        )

        if relations_list and isinstance(relations_list, list):
            for rel in relations_list:
                if isinstance(rel, (tuple, list)) and len(rel) >= 2:
                    concept.add_relation(str(rel[0]), str(rel[1]), channel=channel)
        return concept


__all__ = ["KnowledgeGraph", "Concept"]
