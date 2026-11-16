"""Model provider abstractions and opt-in HTTP implementations."""
from __future__ import annotations
import json
from urllib.request import Request, urlopen

class ModelProvider:
    def generate(self, prompt: str, *, system: str = "") -> str:
        raise NotImplementedError

class OfflineProvider(ModelProvider):
    def generate(self, prompt: str, *, system: str = "") -> str:
        return "No model provider is configured. Configure Ollama or an optional remote provider to get a response."

class OllamaProvider(ModelProvider):
    def __init__(self, base_url: str, model: str, timeout: float = 90):
        self.base_url, self.model, self.timeout = base_url.rstrip("/"), model, timeout

    def generate(self, prompt: str, *, system: str = "") -> str:
        payload = {"model": self.model, "prompt": prompt, "system": system, "stream": False}
        request = Request(self.base_url + "/api/generate", data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
        with urlopen(request, timeout=self.timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
        return str(body.get("response", ""))

class OpenAICompatibleProvider(ModelProvider):
    """Optional chat-completions provider; credentials are supplied at runtime."""
    def __init__(self, base_url: str, model: str, api_key: str, timeout: float = 90):
        if not base_url or not model:
            raise ValueError("Remote base URL and model are required")
        self.base_url, self.model, self.api_key, self.timeout = base_url.rstrip("/"), model, api_key, timeout

    def generate(self, prompt: str, *, system: str = "") -> str:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        payload = {"model": self.model, "messages": messages, "stream": False}
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        request = Request(self.base_url + "/chat/completions", data=json.dumps(payload).encode(), headers=headers)
        with urlopen(request, timeout=self.timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
        return str(body["choices"][0]["message"]["content"])
