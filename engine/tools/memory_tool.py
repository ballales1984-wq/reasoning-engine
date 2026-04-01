"""
MemoryTool — Canale specializzato per la memoria a lungo termine (RAG).
Utilizza Ollama per generare embeddings e il VectorStore per salvare/cercare.
"""

import os
import time
from typing import Any, Dict, List, Optional
from ..data.vector_store import VectorStore
from ..llm.ollama import OllamaTool


class MemoryTool:
    """
    Tool per la gestione della memoria semantica.
    """

    def __init__(self, engine=None):
        self.engine = engine
        self.store = VectorStore()
        self.ollama = OllamaTool()
        self.channel_name = "long_term_memory"
        self.trust_score = 0.85
        self.upload_dir = "data/uploads"
        os.makedirs(self.upload_dir, exist_ok=True)

    def learn_text(self, text: str, source: str = "user"):
        """Impara un testo tramite embedding semantico."""
        try:
            # 1. Genera embedding via Ollama
            res = self.ollama.generate_embedding(text, model="nomic-embed-text")
            if not res.get("success"):
                return {"success": False, "error": "Embedding failed via Ollama"}
            
            embedding = res["embedding"]
            
            # 2. Salva nel VectorStore
            self.store.add(text, embedding, {"source": source})
            self.store.save()
            
            return {"success": True, "channel": self.channel_name}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def search_semantic(self, query: str, top_k: int = 3) -> dict:
        """Cerca l'informazione semanticamente più vicina."""
        try:
            # 1. Genera embedding della query
            res = self.ollama.generate_embedding(query, model="nomic-embed-text")
            if not res.get("success"):
                return {"success": False, "error": "Query embedding failed"}
            
            # 2. Cerca nel VectorStore
            results = self.store.search(res["embedding"], top_k=top_k)
            
            return {
                "success": True,
                "matches": results,
                "channel": self.channel_name
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def scan_uploads(self) -> int:
        """Scansiona la cartella uploads e impara i nuovi file TXT."""
        count = 0
        for filename in os.listdir(self.upload_dir):
            if filename.endswith(".txt"):
                filepath = os.path.join(self.upload_dir, filename)
                with open(filepath, "r", encoding="utf-8") as f:
                    content = f.read()
                    # Dividi in frammenti se troppo lungo (chunking semplice)
                    chunks = [content[i:i+1000] for i in range(0, len(content), 800)]
                    for chunk in chunks:
                        self.learn_text(chunk, source=filename)
                        count += 1
                # Mark as processed or move? Per ora lasciamolo.
        return count
