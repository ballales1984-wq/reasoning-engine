import json
import os
import time
from typing import Any, Dict, List, Optional
from ..core.types import SourceMetadata


class Concept:
    """Un singolo concetto nel knowledge graph con supporto multi-canale."""

    def __init__(
        self,
        name: str,
        description: str = "",
        examples: list[str] = None,
        category: str = "general",
        channel: str = "local",
    ):
        self.name = name
        # Dati suddivisi per canale: {channel_id: {description, examples, category, metadata}}
        self.channels = {}
        self.relations = {}  # {relation_type: [(target, channel_id)]}

        # Aggiungi il primo canale
        self.update_channel(channel, description, examples, category)

    def update_channel(
        self,
        channel: str,
        description: str = "",
        examples: list[str] = None,
        category: str = "general",
        trust_score: float = None,
    ):
        """Aggiorna o aggiunge dati per un determinato canale."""
        if channel not in self.channels:
            self.channels[channel] = {
                "description": description,
                "examples": examples or [],
                "category": category,
                "last_updated": time.time(),
                "trust_score": trust_score or self._get_default_trust(channel),
            }
        else:
            c_data = self.channels[channel]
            if description:
                c_data["description"] = description
            if examples:
                # Evita duplicati
                for ex in examples:
                    if ex not in c_data["examples"]:
                        c_data["examples"].append(ex)
            if category != "general":
                c_data["category"] = category
            c_data["last_updated"] = time.time()
            if trust_score is not None:
                c_data["trust_score"] = trust_score

    def _get_default_trust(self, channel: str) -> float:
        """Restituisce il punteggio di fiducia predefinito per un canale."""
        trust_map = {
            "local": 1.0,
            "user": 1.0,
            "system": 1.0,
            "financial": 0.9,
            "wikipedia": 0.8,
            "web": 0.5,
            "ollama": 0.4,
        }
        return trust_map.get(channel, 0.5)

    def get_best_info(self) -> dict:
        """Restituisce le migliori informazioni disponibili basate sul trust_score."""
        if not self.channels:
            return {
                "description": "",
                "examples": [],
                "category": "general",
                "channel": "none",
            }

        # Trova il canale con il trust score più alto
        best_channel = max(self.channels.items(), key=lambda x: x[1]["trust_score"])
        return {
            "description": best_channel[1]["description"],
            "examples": best_channel[1]["examples"],
            "category": best_channel[1]["category"],
            "channel": best_channel[0],
            "trust_score": best_channel[1]["trust_score"],
        }

    @property
    def description(self) -> str:
        return self.get_best_info()["description"]

    @property
    def examples(self) -> list:
        return self.get_best_info()["examples"]

    @property
    def category(self) -> str:
        return self.get_best_info()["category"]

    def add_relation(self, relation_type: str, target: str, channel: str = "local"):
        if relation_type not in self.relations:
            self.relations[relation_type] = []

        # Verifica se la relazione esiste già per questo canale
        exists = any(
            r[0] == target and r[1] == channel for r in self.relations[relation_type]
        )
        if not exists:
            self.relations[relation_type].append((target, channel))

    def to_dict(self):
        return {
            "name": self.name,
            "channels": self.channels,
            "relations": self.relations,
        }


class KnowledgeGraph:
    """
    Il grafo di conoscenza multi-canale.
    """

    def __init__(self):
        self.concepts = {}  # {name: Concept}

    def add(
        self,
        name: str,
        description: str = "",
        examples: list[str] = None,
        category: str = "general",
        channel: str = "local",
        trust_score: float = None,
    ) -> Concept:
        """Aggiunge o aggiorna un concetto nel grafo per un determinato canale."""
        if name not in self.concepts:
            self.concepts[name] = Concept(
                name, description, examples, category, channel
            )
            if trust_score is not None:
                self.concepts[name].channels[channel]["trust_score"] = trust_score
        else:
            self.concepts[name].update_channel(
                channel, description, examples, category, trust_score
            )
        return self.concepts[name]

    def get(self, name: str) -> Concept | None:
        """Recupera un concetto per nome (case-insensitive)."""
        if name in self.concepts:
            return self.concepts[name]
        # Case-insensitive fallback
        name_lower = name.lower()
        for key, concept in self.concepts.items():
            if key.lower() == name_lower:
                return concept
        return None

    def find(self, names: list[str]) -> dict:
        """Cerca più concetti. Ritorna {name: Concept|None}."""
        return {name: self.get(name) for name in names}

    def connect(self, source: str, relation: str, target: str, channel: str = "local"):
        """Crea una relazione tra due concetti su un canale specifico."""
        if source in self.concepts:
            # Assicuriamoci che anche il target esista (opzionale, ma consigliato)
            if target not in self.concepts:
                self.add(target, channel=channel)
            self.concepts[source].add_relation(relation, target, channel)

    def list_all(self) -> list[dict]:
        """Lista tutti i concetti."""
        return [c.to_dict() for c in self.concepts.values()]

    def search(self, query: str) -> list[Concept]:
        """Cerca concetti per nome o descrizione (nella info migliore)."""
        results = []
        query_lower = query.lower()
        for concept in self.concepts.values():
            best_info = concept.get_best_info()
            if (
                query_lower in concept.name.lower()
                or query_lower in best_info["description"].lower()
            ):
                results.append(concept)
        return results

    def save(self, filepath: str = None):
        """Salva il knowledge graph su disco (JSON)."""
        if filepath is None:
            filepath = os.path.join(
                os.path.dirname(__file__), "..", "..", "data", "knowledge.json"
            )
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        data = {name: concept.to_dict() for name, concept in self.concepts.items()}
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def load(self, filepath: str = None):
        """Carica il knowledge graph da disco (JSON)."""
        if filepath is None:
            filepath = os.path.join(
                os.path.dirname(__file__), "..", "..", "data", "knowledge.json"
            )
        if not os.path.exists(filepath):
            return
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            for name, cdata in data.items():
                if "channels" in cdata:
                    # Nuovo formato
                    concept = Concept(name=name)
                    concept.channels = cdata.get("channels", {})
                    concept.relations = cdata.get("relations", {})
                else:
                    # Vecchio formato (migrazione)
                    concept = Concept(
                        name=name,
                        description=cdata.get("description", ""),
                        examples=cdata.get("examples", []),
                        category=cdata.get("category", "general"),
                        channel="legacy",
                    )
                    concept.relations = {}
                    # Migrazione relazioni vecchie
                    old_rels = cdata.get("relations", {})
                    for rel_type, targets in old_rels.items():
                        for t in targets:
                            concept.add_relation(rel_type, t, "legacy")

                self.concepts[name] = concept
        except Exception as e:
            print(f"Errore caricamento KnowledgeGraph: {e}")
