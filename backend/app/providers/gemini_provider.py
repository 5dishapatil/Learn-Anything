from __future__ import annotations

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

T = TypeVar("T", bound=BaseModel)


class GeminiProvider(AIProvider):
    """Optional cloud AI provider using Google Gemini Developer API (Explicit User Opt-In Only)."""

    BASE_URL = "https://generativelanguage.googleapis.com/v1beta"

    def __init__(
        self,
        api_key: Optional[str] = None,
        default_model: Optional[str] = None,
        enabled: Optional[bool] = None,
    ) -> None:
        self.api_key = api_key if api_key is not None else settings.GEMINI_API_KEY
        self.default_model = default_model or settings.DEFAULT_GEMINI_MODEL
        self.enabled = enabled if enabled is not None else settings.ALLOW_CLOUD_AI

    def _ensure_permitted(self) -> None:
        if not self.enabled:
            raise PermissionError(
                "Gemini Cloud Provider is disabled by default. Explicit user opt-in is required in Settings."
            )
        if not self.api_key:
            raise PermissionError("Gemini API Key is not configured.")

    async def list_models(self) -> list[ModelDescriptor]:
        if not self.enabled or not self.api_key:
            return [
                ModelDescriptor(
                    name="gemini-2.5-flash",
                    provider="gemini",
                    context_length=1048576,
                    license_name="Google APIs Terms of Service",
                    usage_restrictions="Free tier prompts may be reviewed by Google; Paid tier does not train on data.",
                    is_installed=False,
                ),
                ModelDescriptor(
                    name="gemini-2.5-pro",
                    provider="gemini",
                    context_length=1048576,
                    license_name="Google APIs Terms of Service",
                    usage_restrictions="Free tier prompts may be reviewed by Google; Paid tier does not train on data.",
                    is_installed=False,
                ),
            ]
        try:
            async with httpx.AsyncClient(timeout=6.0) as client:
                resp = await client.get(f"{self.BASE_URL}/models", params={"key": self.api_key})
                if resp.status_code == 200:
                    items = resp.json().get("models", [])
                    results: list[ModelDescriptor] = []
                    for item in items:
                        raw_name = item.get("name", "").replace("models/", "")
                        if "gemini" in raw_name and "generateContent" in item.get("supportedGenerationMethods", []):
                            results.append(
                                ModelDescriptor(
                                    name=raw_name,
                                    provider="gemini",
                                    context_length=item.get("inputTokenLimit", 1048576),
                                    license_name="Google Gemini API Terms",
                                    usage_restrictions="Cloud API: Free-tier inputs may be used for service improvement.",
                                    is_installed=True,
                                )
                            )
                    if results:
                        return results
        except Exception:
            pass
        return []

    async def health_check(self) -> ProviderHealthStatus:
        if not self.enabled:
            return ProviderHealthStatus(
                provider="gemini",
                installed=True,
                online=False,
                base_url=self.BASE_URL,
                active_model=self.default_model,
                available_models=await self.list_models(),
                message="Disabled by default (Zero-cost local privacy mode active). Enable in Settings if desired.",
                privacy_mode="cloud_opt_in",
            )
        if not self.api_key:
            return ProviderHealthStatus(
                provider="gemini",
                installed=True,
                online=False,
                base_url=self.BASE_URL,
                active_model=self.default_model,
                available_models=[],
                message="Gemini enabled, but API key is missing.",
                privacy_mode="cloud_opt_in",
            )
        t0 = time.perf_counter()
        models = await self.list_models()
        latency = round((time.perf_counter() - t0) * 1000.0, 1)
        online = len(models) > 0
        return ProviderHealthStatus(
            provider="gemini",
            installed=True,
            online=online,
            base_url=self.BASE_URL,
            active_model=self.default_model,
            available_models=models,
            latency_ms=latency,
            message="Gemini API verified and online." if online else "Could not verify Gemini API key or quota exhausted.",
            privacy_mode="cloud_opt_in",
        )

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> GenerationResult:
        self._ensure_permitted()
        target_model = model or self.default_model
        url = f"{self.BASE_URL}/models/{target_model}:generateContent"
        body: dict = {
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": temperature, "maxOutputTokens": max_tokens},
        }
        if system_prompt:
            body["systemInstruction"] = {"parts": [{"text": system_prompt}]}

        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(url, params={"key": self.api_key}, json=body)
            if resp.status_code == 429:
                raise RuntimeError("Gemini API quota exhausted (HTTP 429). Falling back to local provider.")
            resp.raise_for_status()
            data = resp.json()
            candidates = data.get("candidates", [])
            text_out = ""
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                text_out = "".join(p.get("text", "") for p in parts)
            return GenerationResult(
                content=text_out.strip(),
                provider="gemini",
                model=target_model,
                is_local=False,
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
        self._ensure_permitted()
        res = await self.generate(
            prompt=f"{prompt}\n\nReturn strictly valid JSON conforming to: {schema.model_json_schema()}",
            system_prompt=system_prompt,
            model=model,
            temperature=temperature,
        )
        cleaned = res.content.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.strip("`").removeprefix("json").strip()
        return schema.model_validate_json(cleaned)

    async def stream(
        self,
        prompt: str,
        system_prompt: str = "",
        model: Optional[str] = None,
        temperature: float = 0.3,
    ) -> AsyncIterator[str]:
        res = await self.generate(prompt=prompt, system_prompt=system_prompt, model=model, temperature=temperature)
        yield res.content

    def estimate_context(self, text: str, max_context: int = 1048576) -> ContextEstimate:
        chars = len(text or "")
        tokens = max(1, chars // 4)
        return ContextEstimate(
            character_count=chars,
            estimated_tokens=tokens,
            max_context_tokens=max_context,
            utilization_percent=round((tokens / max_context) * 100.0, 4),
            fits_in_context=tokens <= max_context,
        )

    def get_capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            provider="gemini",
            supports_streaming=True,
            supports_structured_json=True,
            supports_system_prompt=True,
            supports_embeddings=True,
            is_local=False,
            max_context_length=1048576,
        )
