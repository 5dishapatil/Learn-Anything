from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Optional, Type, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T", bound=BaseModel)


class ModelDescriptor(BaseModel):
    name: str
    provider: str
    size_gb: float = 0.0
    family: str = ""
    parameter_size: str = ""
    quantization: str = ""
    context_length: int = 16384
    license_name: str = "Open-Weight License"
    usage_restrictions: str = "Check model card for commercial/redistribution terms."
    is_installed: bool = True


class ProviderHealthStatus(BaseModel):
    provider: str
    installed: bool
    online: bool
    base_url: str
    active_model: str
    available_models: list[ModelDescriptor] = Field(default_factory=list)
    latency_ms: float = 0.0
    message: str = ""
    privacy_mode: str = "local_private"  # local_private | cloud_opt_in


class ContextEstimate(BaseModel):
    character_count: int
    estimated_tokens: int
    max_context_tokens: int
    utilization_percent: float
    fits_in_context: bool


class ProviderCapabilities(BaseModel):
    provider: str
    supports_streaming: bool = True
    supports_structured_json: bool = True
    supports_system_prompt: bool = True
    supports_embeddings: bool = True
    is_local: bool = True
    max_context_length: int = 16384


class GenerationResult(BaseModel):
    content: str
    provider: str
    model: str
    is_local: bool
    tokens_estimated: int = 0
    generation_status: str = "completed"
    source_retrieval_performed: bool = False


class AIProvider(ABC):
    """Unified abstraction for local and optional cloud AI providers."""

    @abstractmethod
    async def health_check(self) -> ProviderHealthStatus:
        """Inspect installation, connectivity, and available models."""

    @abstractmethod
    async def list_models(self) -> list[ModelDescriptor]:
        """Discover models available on this provider."""

    @abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> GenerationResult:
        """Generate text from prompt."""

    @abstractmethod
    async def generate_structured(
        self,
        prompt: str,
        schema: Type[T],
        system_prompt: str = "",
        model: Optional[str] = None,
        temperature: float = 0.2,
    ) -> T:
        """Generate and validate a structured Pydantic model response."""

    @abstractmethod
    async def stream(
        self,
        prompt: str,
        system_prompt: str = "",
        model: Optional[str] = None,
        temperature: float = 0.3,
    ) -> AsyncIterator[str]:
        """Stream generated tokens incrementally."""

    @abstractmethod
    def estimate_context(self, text: str, max_context: int = 16384) -> ContextEstimate:
        """Estimate token usage and context window fit."""

    @abstractmethod
    def get_capabilities(self) -> ProviderCapabilities:
        """Report provider capabilities."""
