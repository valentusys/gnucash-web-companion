"""Fail-closed matrix for the owner-writebeta routed mutation guard.

Issue #36-W1-A: CREATE/PATCH/DELETE routes share
require_owner_writebeta_if_active().  These tests exercise that guard directly
with synthetic in-memory sessions only; no GnuCash book, app DB, backup, export,
private path, account name, memo, description, amount, or raw evidence is used.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException

from app.owner_writebeta_state_machine import (
    OwnerWritebetaSession,
    OwnerWritebetaState,
    arm_confirmed_preview,
    prepare_preview,
)
from app.routers.owner_writebeta import _SESSIONS, require_owner_writebeta_if_active


@pytest.fixture(autouse=True)
def clear_owner_writebeta_sessions():
    _SESSIONS.clear()
    yield
    _SESSIONS.clear()


def _armed_session(*, restore_readiness_ref: str | None = "rr-route-guard") -> tuple[int, str, str]:
    """Create a synthetic CONFIRMATION session and return book/hash/token."""
    book_id = 36_007
    session = OwnerWritebetaSession()
    session.transition(OwnerWritebetaState.PREFLIGHT)
    prepare_preview(session, "CREATE", {"field": "synthetic"}, count=1)
    preview_hash = session.preview_hash or ""
    _, raw_token = arm_confirmed_preview(
        session,
        preview_hash=preview_hash,
        backup_ref="bkp-route-guard",
        restore_readiness_ref=restore_readiness_ref,
    )
    _SESSIONS[book_id] = session
    return book_id, preview_hash, raw_token


def test_owner_writebeta_guard_allows_inactive_or_disabled_session_without_arming():
    """No active owner-writebeta session should not change old default-disabled gates."""
    require_owner_writebeta_if_active(
        book_id=1,
        preview_hash=None,
        confirmation_token=None,
    )

    session = OwnerWritebetaSession()
    _SESSIONS[2] = session
    require_owner_writebeta_if_active(
        book_id=2,
        preview_hash="owb-prev-unused",
        confirmation_token="unused-token",
    )
    assert session.state == OwnerWritebetaState.DISABLED


@pytest.mark.parametrize(
    "state",
    [
        OwnerWritebetaState.PREFLIGHT,
        OwnerWritebetaState.PREVIEW,
        OwnerWritebetaState.MUTATING,
        OwnerWritebetaState.VERIFICATION,
        OwnerWritebetaState.RESET_REQUIRED,
        OwnerWritebetaState.COMPLETE,
        OwnerWritebetaState.FAILED_HARD_STOP,
    ],
)
def test_owner_writebeta_guard_blocks_every_non_confirmation_active_state(state):
    """Any active state except CONFIRMATION must fail closed before mutation."""
    book_id = 36_100 + list(OwnerWritebetaState).index(state)
    session = OwnerWritebetaSession()
    session.state = state
    _SESSIONS[book_id] = session

    with pytest.raises(HTTPException) as excinfo:
        require_owner_writebeta_if_active(
            book_id=book_id,
            preview_hash="owb-prev-synthetic",
            confirmation_token="synthetic-token",
        )

    assert excinfo.value.status_code == 403
    assert "not armed" in str(excinfo.value.detail)
    assert session.state == state


def test_owner_writebeta_guard_blocks_confirmation_without_both_header_values():
    book_id, preview_hash, raw_token = _armed_session()

    missing_cases = [
        (None, raw_token),
        (preview_hash, None),
        (None, None),
        ("", raw_token),
        (preview_hash, ""),
    ]
    for candidate_hash, candidate_token in missing_cases:
        with pytest.raises(HTTPException) as excinfo:
            require_owner_writebeta_if_active(
                book_id=book_id,
                preview_hash=candidate_hash,
                confirmation_token=candidate_token,
            )
        assert excinfo.value.status_code == 403
        assert "matching preview hash and confirmation token" in str(excinfo.value.detail)
        assert _SESSIONS[book_id].state == OwnerWritebetaState.CONFIRMATION


def test_owner_writebeta_guard_blocks_mismatched_preview_hash_and_token():
    book_id, preview_hash, raw_token = _armed_session()

    mismatch_cases = [
        ("owb-prev-wrong", raw_token, "does not match armed preview"),
        (preview_hash, "wrong-token", "confirmation token mismatch"),
    ]
    for candidate_hash, candidate_token, expected_detail in mismatch_cases:
        with pytest.raises(HTTPException) as excinfo:
            require_owner_writebeta_if_active(
                book_id=book_id,
                preview_hash=candidate_hash,
                confirmation_token=candidate_token,
            )
        assert excinfo.value.status_code == 403
        assert expected_detail in str(excinfo.value.detail)
        assert _SESSIONS[book_id].state == OwnerWritebetaState.CONFIRMATION


def test_owner_writebeta_guard_blocks_expired_confirmation_without_mutating():
    book_id, preview_hash, raw_token = _armed_session()
    _SESSIONS[book_id].expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)

    with pytest.raises(HTTPException) as excinfo:
        require_owner_writebeta_if_active(
            book_id=book_id,
            preview_hash=preview_hash,
            confirmation_token=raw_token,
        )

    assert excinfo.value.status_code == 403
    assert "expired" in str(excinfo.value.detail)
    assert _SESSIONS[book_id].state == OwnerWritebetaState.CONFIRMATION


def test_owner_writebeta_guard_blocks_missing_restore_readiness_ref_without_mutating():
    book_id, preview_hash, raw_token = _armed_session(restore_readiness_ref=None)

    with pytest.raises(HTTPException) as excinfo:
        require_owner_writebeta_if_active(
            book_id=book_id,
            preview_hash=preview_hash,
            confirmation_token=raw_token,
        )

    assert excinfo.value.status_code == 403
    assert "restore_readiness_ref" in str(excinfo.value.detail)
    assert _SESSIONS[book_id].state == OwnerWritebetaState.CONFIRMATION


def test_owner_writebeta_guard_accepts_matching_unexpired_confirmation_once():
    book_id, preview_hash, raw_token = _armed_session()

    require_owner_writebeta_if_active(
        book_id=book_id,
        preview_hash=preview_hash,
        confirmation_token=raw_token,
    )

    assert _SESSIONS[book_id].state == OwnerWritebetaState.MUTATING
    assert _SESSIONS[book_id].writes_blocked is False

    with pytest.raises(HTTPException) as excinfo:
        require_owner_writebeta_if_active(
            book_id=book_id,
            preview_hash=preview_hash,
            confirmation_token=raw_token,
        )
    assert excinfo.value.status_code == 403
    assert "not armed" in str(excinfo.value.detail)
