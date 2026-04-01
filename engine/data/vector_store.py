import json
import os
import numpy as np
from typing import Any, Dict, List, Optional
import time

class VectorStore:
    """
    Gestore di memoria vettoriale locale (RAG).
    Memorizza frasi e i loro embeddings per la ricerca semantica.
    """

    def __init__(self, storage_path: str = "data/vector_store.json"):
        self.storage_path = storage_path
        self.data = []  # List of {text, embedding, metadata}
        self._load()

    def add(self, text: str, embedding: List[float], metadata: Dict = None):
        """Aggiunge un nuovo frammento di memoria."""
        self.data.append({
            "text": text,
            "embedding": embedding,
            "metadata": metadata or {},
            "timestamp": time.time()
        })

    def search(self, query_embedding: List[float], top_k: int = 3) -> List[Dict]:
        """Trova i frammenti più simili usando la cosine similarity."""
        if not self.data:
            return []

        # Trasforma in array numpy per calcoli veloci
        embeddings = np.array([item["embedding"] for item in self.data])
        query_vec = np.array(query_embedding)

        # Calcola similarità (Cosine Similarity = dot product / norms)
        # Assumiamo che gli embeddings di Ollama siano già normalizzati o vicini alla norma 1
        dot_products = np.dot(embeddings, query_vec)
        norms = np.linalg.norm(embeddings, axis=1) * np.linalg.norm(query_vec)
        similarities = dot_products / norms

        # Prendi i top k risultati
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.0:  # Evita risultati irrilevanti
                item = self.data[idx].copy()
                item["score"] = float(similarities[idx])
                results.append(item)
        
        return results

    def save(self):
        """Salva i vettori su disco (formato JSON per semplicità e ispezionabilità)."""
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        # Convertiamo numpy arrays in liste se presenti (anche se salviamo già liste)
        serializable_data = []
        for item in self.data:
            new_item = item.copy()
            if isinstance(new_item["embedding"], np.ndarray):
                new_item["embedding"] = new_item["embedding"].tolist()
            serializable_data.append(new_item)
            
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(serializable_data, f, ensure_ascii=False, indent=2)

    def _load(self):
        """Carica la memoria esistente."""
        if os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, "r", encoding="utf-8") as f:
                    self.data = json.load(f)
            except Exception:
                self.data = []

    def clear(self):
        """Svuota la memoria vettoriale."""
        self.data = []
        if os.path.exists(self.storage_path):
            os.remove(self.storage_path)
