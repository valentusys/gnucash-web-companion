"""Book registry service for resolving books from the app metadata DB."""

from typing import Optional

from sqlalchemy import and_, func
from sqlalchemy.orm import Session, joinedload

from app.models import Book, User, UserBookAccess


class BookRegistryService:
    def __init__(self, session: Session):
        self.session = session

    def get_default_book(self) -> Optional[Book]:
        return (
            self.session.query(Book)
            .options(joinedload(Book.health_snapshot))
            .filter(
                Book.is_default.is_(True),
                Book.is_archived.is_(False),
                Book.is_enabled.is_(True),
            )
            .first()
        )

    def get_default_book_for_user(self, user: User) -> Optional[Book]:
        row = (
            self.session.query(Book, UserBookAccess.role)
            .options(joinedload(Book.health_snapshot))
            .outerjoin(
                UserBookAccess,
                and_(
                    UserBookAccess.book_id == Book.id,
                    UserBookAccess.user_id == user.id,
                ),
            )
            .filter(
                Book.is_default.is_(True),
                Book.is_archived.is_(False),
                Book.is_enabled.is_(True),
            )
            .first()
        )
        if row is None:
            return None
        book, role = row
        _cache_current_user_access_role(book, user_id=int(user.id), role=role)
        return book

    def list_books_for_user(self, user: User) -> list[Book]:
        rows = (
            self.session.query(Book, UserBookAccess.role)
            .options(joinedload(Book.health_snapshot))
            .join(UserBookAccess, UserBookAccess.book_id == Book.id)
            .filter(
                UserBookAccess.user_id == user.id,
                Book.is_archived.is_(False),
                Book.is_enabled.is_(True),
            )
            .order_by(func.lower(Book.name), Book.id)
            .all()
        )
        books: list[Book] = []
        for book, role in rows:
            _cache_current_user_access_role(book, user_id=int(user.id), role=role)
            books.append(book)
        return books

    def get_book(self, book_id: int) -> Optional[Book]:
        return (
            self.session.query(Book)
            .options(joinedload(Book.health_snapshot))
            .filter(Book.id == book_id)
            .first()
        )

    def get_book_for_user(self, book_id: int, user: User) -> Optional[Book]:
        row = (
            self.session.query(Book, UserBookAccess.role)
            .options(joinedload(Book.health_snapshot))
            .outerjoin(
                UserBookAccess,
                and_(
                    UserBookAccess.book_id == Book.id,
                    UserBookAccess.user_id == user.id,
                ),
            )
            .filter(Book.id == book_id)
            .first()
        )
        if row is None:
            return None
        book, role = row
        _cache_current_user_access_role(book, user_id=int(user.id), role=role)
        return book


def _cache_current_user_access_role(book: Book, *, user_id: int, role: str | None) -> None:
    setattr(book, "_current_user_access_user_id", int(user_id))
    setattr(book, "_current_user_access_role", role)
