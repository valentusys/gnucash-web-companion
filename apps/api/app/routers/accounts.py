"""MVP account aliases that resolve the default book.

These endpoints keep the v0.1 UI simple while book-aware endpoints remain
available for future multi-book routing.
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models import Book, User
from app.routers.auth import get_current_user, get_db
from app.routers.books import (
    account_service_for,
    handle_gnucash_error,
    require_book_view_access,
)
from app.services.book_registry import BookRegistryService
from app.services.gnucash_exceptions import (
    BookNotConfiguredError,
    BookNotFoundError,
    EntityNotFoundError,
    GnuCashReadError,
)

router = APIRouter(tags=["accounts"])


def resolve_default_viewable_book(user: User, session: Session) -> Book:
    """Resolve default book and require current user view access."""
    book = BookRegistryService(session).get_default_book()
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No default book configured",
        )
    require_book_view_access(book, user, session)
    return book


@router.get("/accounts")
async def list_default_book_accounts(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    """List accounts for the default book."""
    book = resolve_default_viewable_book(user, session)
    try:
        accounts = account_service_for(book).list_accounts()
    except (BookNotFoundError, BookNotConfiguredError, EntityNotFoundError, GnuCashReadError) as exc:
        handle_gnucash_error(exc)
    return [account.model_dump() for account in accounts]


@router.get("/accounts/tree")
async def get_default_book_account_tree(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    """Return account tree for the default book."""
    book = resolve_default_viewable_book(user, session)
    try:
        tree = account_service_for(book).get_account_tree()
    except (BookNotFoundError, BookNotConfiguredError, EntityNotFoundError, GnuCashReadError) as exc:
        handle_gnucash_error(exc)
    return [node.model_dump() for node in tree]


@router.get("/accounts/{account_id}")
async def get_default_book_account(
    account_id: str,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> dict[str, Any]:
    """Return one account from the default book."""
    book = resolve_default_viewable_book(user, session)
    try:
        account = account_service_for(book).get_account(account_id)
    except (BookNotFoundError, BookNotConfiguredError, EntityNotFoundError, GnuCashReadError) as exc:
        handle_gnucash_error(exc)
    return account.model_dump()
