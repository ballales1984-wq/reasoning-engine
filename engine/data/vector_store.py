import json
import os
import time
from typing import List, Dict
from numba import njit
import numpy as np

@njit(fastmath=True)
def _jit_cosine_similarity(embeddings, query_vec):
    """Calcolo accelerato JIT della similarità (ottimizzato per AMD Vega 8)."""
    n = embeddings.shape[0]
    similarities = np.zeros(n)
    
    query_norm = np.linalg.norm(query_vec)
    if query_norm == 0:
        return similarities
        
    for i in range(n):
        dot = np.dot(embeddings[i], query_vec)
        norm = np.linalg.norm(embeddings[i]) * query_norm
        if norm > 0:
            similarities[i] = dot / norm
            
    return similarities

class VectorStore:
    """
    Gestore di memoria vettoriale locale (RAG) con accelerazione JIT (TurboMode).
    """

    def __init__(self, storage_path: str = "data/vector_store.json"):
        self.storage_path = storage_path
        self.data = []  # List of {text, embedding, metadata}
        self._embedding_matrix = None # Cache per performance GPU/CPU
        self._load()

    def _refresh_matrix(self):
        """Rigenera la matrice degli embedding per ricerca veloce."""
        if not self.data:
            self._embedding_matrix = None
            return
        self._embedding_matrix = np.array([item["embedding"] for item in self.data], dtype=np.float32)

    def add(self, text: str, embedding: List[float], metadata: Dict = None):
        """Aggiunge un nuovo frammento e invalida la cache della matrice."""
        self.data.append({
            "text": text,
            "embedding": embedding,
            "metadata": metadata or {},
            "timestamp": time.time()
        })
        self._embedding_matrix = None # Invalida cache

    def search(self, query_embedding: List[float], top_k: int = 3) -> List[Dict]:
        """Trova i frammenti più simili usando la Turbo Mode JIT."""
        if not self.data:
            return []

        # Rigenera matrice se necessario
        if self._embedding_matrix is None:
            self._refresh_matrix()

        query_vec = np.array(query_embedding, dtype=np.float32)

        # Esecuzione accelerata JIT
        similarities = _jit_cosine_similarity(self._embedding_matrix, query_vec)

        # Prendi i top k risultati
        top_indices = np.argsort(similarities)[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0.05:  # Filtro rumore minimo
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
