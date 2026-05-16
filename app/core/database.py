from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_application_settings

_settings = get_application_settings()

database_engine = create_engine(
    _settings.database_url,
    pool_pre_ping=True,
    future=True,
)

DatabaseSessionFactory = sessionmaker(
    bind=database_engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
    future=True,
)


class DatabaseModelBase(DeclarativeBase):
    """Shared declarative base for every SQLAlchemy ORM model in this project."""


def get_database_session() -> Generator[Session, None, None]:
    """FastAPI dependency that yields a request-scoped SQLAlchemy session."""
    session = DatabaseSessionFactory()
    try:
        yield session
    finally:
        session.close()
