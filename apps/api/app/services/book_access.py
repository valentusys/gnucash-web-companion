"""Book access control service."""

from typing import Optional

from sqlalchemy.orm import Session

from app.models import Book, User, UserBookAccess


class AccessDenied(Exception):
    """Raised when a user does not have the required access to a book."""

    def __init__(self, user_id: int, book_id: int, required_role: str):
        self.user_id = user_id
        self.book_id = book_id
        self.required_role = required_role
        super().__init__(
            f"User {user_id} denied {required_role} access to book {book_id}"
        )


_EDIT_ROLES = {"owner", "editor"}
_VIEW_ROLES = {"owner", "editor", "viewer"}


class BookAccessService:
    def __init__(self, session: Session):
        self.session = session

    def get_role(self, user: User, book: Book) -> Optional[str]:
        access = (
            self.session.query(UserBookAccess)
            .filter(
                UserBookAccess.user_id == user.id,
                UserBookAccess.book_id == book.id,
            )
            .first()
        )
        if access is None:
            return None
        return access.role

    def assert_can_view(self, user: User, book: Book) -> None:
        role = self.get_role(user, book)
        if role not in _VIEW_ROLES:
            raise AccessDenied(user.id, book.id, "view")

    def assert_can_edit(self, user: User, book: Book) -> None:
        role = self.get_role(user, book)
        if role not in _EDIT_ROLES:
            raise AccessDenied(user.id, book.id, "edit")
