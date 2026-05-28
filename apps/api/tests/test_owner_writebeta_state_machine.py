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
