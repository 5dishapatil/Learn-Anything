from __future__ import annotations

import asyncio
from sqlalchemy.orm import Session

from app.database import init_fts5_index, rebuild_fts5_index
from app.models.domain import (
    LearningJourney,
    Note,
    NoteRelationship,
    Reflection,
    Tag,
    UserProfile,
    UserSettings,
)
from app.providers.router import ProviderRouter
from app.services.ai_orchestrator import AIOrchestrationService
from app.services.n8n_connector import N8nAutomationService
from app.services.obsidian_connector import ObsidianConnectorService


async def ensure_seed_data(db: Session) -> None:
    """Seed initial user profile, settings, providers, and flagship hybrid journeys if DB is empty."""
    init_fts5_index(db)

    user = db.query(UserProfile).first()
    if not user:
        user = UserProfile(
            name="Principal Researcher & Builder",
            bio="Exploring complex technical systems from first principles, mathematical derivations, and hands-on engineering.",
            experience_level="intermediate",
            preferred_format="combined",
            daily_minutes_goal=45,
            total_xp=0,
            current_level=1,
            exploration_rank="First-Principles Explorer",
            active_days_count=0,
            last_active_date=None,
        )
        db.add(user)
        db.flush()
        db.add(
            UserSettings(
                user_id=user.id,
                theme="dark",
                default_road_mode="hybrid",
                default_explanation_depth="detailed",
                allow_cloud_ai=False,
                allow_cloud_notes_egress=False,
                allow_cloud_code_egress=False,
                allow_local_code_execution=True,
                enable_optional_streaks=True,
                free_resources_only_default=True,
            )
        )
        db.commit()

    # Ensure Provider & Integration configs exist
    p_router = ProviderRouter(db)
    p_router.get_ollama_config()
    p_router.get_gemini_config()
    ObsidianConnectorService(db).get_config()
    N8nAutomationService(db).get_config()

    # Ensure baseline tags exist for knowledge management
    if db.query(Tag).count() == 0:
        db.add_all([
            Tag(name="first-principles", color="indigo"),
            Tag(name="architecture", color="emerald"),
            Tag(name="research", color="purple"),
            Tag(name="experiments", color="amber"),
        ])
        db.commit()

    rebuild_fts5_index(db)
