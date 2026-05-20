"""Book-aware books and accounts API router."""

from __future__ import annotations

from pathlib import Path
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

UNSUPPORTED_MVP_MANAGEMENT_ACTIONS = [
    "book_upload",
    "book_delete",
    "default_book_change",
    "registry_edit",
]

SAFE_OPERATOR_NEXT_ACTIONS = {
    "available": [
        "Open a read-only view from this page.",
        "Use GnuCash Desktop for any edits.",
    ],
    "not_configured": [
        "Check the app metadata database and deployment configuration for this book entry.",
        "Do not upload or browse GnuCash files from the web UI; configure storage from the host side.",
    ],
    "missing_file": [
        "Verify the configured book is mounted on the host/container.",
        "Check the app metadata database and deployment volumes without uploading or browsing files from the web UI.",
    ],
    "remote_or_unchecked": [
        "Validate the configured storage from the host before relying on this read-only view.",
        "Use GnuCash Desktop as the authoritative editor.",
    ],
}

STATUS_SEVERITY = {
    "available": "ok",
    "remote_or_unchecked": "warning",
    "missing_file": "action_required",
    "not_configured": "action_required",
}

ACCESS_ROLE_COPY = {
    "owner": {
        "label": "Owner",
        "description": "Can open read-only views and review operator diagnostics for this independent book.",
    },
    "editor": {
        "label": "Editor",
        "description": "Can open read-only views; write-alpha remains disabled by default and separately gated.",
    },
    "viewer": {
        "label": "Viewer",
        "description": "Can open read-only views for this assigned independent book.",
    },
}


def _is_uri(value: str) -> bool:
    return "://" in value


def _storage_diagnostics_for(book: Book) -> dict[str, Any]:
    """Return safe operator diagnostics without exposing the configured path."""
    configured = bool((book.uri_or_path or "").strip())
    storage_type = (book.storage_type or "").lower()

    if not configured:
        return {
            "status": "not_configured",
            "configured": False,
            "checked": True,
            "safe_summary": "No book location is configured in app metadata.",
            "safe_next_actions": SAFE_OPERATOR_NEXT_ACTIONS["not_configured"],
        }

    if storage_type == "sqlite" and not _is_uri(book.uri_or_path):
        exists = Path(book.uri_or_path).exists()
        if exists:
            return {
                "status": "available",
                "configured": True,
                "checked": True,
                "safe_summary": "A configured local SQLite book path is present and exists; the file is not opened by the metadata listing.",
                "safe_next_actions": SAFE_OPERATOR_NEXT_ACTIONS["available"],
            }
        return {
            "status": "missing_file",
            "configured": True,
            "checked": True,
            "safe_summary": "A configured local SQLite book path is present, but the file was not found from this runtime.",
            "safe_next_actions": SAFE_OPERATOR_NEXT_ACTIONS["missing_file"],
        }

    return {
        "status": "remote_or_unchecked",
        "configured": True,
        "checked": False,
        "safe_summary": "This storage type is configured, but listing metadata does not open or validate the GnuCash data source.",
        "safe_next_actions": SAFE_OPERATOR_NEXT_ACTIONS["remote_or_unchecked"],
    }


def _access_role_for(book: Book, user: User | None) -> str | None:
    if user is None:
        return None
    for entry in book.access_entries:
        if entry.user_id == user.id:
            return entry.role
    return None


def _access_copy_for(role: str | None) -> dict[str, str]:
    if role in ACCESS_ROLE_COPY:
        return ACCESS_ROLE_COPY[role]
    return {
        "label": "Unknown access",
        "description": "This book is listed only when the server has already verified access for the signed-in user.",
    }


def serialize_book(book: Book, user: User | None = None) -> dict[str, Any]:
    """Serialize app metadata for a book without opening its GnuCash data."""
    storage_diagnostics = _storage_diagnostics_for(book)
    status_value = storage_diagnostics["status"]
    access_role = _access_role_for(book, user)
    access_copy = _access_copy_for(access_role)
    return {
        "id": book.id,
        "name": book.name,
        "storage_type": book.storage_type,
        "base_currency": book.base_currency,
        "is_default": book.is_default,
        "is_archived": book.is_archived,
        "access_role": access_role,
        "access_role_label": access_copy["label"],
        "access_role_description": access_copy["description"],
        "read_only": True,
        "status": status_value,
        "status_severity": STATUS_SEVERITY.get(status_value, "warning"),
        "access_status": "accessible",
        "can_open_read_only_views": status_value not in {"missing_file", "not_configured"},
        "storage_diagnostics": storage_diagnostics,
        "management_actions": [],
        "operator_guidance": {
            "metadata_source": "app_metadata_db",
            "data_access": "gnucash_not_opened_for_listing",
            "read_only_default": True,
            "private_path_redacted": True,
            "storage_type_label": f"Read-only {book.storage_type} GnuCash book metadata",
            "unsupported_management_actions": UNSUPPORTED_MVP_MANAGEMENT_ACTIONS,
            "message": (
                "This MVP lists configured accessible book metadata only. "
                "Upload, delete, default-book changes, and registry editing are intentionally unavailable."
            ),
        },
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
    """Translate GnuCash service-layer errors to stable, path-safe HTTP responses."""
    if isinstance(exc, EntityNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
    if isinstance(exc, BookNotFoundError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Configured GnuCash book storage is unavailable from this runtime.",
        ) from exc
    if isinstance(exc, BookNotConfiguredError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GnuCash book storage is not configured for this entry.",
        ) from exc
    if isinstance(exc, GnuCashReadError):
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GnuCash book cannot be read safely from this runtime.",
        ) from exc
    raise exc


def account_service_for(book: Book) -> GnuCashBookService:
    """Create the read-only GnuCash service for a book.

    Routes must use this adapter instead of importing or calling piecash directly.
    """
    return GnuCashBookService(book)


def transaction_service_for(book: Book) -> GnuCashBookService:
    """Alias for account_service_for; same service handles transactions."""
    return GnuCashBookService(book)


def scheduled_transaction_service_for(book: Book) -> GnuCashBookService:
    """Alias for account_service_for; same service handles scheduled transaction metadata."""
    return GnuCashBookService(book)


@router.get("")
async def list_books(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    """List books visible to the current user."""
    books = BookRegistryService(session).list_books_for_user(user)
    return [serialize_book(book, user) for book in books]


@router.get("/{book_id}")
async def get_book(
    book_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> dict[str, Any]:
    """Return one viewable book by id."""
    book = resolve_viewable_book(book_id, user, session)
    return serialize_book(book, user)


@router.get("/{book_id}/scheduled-transactions")
async def list_book_scheduled_transactions(
    book_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    """List safe read-only scheduled transaction metadata for a viewable book."""
    book = resolve_viewable_book(book_id, user, session)
    scheduled = []
    try:
        scheduled = scheduled_transaction_service_for(book).list_scheduled_transactions()
    except (BookNotFoundError, BookNotConfiguredError, EntityNotFoundError, GnuCashReadError) as exc:
        handle_gnucash_error(exc)
    return [item.model_dump() for item in scheduled]


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
