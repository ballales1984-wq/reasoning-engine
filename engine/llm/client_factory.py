from typing import Dict, Any, List, Optional
import json
import urllib.request
import urllib.error


class LLMClient:
    """Unified LLM client supporting Ollama (default) with easy backend switching."""

    def __init__(
        self,
        backend: str = "ollama",
        model: str = "gemma3:1b",
        base_url: str = "http://localhost:11434",
        model_path: str = "models/gemma-3-1b-it-Q4_K_M.gguf",
        temperature: float = 0.0,
    ):
        self.backend = backend
        self.model = model
        self.base_url = base_url
        self.model_path = model_path
        self.temperature = temperature
        self._llm = None

    def chat(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        if self.backend == "ollama":
            return self._ollama_chat(messages, **kwargs)
        elif self.backend == "llama_cpp":
            return self._llamacpp_chat(messages, **kwargs)
        else:
            return self._ollama_chat(messages, **kwargs)

    def _ollama_chat(self, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": kwargs.get("temperature", self.temperature),
            "max_tokens": kwargs.get("max_tokens", 1024),
        }

        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            f"{self.base_url}/v1/chat/completions",
            data=data,
            headers={"Content-Type": "application/json"},
        )

        try:
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return {
                    "message": {"content": result["choices"][0]["message"]["content"]}
                }
        except Exception as e:
            return {"message": {"content": f"Error: {e}"}, "error": True}

    def _llamacpp_chat(
        self, messages: List[Dict[str, str]], **kwargs
    ) -> Dict[str, Any]:
        try:
            from llama_cpp import Llama

            if self._llm is None:
                self._llm = Llama(
                    model_path=self.model_path,
                    n_ctx=8192,
                    n_gpu_layers=-1,
                    verbose=False,
                )

            response = self._llm.create_chat_completion(
                messages=messages,
                temperature=kwargs.get("temperature", self.temperature),
                max_tokens=kwargs.get("max_tokens", 1024),
            )
            return {
                "message": {"content": response["choices"][0]["message"]["content"]}
            }
        except ImportError:
            return {
                "message": {"content": "llama-cpp-python not installed"},
                "error": True,
            }
        except Exception as e:
            return {"message": {"content": f"Error: {e}"}, "error": True}

    def is_available(self) -> bool:
        if self.backend == "ollama":
            try:
                req = urllib.request.Request(f"{self.base_url}/api/tags")
                with urllib.request.urlopen(req, timeout=3) as resp:
                    return resp.status == 200
            except:
                return False
        elif self.backend == "llama_cpp":
            try:
                from llama_cpp import Llama

                return True
            except:
                return False
        return False

    def generate_json(self, prompt: str) -> Dict:
        """Generate JSON response."""
        response = self.chat(
            [{"role": "user", "content": prompt + "\nRispondi SOLO con JSON."}]
        )
        content = response.get("message", {}).get("content", "")
        try:
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1]
            return json.loads(content.strip())
        except:
            return {"error": "parsing_failed", "raw": content}


def create_llm_client(**kwargs) -> LLMClient:
    """Factory to create LLM client."""
    return LLMClient(**kwargs)


if __name__ == "__main__":
    # Test Ollama client
    client = create_llm_client(backend="ollama", model="gemma3:1b")
    print(f"Backend: {client.backend}")
    print(f"Available: {client.is_available()}")
