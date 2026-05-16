"""Seed service for creating the default book from configuration."""

import logging
from pathlib import Path
from typing import Optional

from sqlalchemy.orm import Session

from app.models import Book

logger = logging.getLogger(__name__)


def seed_default_book(session: Session, path: Optional[str]) -> Optional[Book]:
    """Seed the default book from GNUCASH_DEFAULT_BOOK_PATH.

    If path is None or empty, logs a warning and returns None.
    If a default book already exists, returns it (idempotent).
    """
    if not path:
        logger.warning(
            "GNUCASH_DEFAULT_BOOK_PATH is not set; skipping default book seed"
        )
        return None

    existing = (
        session.query(Book).filter(Book.is_default.is_(True)).first()
    )
    if existing is not None:
        return existing

    filename = Path(path).name
    name = filename.split(".")[0] or Path(path).stem or "Default Book"

    book = Book(
        name=name,
        storage_type="sqlite",
        uri_or_path=path,
        is_default=True,
    )
    session.add(book)
    session.commit()
    session.refresh(book)
    logger.info("Seeded default book: %s (%s)", book.name, book.uri_or_path)
    return book
