"""
OllamaTool — Integrazione Ollama per LLM locale.

Permette all'engine di:
- Usare modelli LLM locali (Llama, Mistral, etc.)
- Addestrare/fine-tunare modelli
- Generare risposte
- Usare come fallback quando l'engine non sa rispondere
"""

import urllib.request
import json
import os


class OllamaTool:
    """Tool per Ollama (LLM locale)."""

    def __init__(
        self, base_url: str = "http://127.0.0.1:11434", default_model: str = "gemma3:1b"
    ):
        self.base_url = base_url.rstrip("/")
        self.default_model = default_model
        self.conversation_history = []

    def is_available(self) -> bool:
        """Verifica se Ollama è disponibile."""
        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags")
            with urllib.request.urlopen(req, timeout=5) as response:
                return response.status == 200
        except Exception:
            return False

    def list_models(self) -> dict:
        """Lista i modelli disponibili."""
        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags")
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())

            models = []
            for model in data.get("models", []):
                models.append(
                    {
                        "name": model.get("name", ""),
                        "size": model.get("size", 0),
                        "modified": model.get("modified_at", ""),
                    }
                )

            return {"success": True, "models": models, "count": len(models)}

        except Exception as e:
            return {"success": False, "error": str(e), "models": []}

    def generate(
        self,
        prompt: str,
        model: str = None,
        system: str = None,
        context: list = None,
        timeout: int = 180,
    ) -> dict:
        """Genera una risposta usando Ollama (Auto-detect GPU/CPU)."""
        model = model or self.default_model
        try:
            payload = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "options": {"num_gpu": 1, "num_thread": 8, "temperature": 0.3},
            }
            if system:
                payload["system"] = system
            if context:
                payload["context"] = context

            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                f"{self.base_url}/api/generate",
                data=data,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=timeout) as response:
                result = json.loads(response.read().decode())

            answer = result.get("response", "")
            self.conversation_history.append({"role": "user", "content": prompt})
            self.conversation_history.append({"role": "assistant", "content": answer})

            return {
                "success": True,
                "response": answer,
                "model": model,
                "eval_count": result.get("eval_count", 0),
                "eval_duration": result.get("eval_duration", 0),
                "context": result.get("context", []),
            }
        except Exception as e:
            return {"success": False, "error": str(e), "response": "Errore Ollama"}

    def generate_embedding(self, text: str, model: str = None) -> dict:
        """Genera embedding usando Ollama con accelerazione GPU."""
        model = model or "nomic-embed-text"
        try:
            payload = {
                "model": model,
                "prompt": text,
                "options": {"num_gpu": 1, "num_thread": 8},
            }
            data = json.dumps(payload).encode("utf-8")
            req = urllib.request.Request(
                f"{self.base_url}/api/embeddings",
                data=data,
                headers={"Content-Type": "application/json"},
            )
            with urllib.request.urlopen(req, timeout=60) as response:
                result = json.loads(response.read().decode())

            return {
                "success": True,
                "embedding": result.get("embedding", []),
                "dimensions": len(result.get("embedding", [])),
            }
        except Exception as e:
            return {"success": False, "error": str(e), "embedding": []}

    def chat(self, message: str, model: str = None) -> dict:
        """
        Chat conversazionale con memoria.
        """
        model = model or self.default_model

        # Costruisci messaggi
        messages = self.conversation_history.copy()
        messages.append({"role": "user", "content": message})

        try:
            payload = {"model": model, "messages": messages, "stream": False}

            data = json.dumps(payload).encode("utf-8")

            req = urllib.request.Request(
                f"{self.base_url}/api/chat",
                data=data,
                headers={"Content-Type": "application/json"},
            )

            with urllib.request.urlopen(req, timeout=120) as response:
                result = json.loads(response.read().decode())

            assistant_message = result.get("message", {}).get("content", "")

            # Aggiorna history
            self.conversation_history.append({"role": "user", "content": message})
            self.conversation_history.append(
                {"role": "assistant", "content": assistant_message}
            )

            return {"success": True, "response": assistant_message, "model": model}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def pull_model(self, model: str, timeout: int = 300) -> dict:
        """Scarica un modello."""
        try:
            payload = {"name": model}
            data = json.dumps(payload).encode("utf-8")

            req = urllib.request.Request(
                f"{self.base_url}/api/pull",
                data=data,
                headers={"Content-Type": "application/json"},
            )

            with urllib.request.urlopen(req, timeout=timeout) as response:
                result = json.loads(response.read().decode())

            return {"success": True, "model": model, "status": result.get("status", "")}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def embed(self, text: str, model: str = None) -> dict:
        """Alias per generate_embedding. Genera embedding per un testo."""
        return self.generate_embedding(text, model)

    def clear_history(self):
        """Pulisci la history conversazione."""
        self.conversation_history = []

    def get_stats(self) -> dict:
        """Statistiche."""
        return {
            "model": self.default_model,
            "base_url": self.base_url,
            "history_length": len(self.conversation_history),
            "available": self.is_available(),
        }
