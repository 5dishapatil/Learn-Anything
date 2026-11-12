from __future__ import annotations

import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


BACKEND_DIR = Path(__file__).resolve().parent.parent
WORKSPACE_DIR = BACKEND_DIR.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=(str(WORKSPACE_DIR / ".env"), str(BACKEND_DIR / ".env")),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    APP_NAME: str = "Axiom OS — Personal AI Research, Learning & Creation OS"
    APP_VERSION: str = "3.0.0"
    APP_ENV: str = "development"
    HOST: str = "127.0.0.1"
    PORT: int = 8000

    # Database
    DATABASE_URL: str = f"sqlite:///{(BACKEND_DIR / 'axiom.db').as_posix()}"

    # Ollama (Primary Default Local Provider)
    OLLAMA_BASE_URL: str = "http://127.0.0.1:11434"
    DEFAULT_OLLAMA_MODEL: str = "qwen3.5:9b"

    # Optional Cloud Provider (Disabled by default; requires explicit user opt-in)
    ALLOW_CLOUD_AI: bool = False
    GEMINI_API_KEY: str = ""
    DEFAULT_GEMINI_MODEL: str = "gemini-2.5-flash"

    # Resource Discovery Optional Keys
    GITHUB_TOKEN: str = ""
    YOUTUBE_API_KEY: str = ""
    OPENALEX_MAILTO: str = "researcher@axiom-local.os"

    # Obsidian Integration
    OBSIDIAN_REST_URL: str = "http://127.0.0.1:27123"
    OBSIDIAN_API_TOKEN: str = ""
    OBSIDIAN_DEFAULT_VAULT: str = "Learning OS"
    OBSIDIAN_APPROVED_FOLDER: str = ""

    # Optional Local n8n Automation
    N8N_BASE_URL: str = "http://127.0.0.1:5678"
    N8N_WEBHOOK_SECRET: str = "axiom-local-webhook-secret"

    # Storage paths
    BACKUPS_DIR: Path = BACKEND_DIR / "backups"
    SANDBOX_DIR: Path = BACKEND_DIR / "sandbox_runs"


settings = Settings()
settings.BACKUPS_DIR.mkdir(parents=True, exist_ok=True)
settings.SANDBOX_DIR.mkdir(parents=True, exist_ok=True)
