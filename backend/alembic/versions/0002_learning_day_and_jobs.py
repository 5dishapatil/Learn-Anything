"""Add LearningDay and GenerationJob tables for full-duration curricula and durable background jobs

Revision ID: 0002_learning_day_and_jobs
Revises: 0001_initial_schema
Create Date: 2026-11-12 20:30:00
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from app.database import Base
import app.models  # noqa: F401

revision: str = "0002_learning_day_and_jobs"
down_revision: Union[str, None] = "0001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    pass
