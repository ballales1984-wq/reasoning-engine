"""
Persistence — Salva e carica lo stato dell'engine su disco.

Formato: JSON per semplicità e leggibilità.
Supporta: Knowledge Graph, regole, cronologia apprendimento.
"""

import json
import os
from datetime import datetime
from pathlib import Path


class Persistence:
    """
    Gestisce la persistenza dello stato dell'engine.
    """

    def __init__(self, base_dir: str = None):
        self.base_dir = Path(base_dir or os.path.join(os.path.dirname(__file__), "..", "data"))
        self.base_dir.mkdir(parents=True, exist_ok=True)

    # ============================================================
    # SAVE
    # ============================================================

    def save_engine(self, engine, name: str = "default") -> str:
        """
        Salva lo stato completo dell'engine.
        Ritorna il path del file salvato.
        """
        state = {
            "version": "1.0",
            "saved_at": datetime.now().isoformat(),
            "name": name,
            "knowledge_graph": self._export_kg(engine.knowledge),
            "learning_history": self._export_learner(engine.learner),
        }

        filepath = self.base_dir / f"{name}.json"
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)

        return str(filepath)

    def _export_kg(self, kg) -> dict:
        """Esporta il Knowledge Graph come dict JSON-serializable."""
        concepts = {}
        for name, concept in kg.concepts.items():
            concepts[name] = {
                "name": concept.name,
                "description": concept.description,
                "examples": concept.examples,
                "category": concept.category,
                "relations": concept.relations,
            }
        return {"concepts": concepts}

    def _export_learner(self, learner) -> list:
        """Esporta la cronologia di apprendimento."""
        return learner.learning_history

    # ============================================================
    # LOAD
    # ============================================================

    def load_engine(self, engine, name: str = "default") -> bool:
        """
        Carica lo stato dell'engine da file.
        Ritorna True se caricato con successo.
        """
        filepath = self.base_dir / f"{name}.json"
        if not filepath.exists():
            return False

        with open(filepath, "r", encoding="utf-8") as f:
            state = json.load(f)

        # Ripristina Knowledge Graph
        if "knowledge_graph" in state:
            self._import_kg(engine.knowledge, state["knowledge_graph"])

        # Ripristina cronologia apprendimento
        if "learning_history" in state:
            engine.learner.learning_history = state["learning_history"]

        return True

    def _import_kg(self, kg, data: dict):
        """Importa concetti nel Knowledge Graph."""
        for name, cdata in data.get("concepts", {}).items():
            concept = kg.add(
                name,
                description=cdata.get("description", ""),
                examples=cdata.get("examples", []),
                category=cdata.get("category", "general"),
            )
            # Ripristina relazioni
            for rel_type, targets in cdata.get("relations", {}).items():
                for target in targets:
                    kg.connect(name, rel_type, target)

    # ============================================================
    # LIST / DELETE
    # ============================================================

    def list_saves(self) -> list[dict]:
        """Lista tutti i salvataggi disponibili."""
        saves = []
        for f in sorted(self.base_dir.glob("*.json")):
            try:
                with open(f, "r", encoding="utf-8") as fh:
                    state = json.load(fh)
                concepts = len(state.get("knowledge_graph", {}).get("concepts", {}))
                saves.append({
                    "name": f.stem,
                    "path": str(f),
                    "saved_at": state.get("saved_at", "unknown"),
                    "concepts": concepts,
                    "size_kb": round(f.stat().st_size / 1024, 1),
                })
            except (json.JSONDecodeError, KeyError):
                continue
        return saves

    def delete_save(self, name: str) -> bool:
        """Cancella un salvataggio."""
        filepath = self.base_dir / f"{name}.json"
        if filepath.exists():
            filepath.unlink()
            return True
        return False

    def export_text(self, engine) -> str:
        """Esporta lo stato come testo leggibile."""
        lines = []
        lines.append("=" * 50)
        lines.append("ReasoningEngine — Stato Salvato")
        lines.append("=" * 50)

        # Concetti
        concepts = engine.knowledge.list_all()
        lines.append(f"\n📚 Concetti: {len(concepts)}")
        for c in sorted(concepts, key=lambda x: x["name"]):
            lines.append(f"\n  • {c['name']}")
            if c["description"]:
                lines.append(f"    {c['description']}")
            if c["category"] != "general":
                lines.append(f"    Categoria: {c['category']}")
            if c["examples"]:
                lines.append(f"    Esempi: {', '.join(c['examples'][:3])}")
            if c["relations"]:
                for rel, targets in c["relations"].items():
                    for t in targets:
                        lines.append(f"    → {rel}: {t}")

        # Regole
        rules = engine.rules.list_all()
        lines.append(f"\n⚙️ Regole: {len(rules)}")
        for r in rules:
            lines.append(f"  • {r['name']}: {r['description']}")

        # Statistiche
        lines.append(f"\n📊 Totale concetti: {len(concepts)}")
        lines.append(f"📊 Totale regole: {len(rules)}")
        lines.append(f"📊 Lezioni apprese: {len(engine.learner.learning_history)}")

        return "\n".join(lines)
