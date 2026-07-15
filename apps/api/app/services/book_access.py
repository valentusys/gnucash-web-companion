"""Book access control service."""

from typing import Any, Optional

from sqlalchemy import inspect
from sqlalchemy.orm import Session
from sqlalchemy.orm.attributes import NO_VALUE

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
        """Return the current request's persisted role for this book.

        Registry list lookups attach the current user's role from the same
        bounded DB query. Other call paths intentionally avoid eager-loading all
        assignments for a book and fall back to one point lookup.
        """

        user_id = int(user.id)
        if getattr(book, "_current_user_access_user_id", None) == user_id:
            return getattr(book, "_current_user_access_role", None)

        book_state: Any = inspect(book)
        access_entries_state = book_state.attrs.access_entries
        access_entries = access_entries_state.loaded_value
        if access_entries is not NO_VALUE:
            for access in access_entries:
                if access.user_id == user_id:
                    _cache_current_user_access_role(book, user_id=user_id, role=access.role)
                    return access.role
            _cache_current_user_access_role(book, user_id=user_id, role=None)
            return None
        access = (
            self.session.query(UserBookAccess)
            .filter(
                UserBookAccess.user_id == user_id,
                UserBookAccess.book_id == book.id,
            )
            .first()
        )
        if access is None:
            _cache_current_user_access_role(book, user_id=user_id, role=None)
            return None
        _cache_current_user_access_role(book, user_id=user_id, role=access.role)
        return access.role

    def assert_can_view(self, user: User, book: Book) -> None:
        role = self.get_role(user, book)
        if role not in _VIEW_ROLES:
            raise AccessDenied(user.id, book.id, "view")

    def assert_can_edit(self, user: User, book: Book) -> None:
        role = self.get_role(user, book)
        if role not in _EDIT_ROLES:
            raise AccessDenied(user.id, book.id, "edit")


def _cache_current_user_access_role(book: Book, *, user_id: int, role: str | None) -> None:
    setattr(book, "_current_user_access_user_id", int(user_id))
    setattr(book, "_current_user_access_role", role)
