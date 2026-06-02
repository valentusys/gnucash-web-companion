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
    session.transition(OwnerWritebetaState.MUTATING, restore_readiness_ref="rr-happy-path")
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
    session.transition(OwnerWritebetaState.MUTATING, restore_readiness_ref="rr-verify-test")
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

    _, raw_token = arm_confirmed_preview(session, preview_hash=session.preview_hash, backup_ref="bkp-safe-ref", restore_readiness_ref="rr-token-test")
    require_matching_confirmation(session, preview_hash=session.preview_hash, raw_token=raw_token)
    with pytest.raises(OwnerWritebetaTransitionError):
        require_matching_confirmation(session, preview_hash=session.preview_hash, raw_token="wrong")
    session.transition(OwnerWritebetaState.MUTATING)


def test_owner_writebeta_post_mutation_checks_hard_stop_on_missing_reset_proof():
    from app.owner_writebeta_state_machine import arm_confirmed_preview, mark_post_mutation_checks, prepare_preview

    session = OwnerWritebetaSession()
    session.transition(OwnerWritebetaState.PREFLIGHT)
    prepare_preview(session, "DELETE", {"transaction_id": "opaque-id"}, count=1)
    arm_confirmed_preview(session, preview_hash=session.preview_hash, backup_ref="bkp-safe-ref", restore_readiness_ref="rr-hard-stop-test")
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
    arm_confirmed_preview(session, preview_hash=session.preview_hash, backup_ref="bkp-safe-ref", restore_readiness_ref="rr-reset-proof-test")
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


def test_owner_writebeta_mutation_requires_restore_readiness_ref():
    from app.owner_writebeta_state_machine import arm_confirmed_preview, prepare_preview

    session = OwnerWritebetaSession()
    session.transition(OwnerWritebetaState.PREFLIGHT)
    prepare_preview(session, "CREATE", {"splits": [{"amount": "type"}]}, count=1)
    arm_confirmed_preview(session, preview_hash=session.preview_hash, backup_ref="bkp-safe-ref")
    assert session.state == OwnerWritebetaState.CONFIRMATION
    # No restore_readiness_ref set — must fail closed
    with pytest.raises(OwnerWritebetaTransitionError, match="restore_readiness_ref"):
        session.transition(OwnerWritebetaState.MUTATING)
    assert session.state == OwnerWritebetaState.CONFIRMATION
    # Session is armed in CONFIRMATION but mutation did not proceed
    assert session.restore_readiness_ref is None


def test_owner_writebeta_mutation_succeeds_with_restore_readiness_ref():
    from app.owner_writebeta_state_machine import arm_confirmed_preview, prepare_preview

    session = OwnerWritebetaSession()
    session.transition(OwnerWritebetaState.PREFLIGHT)
    prepare_preview(session, "CREATE", {"splits": [{"amount": "type"}]}, count=1)
    arm_confirmed_preview(session, preview_hash=session.preview_hash, backup_ref="bkp-safe-ref")
    assert session.state == OwnerWritebetaState.CONFIRMATION
    # Now record restore readiness and mutate
    session.transition(
        OwnerWritebetaState.MUTATING,
        restore_readiness_ref="rr-restore-verified-ref",
    )
    assert session.state == OwnerWritebetaState.MUTATING
    assert session.writes_blocked is False
    assert session.restore_readiness_ref == "rr-restore-verified-ref"


def test_owner_writebeta_arm_confirmed_preview_stores_restore_readiness_ref():
    from app.owner_writebeta_state_machine import arm_confirmed_preview, prepare_preview

    session = OwnerWritebetaSession()
    session.transition(OwnerWritebetaState.PREFLIGHT)
    prepare_preview(session, "DELETE", {"transaction_id": "opaque-id"}, count=1)
    result_session, raw_token = arm_confirmed_preview(
        session,
        preview_hash=session.preview_hash,
        backup_ref="bkp-safe-ref",
        restore_readiness_ref="rr-prearm-check-ref",
    )
    assert result_session.state == OwnerWritebetaState.CONFIRMATION
    assert result_session.restore_readiness_ref == "rr-prearm-check-ref"
    # Now mutation can proceed because restore_readiness_ref is present
    result_session.transition(OwnerWritebetaState.MUTATING)
    assert result_session.state == OwnerWritebetaState.MUTATING


def test_owner_writebeta_restore_readiness_ref_is_opaque_and_truncated():
    from app.owner_writebeta_state_machine import arm_confirmed_preview, prepare_preview

    long_ref = "rr-" + "a" * 200
    session = OwnerWritebetaSession()
    session.transition(OwnerWritebetaState.PREFLIGHT)
    prepare_preview(session, "PATCH", {"fields": ["description"]}, count=1)
    arm_confirmed_preview(
        session,
        preview_hash=session.preview_hash,
        backup_ref="bkp",
        restore_readiness_ref=long_ref,
    )
    session.transition(OwnerWritebetaState.MUTATING)
    assert session.restore_readiness_ref is not None
    assert len(session.restore_readiness_ref) <= 80


def test_owner_writebeta_happy_path_with_restore_readiness_gate():
    from app.owner_writebeta_state_machine import arm_confirmed_preview, mark_post_mutation_checks, prepare_preview

    session = OwnerWritebetaSession()
    assert session.writes_blocked is True

    session.transition(OwnerWritebetaState.PREFLIGHT)
    prepare_preview(session, "CREATE", {"splits": [{"account_id": "type", "amount": "type"}]}, count=2)
    arm_confirmed_preview(
        session,
        preview_hash=session.preview_hash,
        backup_ref="bkp-happy-ref",
        restore_readiness_ref="rr-happy-ref",
    )
    assert session.state == OwnerWritebetaState.CONFIRMATION
    # Mutation now succeeds because restore_readiness_ref was provided at confirm time
    session.transition(OwnerWritebetaState.MUTATING)
    assert session.writes_blocked is False

    mark_post_mutation_checks(
        session,
        audit_ref="audit-happy-ref",
        restore_ref="restore-happy-ref",
        lock_released=True,
        defaults_reset=True,
    )
    assert session.state == OwnerWritebetaState.RESET_REQUIRED
    assert session.writes_blocked is True

    summary = session.redacted_summary()
    assert summary["restore_readiness_ref"] == "rr-happy-ref"
    assert summary["state"] == "reset_required"
    # raw evidence must not leak
    assert "amount" not in str(summary).lower()


def test_owner_writebeta_full_reset_enforcement_after_session_completion():
    """Prove the complete writebeta lifecycle resets to default-disabled with arms cleared."""
    from app.owner_writebeta_state_machine import arm_confirmed_preview, mark_post_mutation_checks, prepare_preview

    session = OwnerWritebetaSession()
    assert session.writes_blocked is True
    assert session.state == OwnerWritebetaState.DISABLED

    session.transition(OwnerWritebetaState.PREFLIGHT)
    prepare_preview(session, "CREATE", {"splits": [{"amount": "opaque"}]}, count=1)
    arm_confirmed_preview(
        session,
        preview_hash=session.preview_hash,
        backup_ref="bkp-full-reset-ref",
        restore_readiness_ref="rr-full-reset-ref",
    )
    assert session.preview_hash is not None
    assert session.confirmation_token_ref is not None
    assert session.restore_readiness_ref == "rr-full-reset-ref"

    session.transition(OwnerWritebetaState.MUTATING)
    assert session.writes_blocked is False

    mark_post_mutation_checks(
        session,
        audit_ref="audit-full-reset-ref",
        restore_ref="restore-full-reset-ref",
        lock_released=True,
        defaults_reset=True,
    )
    assert session.state == OwnerWritebetaState.RESET_REQUIRED
    assert session.writes_blocked is True
    assert session.lock_released is True
    assert session.defaults_reset is True

    session.transition(OwnerWritebetaState.COMPLETE)
    session.transition(OwnerWritebetaState.DISABLED)
    assert session.state == OwnerWritebetaState.DISABLED
    assert session.preview_hash is None
    assert session.confirmation_token_ref is None
    assert session.restore_readiness_ref is None
    assert session.writes_blocked is True

    session.transition(OwnerWritebetaState.PREFLIGHT)
    prepare_preview(session, "DELETE", {"id": "opaque"}, count=1)
    arm_confirmed_preview(session, preview_hash=session.preview_hash, backup_ref="bkp-2", restore_readiness_ref="rr-2")
    session.transition(OwnerWritebetaState.MUTATING)
    mark_post_mutation_checks(
        session,
        audit_ref="audit-2",
        restore_ref="restore-2",
        lock_released=True,
        defaults_reset=False,
    )
    assert session.state == OwnerWritebetaState.FAILED_HARD_STOP
    assert session.writes_blocked is True


def test_owner_writebeta_restart_post_hard_stop_requires_new_session():
    """FAILED_HARD_STOP terminal state blocks all further transitions."""
    session = OwnerWritebetaSession()
    session.transition(OwnerWritebetaState.PREFLIGHT)
    session.transition(OwnerWritebetaState.FAILED_HARD_STOP, reason="post-mutation verification incomplete")
    assert session.state == OwnerWritebetaState.FAILED_HARD_STOP
    assert session.writes_blocked is True

    for target in OwnerWritebetaState:
        if target == OwnerWritebetaState.FAILED_HARD_STOP:
            continue
        with pytest.raises(OwnerWritebetaTransitionError):
            session.transition(target)
