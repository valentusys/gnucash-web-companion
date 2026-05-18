"""Seed service for creating the default book from configuration."""

import logging
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

from sqlalchemy.orm import Session

from app.models import Book, User, UserBookAccess

logger = logging.getLogger(__name__)


def _safe_book_log_label(path: str) -> str:
    """Return a non-sensitive default-book label for logs.

    The app metadata DB must retain the configured path/URI so the backend can
    open the book, but startup logs should not expose directories, credentials,
    hosts, query parameters, or full connection strings.
    """
    parsed = urlparse(path)
    if parsed.scheme and parsed.netloc:
        filename = Path(parsed.path).name
    else:
        filename = Path(path).name

    return filename or "configured default book"


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

    filename = _safe_book_log_label(path)
    name = filename.split(".")[0] or Path(filename).stem or "Default Book"

    book = Book(
        name=name,
        storage_type="sqlite",
        uri_or_path=path,
        is_default=True,
    )
    session.add(book)
    session.commit()
    session.refresh(book)
    logger.info("Seeded default book: %s (%s)", book.name, _safe_book_log_label(path))
    return book


def seed_admin_default_book_access(session: Session) -> Optional[UserBookAccess]:
    """Grant the first admin owner access to the default book when missing.

    This keeps a fresh single-book deployment usable after bootstrap while still
    storing access metadata in app.db instead of the GnuCash book.
    """
    default_book = (
        session.query(Book)
        .filter(Book.is_default.is_(True), Book.is_archived.is_(False))
        .first()
    )
    if default_book is None:
        logger.warning("No default book configured; skipping admin book access seed")
        return None

    admin = session.query(User).filter(User.is_admin.is_(True)).order_by(User.id).first()
    if admin is None:
        logger.warning("No admin user configured; skipping admin book access seed")
        return None

    existing = (
        session.query(UserBookAccess)
        .filter(
            UserBookAccess.user_id == admin.id,
            UserBookAccess.book_id == default_book.id,
        )
        .first()
    )
    if existing is not None:
        return existing

    access = UserBookAccess(user_id=admin.id, book_id=default_book.id, role="owner")
    session.add(access)
    session.commit()
    session.refresh(access)
    logger.info(
        "Seeded owner access for admin '%s' to default book '%s'",
        admin.username,
        default_book.name,
    )
    return access
