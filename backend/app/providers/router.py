from __future__ import annotations

from typing import Optional
from sqlalchemy.orm import Session

from app.models.domain import AIProviderConfig, UserSettings
from app.providers.base import AIProvider, GenerationResult
from app.providers.gemini_provider import GeminiProvider
from app.providers.ollama_provider import OllamaProvider


DEFAULT_TASK_ROUTING = {
    "general_explanation": "qwen3.5:9b",
    "deep_research": "qwen3.5:9b",
    "coding": "qwen3.5:9b",
    "classification": "qwen3.5:9b",
    "question_generation": "qwen3.5:9b",
}


class ProviderRouter:
    """Routes AI tasks to the user's selected provider and task-specific model."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get_ollama_config(self) -> AIProviderConfig:
        cfg = self.db.query(AIProviderConfig).filter(AIProviderConfig.provider_name == "ollama").first()
        if not cfg:
            cfg = AIProviderConfig(
                provider_name="ollama",
                display_name="Ollama (Local Hardware Engine)",
                is_enabled=True,
                is_default=True,
                base_url="http://127.0.0.1:11434",
                default_model="qwen3.5:9b",
                task_routing_json=dict(DEFAULT_TASK_ROUTING),
                context_length=16384,
                temperature=0.3,
                privacy_notice="100% Local Execution. Zero data leaves your computer.",
                health_status="online",
            )
            self.db.add(cfg)
            self.db.commit()
            self.db.refresh(cfg)
        elif cfg.default_model == "qwen3.5:4b":
            cfg.default_model = "qwen3.5:9b"
            cfg.task_routing_json = dict(DEFAULT_TASK_ROUTING)
            self.db.commit()
            self.db.refresh(cfg)
        return cfg

    def get_gemini_config(self) -> AIProviderConfig:
        cfg = self.db.query(AIProviderConfig).filter(AIProviderConfig.provider_name == "gemini").first()
        if not cfg:
            cfg = AIProviderConfig(
                provider_name="gemini",
                display_name="Google Gemini Developer API (Optional Cloud)",
                is_enabled=False,
                is_default=False,
                base_url="https://generativelanguage.googleapis.com/v1beta",
                default_model="gemini-2.5-flash",
                task_routing_json={},
                context_length=1048576,
                temperature=0.3,
                privacy_notice=(
                    "Privacy Warning: On the Gemini API free tier, Google may review prompts/responses to improve "
                    "products. Axiom OS never transmits Obsidian notes or source code without explicit permission."
                ),
                health_status="disabled",
            )
            self.db.add(cfg)
            self.db.commit()
            self.db.refresh(cfg)
        return cfg

    def get_active_provider(self, task_type: str = "general_explanation") -> tuple[AIProvider, str, bool]:
        from app.services.secret_storage import decrypt_secret
        user_settings = self.db.query(UserSettings).first()
        ollama_cfg = self.get_ollama_config()
        gemini_cfg = self.get_gemini_config()

        gemini_api_key = decrypt_secret(gemini_cfg.encrypted_api_key)
        if (
            gemini_cfg.is_enabled
            and gemini_cfg.is_default
            and gemini_api_key
            and (user_settings is None or user_settings.allow_cloud_ai)
        ):
            model = (gemini_cfg.task_routing_json or {}).get(task_type) or gemini_cfg.default_model
            return (
                GeminiProvider(
                    api_key=gemini_api_key,
                    default_model=model,
                    enabled=True,
                ),
                model,
                False,
            )

        routing = ollama_cfg.task_routing_json or DEFAULT_TASK_ROUTING
        model = routing.get(task_type) or ollama_cfg.default_model or "qwen3.5:9b"
        if model == "qwen3.5:4b" and ollama_cfg.default_model == "qwen3.5:9b":
            model = "qwen3.5:9b"
        return (
            OllamaProvider(base_url=ollama_cfg.base_url, default_model=model),
            model,
            True,
        )

    async def generate_with_fallback(
        self,
        prompt: str,
        system_prompt: str,
        fallback_content: str = "",
        task_type: str = "general_explanation",
        use_live_llm: bool = True,
    ) -> GenerationResult:
        """
        Execute AI generation with automatic resilience.
        Defaults to live model invocation (Ollama / Gemini).
        """
        provider, model, is_local = self.get_active_provider(task_type)
        last_error = None
        if use_live_llm:
            try:
                res = await provider.generate(
                    prompt=prompt,
                    system_prompt=system_prompt,
                    model=model,
                    temperature=0.3,
                    max_tokens=1500,
                )
                if res.content and len(res.content.strip()) > 20:
                    return res
            except Exception as e:
                last_error = str(e)

        if fallback_content:
            return GenerationResult(
                content=fallback_content,
                provider="ollama" if is_local else "gemini",
                model=f"{model} (offline fallback)",
                is_local=is_local,
                tokens_estimated=max(1, len(fallback_content) // 4),
                generation_status="completed" if not last_error else "fallback_used",
                source_retrieval_performed=True,
            )

        err_msg = (
            f"Local AI engine ({model}) is unreachable at http://127.0.0.1:11434. "
            f"Please run 'ollama serve' in your terminal. Error: {last_error or 'Connection timeout'}"
        )
        return GenerationResult(
            content=f"[Axiom OS Engine Offline]\n{err_msg}",
            provider="ollama" if is_local else "gemini",
            model=model,
            is_local=is_local,
            tokens_estimated=1,
            generation_status="error",
            source_retrieval_performed=False,
        )
