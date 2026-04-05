"""
MemoryTool — Canale specializzato per la memoria a lungo termine (RAG).
Utilizza Ollama o sentence-transformers per generare embeddings e il VectorStore per salvare/cercare.
"""

import os
from typing import Any, Dict, List, Optional
from ..data.vector_store import VectorStore
from ..llm.ollama import OllamaTool

ST_AVAILABLE = False
SentenceTransformer = None

try:
    from sentence_transformers import SentenceTransformer

    ST_AVAILABLE = True
except ImportError:
    pass


class MemoryTool:
    """Tool per la gestione della memoria semantica."""

    def __init__(self, engine=None):
        self.engine = engine
        self.store = VectorStore()
        self.ollama = OllamaTool()
        self.channel_name = "long_term_memory"
        self.trust_score = 0.85
        self.upload_dir = "data/uploads"
        os.makedirs(self.upload_dir, exist_ok=True)

        self.st_model = None
        self._st_loaded = False

    def _ensure_st_model(self):
        """Lazy load sentence-transformers only when needed."""
        if self._st_loaded:
            return
        if ST_AVAILABLE:
            try:
                self.st_model = SentenceTransformer("all-MiniLM-L6-v2")
            except Exception:
                pass
        self._st_loaded = True

    def _compute_embedding_st(self, text: str) -> List[float]:
        """Compute embedding using sentence-transformers."""
        self._ensure_st_model()
        if self.st_model is None:
            return None
        try:
            emb = self.st_model.encode([text], show_progress_bar=False)
            return emb[0].tolist()
        except Exception:
            return None

    def learn_text(self, text: str, source: str = "user") -> Dict[str, Any]:
        """Impara un testo tramite embedding semantico."""
        try:
            embedding = None

            if self.st_model is not None:
                embedding = self._compute_embedding_st(text)

            if embedding is None:
                res = self.ollama.generate_embedding(text, model="nomic-embed-text")
                if not res.get("success"):
                    return {"success": False, "error": "Embedding failed"}
                embedding = res["embedding"]

            self.store.add(text, embedding, {"source": source})
            self.store.save()

            return {"success": True, "channel": self.channel_name}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def search_semantic(self, query: str, top_k: int = 3) -> Dict[str, Any]:
        """Cerca l'informazione semanticamente."""
        try:
            embedding = None

            if self.st_model is not None:
                embedding = self._compute_embedding_st(query)

            if embedding is None:
                res = self.ollama.generate_embedding(query, model="nomic-embed-text")
                if not res.get("success"):
                    return {"success": False, "error": "Query embedding failed"}
                embedding = res["embedding"]

            results = self.store.search(embedding, top_k=top_k)

            return {"success": True, "matches": results, "channel": self.channel_name}
        except Exception as e:
            return {"success": False, "error": str(e), "matches": []}
