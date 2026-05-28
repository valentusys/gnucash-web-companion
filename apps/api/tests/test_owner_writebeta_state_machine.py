"""Owner-writebeta state-machine tests."""
from __future__ import annotations

import pytest

from app.owner_writebeta_state_machine import (
    OwnerWritebetaSession,
    OwnerWritebetaState,
    OwnerWritebetaTransitionError,
)


def test_owner_writebeta_happy_path_requires_reset_before_complete():
    session = OwnerWritebetaSession()
    assert session.writes_blocked is True

    session.transition(OwnerWritebetaState.PREFLIGHT)
    session.transition(OwnerWritebetaState.PREVIEW)
    session.transition(OwnerWritebetaState.CONFIRMATION, operation_ref="op-create-1", backup_ref="backup-1")
    session.transition(OwnerWritebetaState.MUTATING)
    assert session.writes_blocked is False
    session.transition(OwnerWritebetaState.VERIFICATION, audit_ref="audit-1")
    session.transition(OwnerWritebetaState.RESET_REQUIRED, restore_ref="restore-1")
    assert session.writes_blocked is True
    session.transition(OwnerWritebetaState.COMPLETE)
    session.transition(OwnerWritebetaState.DISABLED)

    summary = session.redacted_summary()
    assert summary["state"] == "disabled"
    assert summary["operation_ref"] == "op-create-1"
    assert "amount" not in str(summary).lower()


def test_owner_writebeta_blocks_skipped_preview_and_unarmed_mutation():
    session = OwnerWritebetaSession()
    with pytest.raises(OwnerWritebetaTransitionError):
        session.transition(OwnerWritebetaState.MUTATING)

    session.transition(OwnerWritebetaState.PREFLIGHT)
    session.transition(OwnerWritebetaState.PREVIEW)
    session.transition(OwnerWritebetaState.CONFIRMATION)
    with pytest.raises(OwnerWritebetaTransitionError):
        session.transition(OwnerWritebetaState.MUTATING)


def test_owner_writebeta_failed_hard_stop_blocks_further_writes():
    session = OwnerWritebetaSession()
    session.transition(OwnerWritebetaState.PREFLIGHT)
    session.transition(OwnerWritebetaState.FAILED_HARD_STOP, reason="restore readiness failed")
    assert session.writes_blocked is True
    assert session.redacted_summary()["failed_reason"] == "restore readiness failed"
    with pytest.raises(OwnerWritebetaTransitionError):
        session.transition(OwnerWritebetaState.PREFLIGHT)


def test_owner_writebeta_verification_requires_audit_and_restore_refs():
    session = OwnerWritebetaSession()
    session.transition(OwnerWritebetaState.PREFLIGHT)
    session.transition(OwnerWritebetaState.PREVIEW)
    session.transition(OwnerWritebetaState.CONFIRMATION, operation_ref="op", backup_ref="backup")
    session.transition(OwnerWritebetaState.MUTATING)
    with pytest.raises(OwnerWritebetaTransitionError):
        session.transition(OwnerWritebetaState.VERIFICATION)
    session.transition(OwnerWritebetaState.VERIFICATION, audit_ref="audit")
    with pytest.raises(OwnerWritebetaTransitionError):
        session.transition(OwnerWritebetaState.RESET_REQUIRED)


def test_owner_writebeta_preview_confirm_token_and_match_required():
    from app.owner_writebeta_state_machine import (
        arm_confirmed_preview,
        prepare_preview,
        require_matching_confirmation,
    )

    session = OwnerWritebetaSession()
    session.transition(OwnerWritebetaState.PREFLIGHT)
    prepare_preview(session, "CREATE", {"splits": [{"account_id": "redacted", "amount": "redacted"}]}, count=1)
    assert session.preview_hash and session.preview_hash.startswith("owb-prev-")
    assert "redacted" not in session.preview_hash

    _, raw_token = arm_confirmed_preview(session, preview_hash=session.preview_hash, backup_ref="bkp-safe-ref")
    require_matching_confirmation(session, preview_hash=session.preview_hash, raw_token=raw_token)
    with pytest.raises(OwnerWritebetaTransitionError):
        require_matching_confirmation(session, preview_hash=session.preview_hash, raw_token="wrong")
    session.transition(OwnerWritebetaState.MUTATING)


def test_owner_writebeta_post_mutation_checks_hard_stop_on_missing_reset_proof():
    from app.owner_writebeta_state_machine import arm_confirmed_preview, mark_post_mutation_checks, prepare_preview

    session = OwnerWritebetaSession()
    session.transition(OwnerWritebetaState.PREFLIGHT)
    prepare_preview(session, "DELETE", {"transaction_id": "opaque-id"}, count=1)
    arm_confirmed_preview(session, preview_hash=session.preview_hash, backup_ref="bkp-safe-ref")
    session.transition(OwnerWritebetaState.MUTATING)
    mark_post_mutation_checks(
        session,
        audit_ref="audit-safe-ref",
        restore_ref="restore-safe-ref",
        lock_released=True,
        defaults_reset=False,
    )
    assert session.state == OwnerWritebetaState.FAILED_HARD_STOP
    assert session.writes_blocked is True


def test_owner_writebeta_post_mutation_checks_record_reset_proof():
    from app.owner_writebeta_state_machine import arm_confirmed_preview, mark_post_mutation_checks, prepare_preview

    session = OwnerWritebetaSession()
    session.transition(OwnerWritebetaState.PREFLIGHT)
    prepare_preview(session, "PATCH", {"fields": ["description"]}, count=1)
    arm_confirmed_preview(session, preview_hash=session.preview_hash, backup_ref="bkp-safe-ref")
    session.transition(OwnerWritebetaState.MUTATING)
    mark_post_mutation_checks(
        session,
        audit_ref="audit-safe-ref",
        restore_ref="restore-safe-ref",
        lock_released=True,
        defaults_reset=True,
    )
    assert session.state == OwnerWritebetaState.RESET_REQUIRED
    assert session.lock_released is True
    assert session.defaults_reset is True
    assert session.writes_blocked is True
