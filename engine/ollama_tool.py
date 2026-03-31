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
    
    def __init__(self, base_url: str = "http://localhost:11434", default_model: str = "llama3.2"):
        self.base_url = base_url.rstrip('/')
        self.default_model = default_model
        self.conversation_history = []
    
    def is_available(self) -> bool:
        """Verifica se Ollama è disponibile."""
        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags")
            with urllib.request.urlopen(req, timeout=5) as response:
                return response.status == 200
        except:
            return False
    
    def list_models(self) -> dict:
        """Lista i modelli disponibili."""
        try:
            req = urllib.request.Request(f"{self.base_url}/api/tags")
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode())
            
            models = []
            for model in data.get('models', []):
                models.append({
                    'name': model.get('name', ''),
                    'size': model.get('size', 0),
                    'modified': model.get('modified_at', '')
                })
            
            return {
                'success': True,
                'models': models,
                'count': len(models)
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'models': []
            }
    
    def generate(self, prompt: str, model: str = None, 
                 system: str = None, context: list = None) -> dict:
        """
        Genera una risposta usando Ollama.
        
        Args:
            prompt: il prompt
            model: modello da usare (default: llama3.2)
            system: system prompt opzionale
            context: contesto conversazione
        """
        model = model or self.default_model
        
        try:
            payload = {
                'model': model,
                'prompt': prompt,
                'stream': False
            }
            
            if system:
                payload['system'] = system
            
            if context:
                payload['context'] = context
            
            data = json.dumps(payload).encode('utf-8')
            
            req = urllib.request.Request(
                f"{self.base_url}/api/generate",
                data=data,
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=120) as response:
                result = json.loads(response.read().decode())
            
            # Salva nella history
            self.conversation_history.append({
                'role': 'user',
                'content': prompt
            })
            self.conversation_history.append({
                'role': 'assistant',
                'content': result.get('response', '')
            })
            
            return {
                'success': True,
                'response': result.get('response', ''),
                'model': model,
                'eval_count': result.get('eval_count', 0),
                'eval_duration': result.get('eval_duration', 0),
                'context': result.get('context', [])
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'response': None
            }
    
    def chat(self, message: str, model: str = None) -> dict:
        """
        Chat conversazionale con memoria.
        """
        model = model or self.default_model
        
        # Costruisci messaggi
        messages = self.conversation_history.copy()
        messages.append({
            'role': 'user',
            'content': message
        })
        
        try:
            payload = {
                'model': model,
                'messages': messages,
                'stream': False
            }
            
            data = json.dumps(payload).encode('utf-8')
            
            req = urllib.request.Request(
                f"{self.base_url}/api/chat",
                data=data,
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=120) as response:
                result = json.loads(response.read().decode())
            
            assistant_message = result.get('message', {}).get('content', '')
            
            # Aggiorna history
            self.conversation_history.append({
                'role': 'user',
                'content': message
            })
            self.conversation_history.append({
                'role': 'assistant',
                'content': assistant_message
            })
            
            return {
                'success': True,
                'response': assistant_message,
                'model': model
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def pull_model(self, model: str) -> dict:
        """Scarica un modello."""
        try:
            payload = {'name': model}
            data = json.dumps(payload).encode('utf-8')
            
            req = urllib.request.Request(
                f"{self.base_url}/api/pull",
                data=data,
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=300) as response:
                result = json.loads(response.read().decode())
            
            return {
                'success': True,
                'model': model,
                'status': result.get('status', '')
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def embed(self, text: str, model: str = None) -> dict:
        """
        Genera embedding per un testo.
        """
        model = model or self.default_model
        
        try:
            payload = {
                'model': model,
                'prompt': text
            }
            
            data = json.dumps(payload).encode('utf-8')
            
            req = urllib.request.Request(
                f"{self.base_url}/api/embeddings",
                data=data,
                headers={'Content-Type': 'application/json'}
            )
            
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode())
            
            return {
                'success': True,
                'embedding': result.get('embedding', []),
                'dimensions': len(result.get('embedding', []))
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def clear_history(self):
        """Pulisci la history conversazione."""
        self.conversation_history = []
    
    def get_stats(self) -> dict:
        """Statistiche."""
        return {
            'model': self.default_model,
            'base_url': self.base_url,
            'history_length': len(self.conversation_history),
            'available': self.is_available()
        }
