"""MVP scheduled transaction aliases that resolve the default book."""

from __future__ import annotations

from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models import User
from app.routers.accounts import resolve_default_viewable_book
from app.routers.auth import get_current_user, get_db
from app.routers.books import handle_gnucash_error, scheduled_transaction_service_for
from app.services.gnucash_exceptions import (
    BookNotConfiguredError,
    BookNotFoundError,
    EntityNotFoundError,
    GnuCashReadError,
    ScheduledRecurrenceError,
)

router = APIRouter(tags=["scheduled-transactions"])


@router.get("/scheduled-transactions")
async def list_default_book_scheduled_transactions(
    as_of_date: date | None = None,
    user: User = Depends(get_current_user),
    session: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    """List safe read-only scheduled transaction metadata for the default book."""
    book = resolve_default_viewable_book(user, session)
    scheduled = []
    try:
        scheduled = scheduled_transaction_service_for(book).list_scheduled_transactions(as_of_date=as_of_date)
    except ScheduledRecurrenceError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=exc.detail()) from exc
    except (BookNotFoundError, BookNotConfiguredError, EntityNotFoundError, GnuCashReadError) as exc:
        handle_gnucash_error(exc)
    return [item.model_dump() for item in scheduled]
