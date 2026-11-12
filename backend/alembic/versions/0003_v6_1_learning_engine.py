"""V6.1: Add structured outcome schemas, why_this_day, activity types, and intake profile

Revision ID: 0003_v6_1_learning_engine
Revises: 0002_learning_day_and_jobs
Create Date: 2026-11-12 21:30:00
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

revision: str = "0003_v6_1_learning_engine"
down_revision: Union[str, None] = "0002_learning_day_and_jobs"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = Inspector.from_engine(bind)

    # 1. Update learning_journeys table
    journey_cols = [c["name"] for c in inspector.get_columns("learning_journeys")]
    if "intake_profile_json" not in journey_cols:
        op.add_column("learning_journeys", sa.Column("intake_profile_json", sa.JSON(), server_default="{}", nullable=False))

    # 2. Update learning_days table
    day_cols = [c["name"] for c in inspector.get_columns("learning_days")]

    cols_to_add = [
        ("why_this_day", sa.Column("why_this_day", sa.Text(), server_default="", nullable=False)),
        ("prerequisites_json", sa.Column("prerequisites_json", sa.JSON(), server_default="[]", nullable=False)),
        ("introduced_concepts_json", sa.Column("introduced_concepts_json", sa.JSON(), server_default="[]", nullable=False)),
        ("learning_outcomes_json", sa.Column("learning_outcomes_json", sa.JSON(), server_default="[]", nullable=False)),
        ("scholar_content_markdown", sa.Column("scholar_content_markdown", sa.Text(), server_default="", nullable=False)),
        ("builder_content_markdown", sa.Column("builder_content_markdown", sa.Text(), server_default="", nullable=False)),
        ("builder_activity_type", sa.Column("builder_activity_type", sa.String(60), server_default="code_lab", nullable=False)),
        ("builder_rubric_json", sa.Column("builder_rubric_json", sa.JSON(), server_default="[]", nullable=False)),
        ("assessment_json", sa.Column("assessment_json", sa.JSON(), server_default="{}", nullable=False)),
        ("generation_status", sa.Column("generation_status", sa.String(40), server_default="planned", nullable=False)),
        ("scholar_completed", sa.Column("scholar_completed", sa.Boolean(), server_default="0", nullable=False)),
        ("assessment_completed", sa.Column("assessment_completed", sa.Boolean(), server_default="0", nullable=False)),
    ]

    for col_name, col_def in cols_to_add:
        if col_name not in day_cols:
            op.add_column("learning_days", col_def)

    # Unique index on (journey_id, day_number)
    existing_indexes = [idx["name"] for idx in inspector.get_indexes("learning_days")]
    if "uq_journey_day" not in existing_indexes and "idx_journey_day_unique" not in existing_indexes:
        try:
            op.create_index("uq_journey_day", "learning_days", ["journey_id", "day_number"], unique=True)
        except Exception:
            pass


def downgrade() -> None:
    # SQLite has limited ALTER TABLE DROP COLUMN support in older versions, batch mode handled if needed
    pass
