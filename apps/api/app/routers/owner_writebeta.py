"""Routed owner-writebeta state-machine API.

The route family is intentionally app-metadata/redacted only. It exposes state,
blocked/pass reasons, preview refs, confirmation refs, and verification refs; it
must not expose raw book paths, account names, descriptions, memos, amounts, or
backup paths.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.config import Settings, get_settings
from app.models import Book, User
from app.owner_writebeta_state_machine import (
    OwnerWritebetaSession,
    OwnerWritebetaState,
    OwnerWritebetaTransitionError,
    arm_confirmed_preview,
    mark_post_mutation_checks,
    prepare_preview,
    require_matching_confirmation,
)
from app.routers.auth import get_current_user, get_db
from app.routers.books import resolve_viewable_book
from app.services.book_access import AccessDenied, BookAccessService

router = APIRouter(prefix="/books/{book_id}/owner-writebeta", tags=["owner-writebeta"])

_SESSIONS: dict[int, OwnerWritebetaSession] = {}


class OwnerWritebetaStatusDTO(BaseModel):
    book_id: int
    state: str
    writes_blocked: bool
    blocked_reasons: list[str]
    pass_reasons: list[str]
    summary: dict[str, Any]
    warnings: list[str]


class OwnerWritebetaPreviewRequestDTO(BaseModel):
    operation: Literal["CREATE", "PATCH", "DELETE"]
    payload_shape: dict[str, Any] = Field(default_factory=dict)
    count: int = Field(1, ge=1, le=4)
    target_is_write_alpha_owned: bool = False
    metadata_only_patch: bool = True


class OwnerWritebetaPreviewResponseDTO(BaseModel):
    book_id: int
    preview_hash: str
    state: str
    redacted_summary: dict[str, Any]
    limitations: list[str]


class OwnerWritebetaConfirmRequestDTO(BaseModel):
    preview_hash: str
    backup_ref: str = Field(min_length=1, max_length=80)
    restore_readiness_ref: str | None = Field(None, min_length=1, max_length=80)
    ttl_seconds: int = Field(600, ge=1, le=3600)


class OwnerWritebetaConfirmResponseDTO(BaseModel):
    book_id: int
    confirmation_token: str
    confirmation_token_ref: str | None
    state: str
    preview_hash: str
    expires: str | None


class OwnerWritebetaVerifyRequestDTO(BaseModel):
    audit_ref: str = Field(min_length=1, max_length=80)
    restore_ref: str = Field(min_length=1, max_length=80)
    lock_released: bool
    defaults_reset: bool


def _session_for(book_id: int) -> OwnerWritebetaSession:
    return _SESSIONS.setdefault(book_id, OwnerWritebetaSession())


def _resolve_editable_book(book_id: int, user: User, db: Session) -> Book:
    book = resolve_viewable_book(book_id, user, db)
    try:
        BookAccessService(db).assert_can_edit(user, book)
    except AccessDenied as exc:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Book edit access denied",
        ) from exc
    return book


def require_owner_writebeta_if_active(
    *,
    book_id: int,
    preview_hash: str | None,
    confirmation_token: str | None,
) -> None:
    """Fail closed for mutation when an owner-writebeta session is armed."""
    session_state = _SESSIONS.get(book_id)
    if session_state is None or session_state.state == OwnerWritebetaState.DISABLED:
        return
    if session_state.state != OwnerWritebetaState.CONFIRMATION:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner-writebeta session is not armed for mutation.",
        )
    if not preview_hash or not confirmation_token:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Owner-writebeta mutation requires matching preview hash and confirmation token.",
        )
    try:
        require_matching_confirmation(session_state, preview_hash=preview_hash, raw_token=confirmation_token)
        # The restore-readiness evidence must already be stored by /confirm.
        # If it is absent, the state machine transition below fails closed.
        session_state.transition(OwnerWritebetaState.MUTATING)
    except OwnerWritebetaTransitionError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


def _status(book_id: int, session_state: OwnerWritebetaSession, settings: Settings) -> OwnerWritebetaStatusDTO:
    blocked: list[str] = []
    passed: list[str] = []
    if not settings.gnucash_writes_enabled:
        blocked.append("writes_disabled_default")
    else:
        passed.append("writes_explicitly_enabled_runtime")
    if settings.app_env.lower() != "test":
        blocked.append("app_env_not_test")
    else:
        passed.append("app_env_test_gate")
    # State-machine blocked reasons: explicit operator visibility for each
    # blocked state. These are additive with env/defaults blocking above.
    if session_state.state == OwnerWritebetaState.FAILED_HARD_STOP:
        blocked.append(f"state_{session_state.state.value}")
    if session_state.state == OwnerWritebetaState.RESET_REQUIRED:
        blocked.append(f"state_{session_state.state.value}")
    if session_state.state == OwnerWritebetaState.CONFIRMATION:
        now = datetime.now(timezone.utc)
        if session_state.expires_at is not None and now > session_state.expires_at:
            blocked.append("confirmation_expired")
        else:
            passed.append("preview_confirmed_armed")
        if not session_state.restore_readiness_ref:
            blocked.append("restore_not_ready")
    return OwnerWritebetaStatusDTO(
        book_id=book_id,
        state=session_state.state.value,
        writes_blocked=session_state.writes_blocked or bool(blocked),
        blocked_reasons=blocked,
        pass_reasons=passed,
        summary=session_state.redacted_summary(),
        warnings=[
            "Owner-only experimental writebeta state visibility for copied/restorable test books only.",
            "Real working/private/original/only-copy books remain blocked.",
            "Values are redacted; raw paths, account names, memos, descriptions, and amounts are not exposed.",
        ],
    )


@router.get("/status", response_model=OwnerWritebetaStatusDTO)
async def owner_writebeta_status(
    book_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> OwnerWritebetaStatusDTO:
    _resolve_editable_book(book_id, user, db)
    return _status(book_id, _session_for(book_id), settings)


@router.post("/preflight", response_model=OwnerWritebetaStatusDTO)
async def owner_writebeta_preflight(
    book_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> OwnerWritebetaStatusDTO:
    _resolve_editable_book(book_id, user, db)
    session_state = _session_for(book_id)
    if session_state.state == OwnerWritebetaState.DISABLED:
        session_state.transition(OwnerWritebetaState.PREFLIGHT)
    elif session_state.state not in {OwnerWritebetaState.PREFLIGHT, OwnerWritebetaState.PREVIEW, OwnerWritebetaState.CONFIRMATION}:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Owner-writebeta preflight is blocked by current state.")
    return _status(book_id, session_state, settings)


@router.post("/preview", response_model=OwnerWritebetaPreviewResponseDTO)
async def owner_writebeta_preview(
    book_id: int,
    request: OwnerWritebetaPreviewRequestDTO,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OwnerWritebetaPreviewResponseDTO:
    _resolve_editable_book(book_id, user, db)
    if request.operation in {"PATCH", "DELETE"} and not request.target_is_write_alpha_owned:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="PATCH/DELETE preview requires a write-alpha/state-machine-created disposable transaction target.")
    if request.operation == "PATCH" and not request.metadata_only_patch:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="PATCH preview is metadata-only in this owner-writebeta slice.")
    session_state = _session_for(book_id)
    if session_state.state == OwnerWritebetaState.DISABLED:
        session_state.transition(OwnerWritebetaState.PREFLIGHT)
    if session_state.state != OwnerWritebetaState.PREFLIGHT:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Owner-writebeta preview requires preflight state.")
    try:
        prepare_preview(session_state, request.operation, request.payload_shape, count=request.count)
    except OwnerWritebetaTransitionError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc
    return OwnerWritebetaPreviewResponseDTO(
        book_id=book_id,
        preview_hash=session_state.preview_hash or "",
        state=session_state.state.value,
        redacted_summary=session_state.redacted_summary(),
        limitations=[
            "Preview is a redacted operation-shape hash, not committed raw payload evidence.",
            "Mutation still requires explicit confirmation, old write gates, backup, audit, read-back, restore verification, lock release, and disabled reset.",
        ],
    )


@router.post("/confirm", response_model=OwnerWritebetaConfirmResponseDTO)
async def owner_writebeta_confirm(
    book_id: int,
    request: OwnerWritebetaConfirmRequestDTO,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> OwnerWritebetaConfirmResponseDTO:
    _resolve_editable_book(book_id, user, db)
    session_state = _session_for(book_id)
    try:
        _, raw_token = arm_confirmed_preview(
            session_state,
            preview_hash=request.preview_hash,
            backup_ref=request.backup_ref,
            restore_readiness_ref=request.restore_readiness_ref,
            ttl_seconds=request.ttl_seconds,
        )
    except OwnerWritebetaTransitionError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return OwnerWritebetaConfirmResponseDTO(
        book_id=book_id,
        confirmation_token=raw_token,
        confirmation_token_ref=session_state.confirmation_token_ref,
        state=session_state.state.value,
        preview_hash=request.preview_hash,
        expires=session_state.expires_at.isoformat() if session_state.expires_at else None,
    )


@router.post("/verify-reset", response_model=OwnerWritebetaStatusDTO)
async def owner_writebeta_verify_reset(
    book_id: int,
    request: OwnerWritebetaVerifyRequestDTO,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> OwnerWritebetaStatusDTO:
    _resolve_editable_book(book_id, user, db)
    session_state = _session_for(book_id)
    if session_state.state != OwnerWritebetaState.MUTATING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Owner-writebeta verify-reset requires a mutating session with routed mutation evidence.",
        )
    try:
        mark_post_mutation_checks(
            session_state,
            audit_ref=request.audit_ref,
            restore_ref=request.restore_ref,
            lock_released=request.lock_released,
            defaults_reset=request.defaults_reset,
        )
    except OwnerWritebetaTransitionError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc)) from exc
    return _status(book_id, session_state, settings)


@router.post("/reset-disabled", response_model=OwnerWritebetaStatusDTO)
async def owner_writebeta_reset_disabled(
    book_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> OwnerWritebetaStatusDTO:
    _resolve_editable_book(book_id, user, db)
    session_state = _session_for(book_id)
    if session_state.state == OwnerWritebetaState.RESET_REQUIRED:
        session_state.transition(OwnerWritebetaState.COMPLETE)
        session_state.transition(OwnerWritebetaState.DISABLED)
    elif session_state.state != OwnerWritebetaState.DISABLED:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Reset-disabled requires reset_required state or already disabled state.")
    return _status(book_id, session_state, settings)
