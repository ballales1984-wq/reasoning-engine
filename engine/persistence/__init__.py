"""
Persistence Layer — Come Claude Code.
"""

import json
import os
from datetime import datetime


class Storage:
    """Storage backend per persistenza."""
    
    def __init__(self, base_path: str = "./data"):
        self.base_path = base_path
        os.makedirs(base_path, exist_ok=True)
    
    def save(self, key: str, data: dict):
        """Salva dati."""
        path = os.path.join(self.base_path, f"{key}.json")
        with open(path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def load(self, key: str) -> dict:
        """Carica dati."""
        path = os.path.join(self.base_path, f"{key}.json")
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
        return {}
    
    def exists(self, key: str) -> bool:
        """Verifica esistenza."""
        return os.path.exists(os.path.join(self.base_path, f"{key}.json"))
    
    def list_keys(self) -> list:
        """Lista tutte le chiavi."""
        return [f.replace('.json', '') for f in os.listdir(self.base_path) if f.endswith('.json')]
    
    def delete(self, key: str):
        """Elimina dati."""
        path = os.path.join(self.base_path, f"{key}.json")
        if os.path.exists(path):
            os.remove(path)
    
    def save_session(self, session_id: str, state: dict):
        """Salva sessione."""
        self.save(f"session_{session_id}", {
            "session_id": session_id,
            "state": state,
            "saved_at": datetime.now().isoformat()
        })
    
    def load_session(self, session_id: str) -> dict:
        """Carica sessione."""
        return self.load(f"session_{session_id}")
    
    def get_stats(self) -> dict:
        """Statistiche storage."""
        keys = self.list_keys()
        return {
            "total_keys": len(keys),
            "base_path": self.base_path
        }
