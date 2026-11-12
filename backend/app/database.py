from __future__ import annotations

from typing import Generator
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    pass


connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    future=True,
)

if settings.DATABASE_URL.startswith("sqlite"):
    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON;")
        cursor.execute("PRAGMA journal_mode=WAL;")
        cursor.execute("PRAGMA synchronous=NORMAL;")
        cursor.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_fts5_index(db: Session) -> None:
    """Create SQLite FTS5 full-text search index across knowledge, concepts, notes, projects, and resources."""
    if not settings.DATABASE_URL.startswith("sqlite"):
        return
    db.execute(
        text(
            """
            CREATE VIRTUAL TABLE IF NOT EXISTS fts_search_index USING fts5(
                entity_type,
                entity_id UNINDEXED,
                journey_id UNINDEXED,
                title,
                subtitle,
                body,
                tags
            );
            """
        )
    )
    db.commit()


def rebuild_fts5_index(db: Session) -> None:
    """Synchronize relational tables into the SQLite FTS5 virtual table for fast global search."""
    if not settings.DATABASE_URL.startswith("sqlite"):
        return
    init_fts5_index(db)
    db.execute(text("DELETE FROM fts_search_index;"))

    # Index Concepts
    db.execute(
        text(
            """
            INSERT INTO fts_search_index (entity_type, entity_id, journey_id, title, subtitle, body, tags)
            SELECT 'concept', CAST(id AS TEXT), CAST(COALESCE(journey_id, 0) AS TEXT),
                   title, category, COALESCE(summary, ''), COALESCE(mastery_status, '')
            FROM concepts;
            """
        )
    )
    # Index Lessons
    db.execute(
        text(
            """
            INSERT INTO fts_search_index (entity_type, entity_id, journey_id, title, subtitle, body, tags)
            SELECT 'lesson', CAST(id AS TEXT), CAST(COALESCE(concept_id, 0) AS TEXT),
                   title, COALESCE(problem_statement, ''),
                   COALESCE(first_principles_intuition, '') || ' ' || COALESCE(worked_examples, ''),
                   COALESCE(current_depth, 'detailed')
            FROM lessons;
            """
        )
    )
    # Index Notes
    db.execute(
        text(
            """
            INSERT INTO fts_search_index (entity_type, entity_id, journey_id, title, subtitle, body, tags)
            SELECT 'note', CAST(id AS TEXT), CAST(COALESCE(concept_id, 0) AS TEXT),
                   title, COALESCE(note_type, 'concept_note'), COALESCE(content_markdown, ''), COALESCE(slug, '')
            FROM notes;
            """
        )
    )
    # Index Projects
    db.execute(
        text(
            """
            INSERT INTO fts_search_index (entity_type, entity_id, journey_id, title, subtitle, body, tags)
            SELECT 'project', CAST(id AS TEXT), CAST(COALESCE(journey_id, 0) AS TEXT),
                   title, COALESCE(domain, ''), COALESCE(objective, '') || ' ' || COALESCE(architecture_overview, ''),
                   COALESCE(status, '')
            FROM projects;
            """
        )
    )
    # Index Experiments
    db.execute(
        text(
            """
            INSERT INTO fts_search_index (entity_type, entity_id, journey_id, title, subtitle, body, tags)
            SELECT 'experiment', CAST(id AS TEXT), CAST(COALESCE(project_id, 0) AS TEXT),
                   title, COALESCE(hypothesis, ''), COALESCE(observations, '') || ' ' || COALESCE(conclusion, ''),
                   COALESCE(status, '')
            FROM experiments;
            """
        )
    )
    # Index Resources
    db.execute(
        text(
            """
            INSERT INTO fts_search_index (entity_type, entity_id, journey_id, title, subtitle, body, tags)
            SELECT 'resource', CAST(id AS TEXT), '0',
                   title, COALESCE(resource_type, '') || ' (' || COALESCE(access_status, '') || ')',
                   COALESCE(description, '') || ' ' || COALESCE(relevance_explanation, ''),
                   COALESCE(url, '')
            FROM resources;
            """
        )
    )
    db.commit()
