"""#36-W2-D synthetic lock contention drill.

The owner-writebeta active session is treated as the synthetic write-session lock
boundary for routed write-alpha mutations. No GnuCash book is opened or mutated.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from fastapi import HTTPException

from app.owner_writebeta_state_machine import (
    OwnerWritebetaSession,
    OwnerWritebetaState,
    arm_confirmed_preview,
    mark_post_mutation_checks,
    prepare_preview,
)
from app.routers.owner_writebeta import _SESSIONS, require_owner_writebeta_if_active


@pytest.fixture(autouse=True)
def clear_owner_writebeta_sessions():
    _SESSIONS.clear()
    yield
    _SESSIONS.clear()


def _armed_session(book_id: int = 36_200, *, ttl_seconds: int = 600) -> tuple[OwnerWritebetaSession, str, str]:
    session = OwnerWritebetaSession()
    session.transition(OwnerWritebetaState.PREFLIGHT)
    prepare_preview(session, "CREATE", {"synthetic_lock_drill": "shape-only"}, count=1)
    preview_hash = session.preview_hash or ""
    _, raw_token = arm_confirmed_preview(
        session,
        preview_hash=preview_hash,
        backup_ref="bkp-lock-drill",
        restore_readiness_ref="rr-lock-drill",
        ttl_seconds=ttl_seconds,
    )
    _SESSIONS[book_id] = session
    return session, preview_hash, raw_token


def test_second_mutation_cannot_enter_while_synthetic_session_is_active():
    session, preview_hash, raw_token = _armed_session()

    require_owner_writebeta_if_active(
        book_id=36_200,
        preview_hash=preview_hash,
        confirmation_token=raw_token,
        operation="CREATE",
        count=1,
    )
    assert session.state == OwnerWritebetaState.MUTATING
    assert session.writes_blocked is False

    with pytest.raises(HTTPException) as excinfo:
        require_owner_writebeta_if_active(
            book_id=36_200,
            preview_hash=preview_hash,
            confirmation_token=raw_token,
            operation="CREATE",
            count=1,
        )
    assert excinfo.value.status_code == 403
    assert "not armed" in str(excinfo.value.detail)
    assert session.state == OwnerWritebetaState.MUTATING


def test_confirmation_cannot_be_reused_after_successful_reset_to_disabled():
    session, preview_hash, raw_token = _armed_session()

    require_owner_writebeta_if_active(
        book_id=36_200,
        preview_hash=preview_hash,
        confirmation_token=raw_token,
        operation="CREATE",
        count=1,
    )
    mark_post_mutation_checks(
        session,
        audit_ref="audit-lock-drill",
        restore_ref="restore-lock-drill",
        lock_released=True,
        defaults_reset=True,
    )
    session.transition(OwnerWritebetaState.COMPLETE)
    session.transition(OwnerWritebetaState.DISABLED)

    assert session.state == OwnerWritebetaState.DISABLED
    assert session.preview_hash is None
    assert session.confirmation_token_ref is None
    assert session.restore_readiness_ref is None
    assert session.operation is None
    assert session.operation_count == 0
    # Stale headers after reset must not fall through as an unarmed write, and
    # must not resurrect the old confirmation or move back to MUTATING.
    with pytest.raises(HTTPException) as excinfo:
        require_owner_writebeta_if_active(
            book_id=36_200,
            preview_hash=preview_hash,
            confirmation_token=raw_token,
            operation="CREATE",
            count=1,
        )
    assert excinfo.value.status_code == 403
    assert "active armed owner-writebeta session" in str(excinfo.value.detail)
    assert session.state == OwnerWritebetaState.DISABLED


def test_expired_confirmation_fails_closed_and_cannot_be_recovered_by_reusing_token():
    session, preview_hash, raw_token = _armed_session(ttl_seconds=1)
    session.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)

    with pytest.raises(HTTPException) as excinfo:
        require_owner_writebeta_if_active(
            book_id=36_200,
            preview_hash=preview_hash,
            confirmation_token=raw_token,
            operation="CREATE",
            count=1,
        )
    assert excinfo.value.status_code == 403
    assert "expired" in str(excinfo.value.detail)
    assert session.state == OwnerWritebetaState.CONFIRMATION

    session.transition(OwnerWritebetaState.FAILED_HARD_STOP, reason="restore readiness failed")
    with pytest.raises(HTTPException) as second:
        require_owner_writebeta_if_active(
            book_id=36_200,
            preview_hash=preview_hash,
            confirmation_token=raw_token,
            operation="CREATE",
            count=1,
        )
    assert second.value.status_code == 403
    assert "not armed" in str(second.value.detail)
    assert session.state == OwnerWritebetaState.FAILED_HARD_STOP


def test_synthetic_lock_hard_stop_blocks_stale_session_recovery_without_new_session():
    session, preview_hash, raw_token = _armed_session()

    require_owner_writebeta_if_active(
        book_id=36_200,
        preview_hash=preview_hash,
        confirmation_token=raw_token,
        operation="CREATE",
        count=1,
    )
    mark_post_mutation_checks(
        session,
        audit_ref="audit-stale-lock",
        restore_ref="restore-stale-lock",
        lock_released=False,
        defaults_reset=True,
    )
    assert session.state == OwnerWritebetaState.FAILED_HARD_STOP
    assert session.writes_blocked is True

    for supplied_hash, supplied_token in [
        (preview_hash, raw_token),
        ("owb-prev-new", "new-token"),
    ]:
        with pytest.raises(HTTPException) as excinfo:
            require_owner_writebeta_if_active(
                book_id=36_200,
                preview_hash=supplied_hash,
                confirmation_token=supplied_token,
                operation="CREATE",
                count=1,
            )
        assert excinfo.value.status_code == 403
        assert "not armed" in str(excinfo.value.detail)
    assert session.state == OwnerWritebetaState.FAILED_HARD_STOP


def test_fresh_synthetic_session_can_proceed_after_old_session_is_default_disabled():
    old_session, old_preview, old_token = _armed_session(book_id=36_201)
    require_owner_writebeta_if_active(
        book_id=36_201,
        preview_hash=old_preview,
        confirmation_token=old_token,
        operation="CREATE",
        count=1,
    )
    mark_post_mutation_checks(
        old_session,
        audit_ref="audit-old-lock",
        restore_ref="restore-old-lock",
        lock_released=True,
        defaults_reset=True,
    )
    old_session.transition(OwnerWritebetaState.COMPLETE)
    old_session.transition(OwnerWritebetaState.DISABLED)

    new_session, new_preview, new_token = _armed_session(book_id=36_201)
    require_owner_writebeta_if_active(
        book_id=36_201,
        preview_hash=new_preview,
        confirmation_token=new_token,
        operation="CREATE",
        count=1,
    )

    assert old_session.state == OwnerWritebetaState.DISABLED
    assert new_session.state == OwnerWritebetaState.MUTATING
    assert new_preview != old_preview or new_session.confirmation_token_ref != old_session.confirmation_token_ref
