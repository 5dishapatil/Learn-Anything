from __future__ import annotations

import asyncio
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db, init_fts5_index
from app.seed.initial_data import ensure_seed_data

TEST_DB_PATH = Path("backend/test_axiom.db")
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_PATH.resolve()}"


@pytest.fixture(scope="session")
def test_db_session_factory():
    if TEST_DB_PATH.exists():
        try:
            TEST_DB_PATH.unlink()
        except Exception:
            pass

    test_engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        future=True,
    )
    Base.metadata.create_all(bind=test_engine)
    TestingSessionLocal = sessionmaker(bind=test_engine, autoflush=False, autocommit=False, expire_on_commit=False)

    db = TestingSessionLocal()
    init_fts5_index(db)
    asyncio.run(ensure_seed_data(db))
    db.close()

    yield TestingSessionLocal

    test_engine.dispose()
    if TEST_DB_PATH.exists():
        try:
            TEST_DB_PATH.unlink()
        except Exception:
            pass


@pytest.fixture(scope="module")
def client(test_db_session_factory):
    def override_get_db():
        db = test_db_session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
