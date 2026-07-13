"""Book-aware books and accounts API router."""

from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from app.models import Book, User, UserBookAccess, WriteAlphaTransactionOwnership
from app.routers.auth import get_current_user, get_db
from app.services.book_access import AccessDenied, BookAccessService
from app.services.book_registry import BookRegistryService
from app.services.gnucash_book import GnuCashBookService
from app.services.account_explorer import (
    AccountExplorerError,
    build_account_activity_query,
    build_account_explorer_query,
    normalize_account_guid,
)
from app.services.gnucash_exceptions import (
    BookNotConfiguredError,
    BookNotFoundError,
    EntityNotFoundError,
    GnuCashReadError,
)

router = APIRouter(prefix="/books", tags=["books"])

UNSUPPORTED_MVP_MANAGEMENT_ACTIONS = [
    "book_upload",
    "book_file_delete",
    "book_file_edit",
]

ADMIN_SAFE_MANAGEMENT_ACTIONS = [
    "set_default",
    "remove_from_registry",
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
    "invalid_gnucash_schema": [
        "Verify the configured file is a copied/test GnuCash SQLite book mounted from the host.",
        "Do not upload or browse private books from the web UI; fix the host-side metadata or mount.",
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
    "invalid_gnucash_schema": "action_required",
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


class BookRegistrationRequest(BaseModel):
    """Admin-only app metadata registration request.

    This registers an already-mounted local copied/test book in the app metadata
    database. It never uploads, copies, opens, or mutates GnuCash accounting data.
    """

    name: str = Field(min_length=1, max_length=256)
    storage_type: str = "sqlite"
    uri_or_path: str = Field(min_length=1, max_length=1024)
    base_currency: str | None = Field(default=None, max_length=16)
    make_default: bool = False

    @field_validator("name", "storage_type", "uri_or_path", mode="before")
    @classmethod
    def _strip_required_text(cls, value: str) -> str:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("base_currency", mode="before")
    @classmethod
    def _normalize_base_currency(cls, value: str | None) -> str | None:
        if value is None:
            return None
        stripped = value.strip().upper()
        return stripped or None


def require_admin_user(user: User) -> None:
    if not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges are required for book registry management.",
        )


def validate_safe_registration_target(body: BookRegistrationRequest) -> None:
    """Validate registration metadata without exposing private paths in errors."""
    storage_type = body.storage_type.lower()
    if storage_type != "sqlite":
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Only local sqlite book metadata registration is supported by this admin UI.",
        )
    if _is_uri(body.uri_or_path):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="URI data sources are not supported by this metadata registration form.",
        )
    path = Path(body.uri_or_path)
    if not path.exists():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Configured local SQLite book path does not exist from this runtime.",
        )
    if not path.is_file():
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Configured local SQLite book path is not a file.",
        )
    shape_error = _sqlite_gnucash_shape_error(path)
    if shape_error is not None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=shape_error,
        )


def _sqlite_gnucash_shape_error(path: Path) -> str | None:
    """Return a path-redacted schema problem, or None when the target looks usable."""
    required_tables = {"versions", "books", "accounts", "transactions", "splits", "commodities"}
    try:
        with sqlite3.connect(f"file:{path}?mode=ro", uri=True) as conn:
            rows = conn.execute(
                "select name from sqlite_master where type = 'table'"
            ).fetchall()
    except sqlite3.DatabaseError:
        return "Configured local book path is not a readable SQLite GnuCash book."

    table_names = {str(row[0]) for row in rows}
    if not required_tables.issubset(table_names):
        return "Configured local SQLite file does not look like a GnuCash book."
    return None


def _local_sqlite_gnucash_shape_is_valid(path: Path) -> bool:
    """Check read-only schema markers for diagnostics without exposing path details."""
    return _sqlite_gnucash_shape_error(path) is None


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
        path = Path(book.uri_or_path)
        exists = path.exists()
        should_validate_shape = path.name.endswith((".sqlite", ".sqlite3", ".gnucash.sqlite"))
        if exists and (not should_validate_shape or _local_sqlite_gnucash_shape_is_valid(path)):
            return {
                "status": "available",
                "configured": True,
                "checked": True,
                "safe_summary": "A configured local SQLite book path is present and exists; the file is not opened by the metadata listing.",
                "safe_next_actions": SAFE_OPERATOR_NEXT_ACTIONS["available"],
            }
        if exists:
            return {
                "status": "invalid_gnucash_schema",
                "configured": True,
                "checked": True,
                "safe_summary": "A configured local SQLite book path is present, but it does not look like a readable GnuCash SQLite book.",
                "safe_next_actions": SAFE_OPERATOR_NEXT_ACTIONS["invalid_gnucash_schema"],
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
        "can_open_read_only_views": status_value not in {
            "missing_file",
            "not_configured",
            "invalid_gnucash_schema",
        },
        "storage_diagnostics": storage_diagnostics,
        "management_actions": ADMIN_SAFE_MANAGEMENT_ACTIONS if user and user.is_admin else [],
        "operator_guidance": {
            "metadata_source": "app_metadata_db",
            "data_access": "gnucash_not_opened_for_listing",
            "read_only_default": True,
            "private_path_redacted": True,
            "storage_type_label": f"Read-only {book.storage_type} GnuCash book metadata",
            "unsupported_management_actions": UNSUPPORTED_MVP_MANAGEMENT_ACTIONS,
            "message": (
                "This MVP lists configured accessible book metadata only. "
                "Upload, file delete, accounting-data edits, and direct file browsing are intentionally unavailable. "
                "Admin registry actions are metadata-only."
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


def require_book_storage_available_for_readonly(book: Book) -> None:
    """Reject read-only data routes for unavailable local book storage before opening GnuCash."""
    status_value = _storage_diagnostics_for(book)["status"]
    if status_value == "missing_file":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Configured GnuCash book storage is unavailable from this runtime.",
        )
    if status_value == "not_configured":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="GnuCash book storage is not configured for this entry.",
        )
    if status_value == "invalid_gnucash_schema":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Configured GnuCash book storage is not a readable SQLite GnuCash book.",
        )


def resolve_readonly_data_book(book_id: int, user: User, session: Session) -> Book:
    """Resolve a viewable book and require it to be openable for read-only data routes."""
    book = resolve_viewable_book(book_id, user, session)
    require_book_storage_available_for_readonly(book)
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


def _write_alpha_owned_transaction_ids(
    session: Session,
    book_id: int,
    transaction_ids: list[str],
) -> set[str]:
    """Return app-metadata ownership hints for read-only account activity rows."""
    candidate_ids = [transaction_id for transaction_id in transaction_ids if transaction_id]
    if not candidate_ids:
        return set()
    rows = (
        session.query(WriteAlphaTransactionOwnership.transaction_id)
        .filter(
            WriteAlphaTransactionOwnership.book_id == book_id,
            WriteAlphaTransactionOwnership.transaction_id.in_(candidate_ids),
            WriteAlphaTransactionOwnership.created_by_write_alpha == True,  # noqa: E712
        )
        .all()
    )
    return {str(row[0]) for row in rows}


def _serialize_account_activity(result: Any, *, session: Session, book_id: int) -> dict[str, Any]:
    """Attach write-alpha ownership hints without invoking any write path."""
    payload = result.model_dump()
    owned_ids = _write_alpha_owned_transaction_ids(
        session,
        book_id,
        [str(item.get("id", "")) for item in payload.get("recent_transactions", [])],
    )
    for item in payload.get("recent_transactions", []):
        item["is_write_alpha_owned"] = item.get("id") in owned_ids
    return payload


@router.get("")
async def list_books(
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    """List books visible to the current user."""
    books = BookRegistryService(session).list_books_for_user(user)
    return [serialize_book(book, user) for book in books]


@router.post("", status_code=status.HTTP_201_CREATED)
async def register_book(
    body: BookRegistrationRequest,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> dict[str, Any]:
    """Register an already-mounted local SQLite book in app metadata only."""
    require_admin_user(user)
    validate_safe_registration_target(body)

    if body.make_default:
        session.query(Book).update({Book.is_default: False})

    book = Book(
        name=body.name,
        storage_type=body.storage_type.lower(),
        uri_or_path=body.uri_or_path,
        base_currency=body.base_currency,
        is_default=body.make_default,
        is_archived=False,
    )
    session.add(book)
    session.flush()
    session.add(UserBookAccess(user_id=user.id, book_id=book.id, role="owner"))
    session.commit()
    session.refresh(book)
    return serialize_book(book, user)


@router.post("/{book_id}/default")
async def set_default_book(
    book_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> dict[str, Any]:
    """Set an existing app metadata book as default without opening GnuCash data."""
    require_admin_user(user)
    book = BookRegistryService(session).get_book(book_id)
    if book is None or book.is_archived:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )

    session.query(Book).update({Book.is_default: False})
    book.is_default = True
    session.commit()
    session.refresh(book)
    return serialize_book(book, user)


@router.delete("/{book_id}")
async def remove_book_from_registry(
    book_id: int,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> dict[str, Any]:
    """Archive a book metadata entry; never delete the underlying GnuCash file."""
    require_admin_user(user)
    book = BookRegistryService(session).get_book(book_id)
    if book is None or book.is_archived:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )

    book.is_archived = True
    if book.is_default:
        book.is_default = False
    session.commit()
    return {
        "id": book_id,
        "removed_from_registry": True,
        "underlying_file_deleted": False,
    }


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
    """List safe read-only scheduled transaction metadata for an openable book."""
    book = resolve_readonly_data_book(book_id, user, session)
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
    """List accounts for an openable book."""
    book = resolve_readonly_data_book(book_id, user, session)
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
    """Return nested account tree for an openable book."""
    book = resolve_readonly_data_book(book_id, user, session)
    try:
        tree = account_service_for(book).get_account_tree()
    except (BookNotFoundError, BookNotConfiguredError, EntityNotFoundError, GnuCashReadError) as exc:
        handle_gnucash_error(exc)
    return [node.model_dump() for node in tree]


@router.get("/{book_id}/accounts/explorer")
async def explore_book_accounts(
    book_id: int,
    request: Request,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> dict[str, Any]:
    """Return bounded flat preorder account hierarchy for an openable book."""
    book = resolve_readonly_data_book(book_id, user, session)
    try:
        explorer_query = build_account_explorer_query(
            mode=request.query_params.get("mode"),
            query=request.query_params.get("query"),
            types=request.query_params.getlist("type"),
            hidden=request.query_params.get("hidden"),
            placeholder=request.query_params.get("placeholder"),
        )
        result = account_service_for(book).explore_accounts(explorer_query, book_id=book.id)
    except AccountExplorerError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail()) from exc
    except (BookNotFoundError, BookNotConfiguredError, EntityNotFoundError, GnuCashReadError) as exc:
        handle_gnucash_error(exc)
        raise
    return result.model_dump()


@router.get("/{book_id}/accounts/{account_id}/overview")
async def get_book_account_overview(
    book_id: int,
    account_id: str,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> dict[str, Any]:
    """Return a bounded read-only overview for one account in an openable book."""
    book = resolve_readonly_data_book(book_id, user, session)
    try:
        normalized_account_id = normalize_account_guid(account_id)
        result = account_service_for(book).get_account_overview(normalized_account_id, book_id=book.id)
    except AccountExplorerError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail()) from exc
    except (BookNotFoundError, BookNotConfiguredError, EntityNotFoundError, GnuCashReadError) as exc:
        handle_gnucash_error(exc)
        raise
    return result.model_dump()


@router.get("/{book_id}/accounts/{account_id}/activity")
async def get_book_account_activity(
    book_id: int,
    account_id: str,
    date_from: str | None = None,
    date_to: str | None = None,
    limit: str | None = None,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> dict[str, Any]:
    """Return bounded direct-account activity for one account in an openable book."""
    book = resolve_readonly_data_book(book_id, user, session)
    try:
        normalized_account_id = normalize_account_guid(account_id)
        activity_query = build_account_activity_query(date_from=date_from, date_to=date_to, limit=limit)
        result = account_service_for(book).get_account_activity(
            normalized_account_id,
            activity_query,
            book_id=book.id,
        )
    except AccountExplorerError as exc:
        raise HTTPException(status_code=exc.status_code, detail=exc.detail()) from exc
    except (BookNotFoundError, BookNotConfiguredError, EntityNotFoundError, GnuCashReadError) as exc:
        handle_gnucash_error(exc)
        raise
    return _serialize_account_activity(result, session=session, book_id=book.id)


@router.get("/{book_id}/accounts/{account_id}")
async def get_book_account(
    book_id: int,
    account_id: str,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> dict[str, Any]:
    """Return one account in an openable book."""
    book = resolve_readonly_data_book(book_id, user, session)
    try:
        account = account_service_for(book).get_account(account_id)
    except (BookNotFoundError, BookNotConfiguredError, EntityNotFoundError, GnuCashReadError) as exc:
        handle_gnucash_error(exc)
    return account.model_dump()
