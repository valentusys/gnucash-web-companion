"""Book-aware books and accounts API router."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models import Book, User
from app.routers.auth import get_current_user, get_db
from app.services.book_access import AccessDenied, BookAccessService
from app.services.book_registry import BookRegistryService
from app.services.gnucash_book import GnuCashBookService
from app.services.gnucash_exceptions import (
    BookNotConfiguredError,
    BookNotFoundError,
    EntityNotFoundError,
    GnuCashReadError,
)

router = APIRouter(prefix="/books", tags=["books"])


def serialize_book(book: Book) -> dict[str, Any]:
    """Serialize app metadata for a book without opening its GnuCash data."""
    return {
        "id": book.id,
        "name": book.name,
        "storage_type": book.storage_type,
        "uri_or_path": book.uri_or_path,
        "base_currency": book.base_currency,
        "is_default": book.is_default,
        "is_archived": book.is_archived,
    }


def resolve_viewable_book(book_id: int, user: User, session: Session) -> Book:
    """Resolve a book and require current user view access."""
    book = BookRegistryService(session).get_book(book_id)
    if book is None or book.is_archived:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )
    require_book_view_access(book, user, session)
    return book


def require_book_view_access(book: Book, user: User, session: Session) -> None:
    try:
        BookAccessService(session).assert_can_view(user, book)
    except AccessDenied as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Book access denied",
        ) from exc


def handle_gnucash_error(exc: Exception) -> None:
    """Translate GnuCash service-layer errors to stable HTTP responses."""
    if isinstance(exc, (BookNotFoundError, EntityNotFoundError)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    if isinstance(exc, (BookNotConfiguredError, GnuCashReadError)):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    raise exc


def account_service_for(book: Book) -> GnuCashBookService:
    """Create the read-only GnuCash service for a book.

    Routes must use this adapter instead of importing or calling piecash directly.
    """
    return GnuCashBookService(book)


@router.get("")
async def list_books(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    """List books visible to the current user."""
    books = BookRegistryService(session).list_books_for_user(user)
    return [serialize_book(book) for book in books]


@router.get("/{book_id}")
async def get_book(
    book_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> dict[str, Any]:
    """Return one viewable book by id."""
    book = resolve_viewable_book(book_id, user, session)
    return serialize_book(book)


@router.get("/{book_id}/accounts")
async def list_book_accounts(
    book_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    """List accounts for a viewable book."""
    book = resolve_viewable_book(book_id, user, session)
    try:
        accounts = account_service_for(book).list_accounts()
    except (BookNotFoundError, BookNotConfiguredError, EntityNotFoundError, GnuCashReadError) as exc:
        handle_gnucash_error(exc)
    return [account.model_dump() for account in accounts]


@router.get("/{book_id}/accounts/tree")
async def get_book_account_tree(
    book_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    """Return nested account tree for a viewable book."""
    book = resolve_viewable_book(book_id, user, session)
    try:
        tree = account_service_for(book).get_account_tree()
    except (BookNotFoundError, BookNotConfiguredError, EntityNotFoundError, GnuCashReadError) as exc:
        handle_gnucash_error(exc)
    return [node.model_dump() for node in tree]


@router.get("/{book_id}/accounts/{account_id}")
async def get_book_account(
    book_id: int,
    account_id: str,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> dict[str, Any]:
    """Return one account in a viewable book."""
    book = resolve_viewable_book(book_id, user, session)
    try:
        account = account_service_for(book).get_account(account_id)
    except (BookNotFoundError, BookNotConfiguredError, EntityNotFoundError, GnuCashReadError) as exc:
        handle_gnucash_error(exc)
    return account.model_dump()
