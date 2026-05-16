"""Book registry service for resolving books from the app metadata DB."""

from typing import Optional

from sqlalchemy.orm import Session

from app.models import Book, User, UserBookAccess


class BookRegistryService:
    def __init__(self, session: Session):
        self.session = session

    def get_default_book(self) -> Optional[Book]:
        return (
            self.session.query(Book)
            .filter(Book.is_default.is_(True), Book.is_archived.is_(False))
            .first()
        )

    def list_books_for_user(self, user: User) -> list[Book]:
        return (
            self.session.query(Book)
            .join(UserBookAccess, UserBookAccess.book_id == Book.id)
            .filter(
                UserBookAccess.user_id == user.id,
                Book.is_archived.is_(False),
            )
            .all()
        )

    def get_book(self, book_id: int) -> Optional[Book]:
        return self.session.query(Book).filter(Book.id == book_id).first()
