"""SQLAlchemy database engine and session management for app metadata."""

from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine, make_url
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import get_settings


Base = declarative_base()


def _ensure_sqlite_parent_dir(database_url: str) -> None:
    """Create the parent directory for file-backed SQLite app metadata DBs."""
    url = make_url(database_url)
    if url.get_backend_name() != "sqlite" or url.database in (None, ":memory:"):
        return

    Path(url.database).parent.mkdir(parents=True, exist_ok=True)


def get_engine() -> Engine:
    settings = get_settings()
    _ensure_sqlite_parent_dir(settings.app_database_url)
    return create_engine(settings.app_database_url)


def get_session_factory(engine: Engine | None = None):
    if engine is None:
        engine = get_engine()
    return sessionmaker(bind=engine)
