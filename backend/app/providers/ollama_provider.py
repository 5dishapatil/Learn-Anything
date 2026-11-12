from __future__ import annotations

import json
import time
from typing import AsyncIterator, Optional, Type, TypeVar
import httpx
from pydantic import BaseModel

from app.config import settings
from app.providers.base import (
    AIProvider,
    ContextEstimate,
    GenerationResult,
    ModelDescriptor,
    ProviderCapabilities,
    ProviderHealthStatus,
)
from app.providers.hardware import _detect_ollama_cli

T = TypeVar("T", bound=BaseModel)


def _infer_license(model_name: str) -> tuple[str, str]:
    lower = model_name.lower()
    if "gemma" in lower:
        return (
            "Gemma Terms of Use",
            "Google custom open-weight license; subject to Gemma Prohibited Use Policy (not OSI open-source).",
        )
    if "qwen" in lower:
        return ("Apache License 2.0", "Permissive Apache 2.0 open-source license (Alibaba Qwen).")
    if "llama" in lower:
        return ("Llama Community License", "Custom commercial & acceptable-use restrictions by Meta.")
    if "nomic" in lower:
        return ("Apache License 2.0", "Open-source embedding model.")
    return ("Model-Specific License", "Review model repository card before commercial redistribution.")


class OllamaProvider(AIProvider):
    """Primary local-first AI provider powered by Ollama on the user's machine."""

    def __init__(self, base_url: Optional[str] = None, default_model: Optional[str] = None) -> None:
        self.base_url = (base_url or settings.OLLAMA_BASE_URL).rstrip("/")
        self.default_model = default_model or settings.DEFAULT_OLLAMA_MODEL

    async def list_models(self) -> list[ModelDescriptor]:
        models: list[ModelDescriptor] = []
        try:
            async with httpx.AsyncClient(timeout=4.0) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                if resp.status_code == 200:
                    data = resp.json()
                    for item in data.get("models", []):
                        name = item.get("name", "")
                        size_bytes = item.get("size", 0) or 0
                        details = item.get("details", {}) or {}
                        lic_name, lic_notes = _infer_license(name)
                        models.append(
                            ModelDescriptor(
                                name=name,
                                provider="ollama",
                                size_gb=round(size_bytes / (1024**3), 2) if size_bytes else 0.0,
                                family=details.get("family", ""),
                                parameter_size=details.get("parameter_size", ""),
                                quantization=details.get("quantization_level", ""),
                                context_length=16384,
                                license_name=lic_name,
                                usage_restrictions=lic_notes,
                                is_installed=True,
                            )
                        )
        except Exception:
            pass
        return models

    async def health_check(self) -> ProviderHealthStatus:
        installed, version_str = _detect_ollama_cli()
        t0 = time.perf_counter()
        models = await self.list_models()
        latency = round((time.perf_counter() - t0) * 1000.0, 1)

        online = len(models) > 0
        if not online:
            try:
                async with httpx.AsyncClient(timeout=2.5) as client:
                    resp = await client.get(f"{self.base_url}/api/version")
                    online = resp.status_code == 200
            except Exception:
                online = False

        active_model = self.default_model
        installed_names = [m.name for m in models if "embed" not in m.name.lower() and "cloud" not in m.name.lower()]
        if "qwen3.5:9b" in installed_names:
            active_model = "qwen3.5:9b"
        elif installed_names and active_model not in installed_names:
            active_model = installed_names[0]

        msg = (
            f"Ollama online ({version_str}) with {len(models)} local models."
            if online
            else "Ollama API not reachable at localhost:11434. Start `ollama serve` or use deterministic synthesis."
        )
        return ProviderHealthStatus(
            provider="ollama",
            installed=installed or online,
            online=online,
            base_url=self.base_url,
            active_model=active_model,
            available_models=models,
            latency_ms=latency,
            message=msg,
            privacy_mode="local_private",
        )

    async def _resolve_model(self, requested_model: Optional[str]) -> str:
        if requested_model:
            return requested_model
        models = await self.list_models()
        chat_models = [m.name for m in models if "embed" not in m.name.lower() and "cloud" not in m.name.lower()]
        if "qwen3.5:9b" in chat_models:
            return "qwen3.5:9b"
        if self.default_model in chat_models:
            return self.default_model
        if chat_models:
            return chat_models[0]
        return self.default_model

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> GenerationResult:
        target_model = await self._resolve_model(model)
        payload = {
            "model": target_model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "think": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(f"{self.base_url}/api/generate", json=payload)
            resp.raise_for_status()
            data = resp.json()
            text_out = data.get("response", "").strip()
            if "<think>" in text_out and "</think>" in text_out:
                text_out = text_out.split("</think>", 1)[-1].strip()
            return GenerationResult(
                content=text_out,
                provider="ollama",
                model=target_model,
                is_local=True,
                tokens_estimated=max(1, len(text_out) // 4),
                generation_status="completed",
            )

    async def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_prompt: str = "",
        model: Optional[str] = None,
        temperature: float = 0.2,
    ) -> T:
        target_model = await self._resolve_model(model)
        json_schema = schema.model_json_schema()
        payload = {
            "model": target_model,
            "prompt": f"{prompt}\n\nRespond ONLY with valid JSON matching the requested schema.",
            "system": system_prompt,
            "format": json_schema,
            "stream": False,
            "think": False,
            "options": {
                "temperature": temperature,
                "num_predict": 2048,
            },
        }
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(f"{self.base_url}/api/generate", json=payload)
            resp.raise_for_status()
            raw_text = resp.json().get("response", "{}")
            if "<think>" in raw_text and "</think>" in raw_text:
                raw_text = raw_text.split("</think>", 1)[-1].strip()
            return schema.model_validate_json(raw_text)

    async def stream(
        self,
        prompt: str,
        system_prompt: str = "",
        model: Optional[str] = None,
        temperature: float = 0.3,
    ) -> AsyncIterator[str]:
        target_model = await self._resolve_model(model)
        payload = {
            "model": target_model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": True,
            "think": False,
            "options": {"temperature": temperature},
        }
        async with httpx.AsyncClient(timeout=30.0) as client:
            async with client.stream("POST", f"{self.base_url}/api/generate", json=payload) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if not line:
                        continue
                    try:
                        chunk = json.loads(line)
                        token = chunk.get("response", "")
                        if token:
                            yield token
                    except Exception:
                        continue

    def estimate_context(self, text: str, max_context: int = 16384) -> ContextEstimate:
        chars = len(text or "")
        tokens = max(1, chars // 4)
        utilization = round((tokens / max(1, max_context)) * 100.0, 2)
        return ContextEstimate(
            character_count=chars,
            estimated_tokens=tokens,
            max_context_tokens=max_context,
            utilization_percent=utilization,
            fits_in_context=tokens <= max_context,
        )

    def get_capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            provider="ollama",
            supports_streaming=True,
            supports_structured_json=True,
            supports_system_prompt=True,
            supports_embeddings=True,
            is_local=True,
            max_context_length=16384,
        )
