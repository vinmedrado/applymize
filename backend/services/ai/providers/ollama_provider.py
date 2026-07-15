from __future__ import annotations

import httpx

from backend.core.config import settings


class OllamaProvider:
    provider_name = "ollama"

    def __init__(self, model: str | None = None, base_url: str | None = None, enabled: bool | None = None):
        self.model = model or settings.ollama_model
        self.base_url = (base_url or settings.ollama_base_url).rstrip("/")
        self.enabled = settings.ollama_enabled if enabled is None else enabled

    def is_configured(self) -> bool:
        return bool(self.enabled and self.base_url and self.model)

    async def chat(self, messages: list[dict[str, str]], timeout_seconds: float = 45.0) -> dict:
        if not self.is_configured():
            raise RuntimeError("Ollama desabilitado ou não configurado")

        payload = {
            "model": self.model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": 0.35, "num_predict": 900},
        }
        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            response = await client.post(f"{self.base_url}/api/chat", json=payload)
            response.raise_for_status()
            data = response.json()
        answer = (data.get("message") or {}).get("content", "").strip()
        if not answer:
            raise RuntimeError("Ollama retornou resposta vazia")
        return {"answer": answer, "provider": self.provider_name, "model": self.model}
