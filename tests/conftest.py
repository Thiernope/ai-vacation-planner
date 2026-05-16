"""Shared pytest fixtures.

Tests run against an in-memory SQLite database with the same SQLAlchemy ORM
schema as production. This keeps the suite fast and self-contained — no Postgres
container or `.env` file required.
"""
import os
from collections.abc import Generator

# Inject test settings *before* anything imports `app.core.config`, since
# `ApplicationSettings()` validates required env vars at instantiation time.
os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-not-for-production")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("ACCESS_TOKEN_EXPIRE_MINUTES", "60")

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

# Importing `app.main` transitively imports every route module, which in turn
# imports every ORM model, so `DatabaseModelBase.metadata` is fully populated
# before any test runs `create_all`.
from app.core.database import DatabaseModelBase, get_database_session
from app.main import app


@pytest.fixture(scope="function")
def in_memory_database_session() -> Generator[Session, None, None]:
    """Yield a SQLAlchemy session backed by a fresh in-memory SQLite DB per test."""
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    DatabaseModelBase.metadata.create_all(bind=test_engine)
    TestSessionFactory = sessionmaker(bind=test_engine, autocommit=False, autoflush=False)

    session = TestSessionFactory()
    try:
        yield session
    finally:
        session.close()
        DatabaseModelBase.metadata.drop_all(bind=test_engine)
        test_engine.dispose()


@pytest.fixture(scope="function")
def http_client(in_memory_database_session: Session) -> Generator[TestClient, None, None]:
    """FastAPI TestClient with the database dependency swapped for the test session."""

    def override_get_database_session() -> Generator[Session, None, None]:
        yield in_memory_database_session

    app.dependency_overrides[get_database_session] = override_get_database_session
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
