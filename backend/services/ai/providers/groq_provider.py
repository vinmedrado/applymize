from __future__ import annotations

import httpx

from backend.core.config import settings


class GroqProvider:
    provider_name = "groq"

    def __init__(self, api_key: str | None = None, model: str | None = None):
        self.api_key = api_key if api_key is not None else settings.groq_api_key
        self.model = model or settings.groq_model

    def is_configured(self) -> bool:
        return bool(self.api_key)

    async def chat(self, messages: list[dict[str, str]], timeout_seconds: float = 25.0) -> dict:
        if not self.is_configured():
            raise RuntimeError("Groq API key não configurada")

        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.35,
            "max_tokens": 900,
        }
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        async with httpx.AsyncClient(timeout=timeout_seconds) as client:
            response = await client.post("https://api.groq.com/openai/v1/chat/completions", json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
        answer = (data.get("choices") or [{}])[0].get("message", {}).get("content", "").strip()
        if not answer:
            raise RuntimeError("Groq retornou resposta vazia")
        return {"answer": answer, "provider": self.provider_name, "model": self.model}
