"""Book registry service for resolving books from the app metadata DB."""

from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session, joinedload

from app.models import Book, User, UserBookAccess


class BookRegistryService:
    def __init__(self, session: Session):
        self.session = session

    def get_default_book(self) -> Optional[Book]:
        return (
            self.session.query(Book)
            .options(joinedload(Book.health_snapshot), joinedload(Book.access_entries))
            .filter(
                Book.is_default.is_(True),
                Book.is_archived.is_(False),
                Book.is_enabled.is_(True),
            )
            .first()
        )

    def list_books_for_user(self, user: User) -> list[Book]:
        return (
            self.session.query(Book)
            .options(joinedload(Book.health_snapshot), joinedload(Book.access_entries))
            .join(UserBookAccess, UserBookAccess.book_id == Book.id)
            .filter(
                UserBookAccess.user_id == user.id,
                Book.is_archived.is_(False),
                Book.is_enabled.is_(True),
            )
            .order_by(func.lower(Book.name), Book.id)
            .all()
        )

    def get_book(self, book_id: int) -> Optional[Book]:
        return (
            self.session.query(Book)
            .options(joinedload(Book.health_snapshot), joinedload(Book.access_entries))
            .filter(Book.id == book_id)
            .first()
        )
