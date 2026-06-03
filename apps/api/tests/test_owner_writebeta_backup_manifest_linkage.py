"""Owner-writebeta backup/audit/restore manifest-linkage regressions.

Issue #36-W1-B: preserve only opaque operation/backup/audit/restore refs across
successful and failed post-mutation states, and reject path-like evidence refs
before they can enter summaries.  Synthetic state-machine sessions only; no
GnuCash book, app DB, backup file, private path, account name, memo,
description, amount, or raw evidence is used.
"""
from __future__ import annotations

import json

import pytest

from app.owner_writebeta_state_machine import (
    OwnerWritebetaSession,
    OwnerWritebetaState,
    OwnerWritebetaTransitionError,
    arm_confirmed_preview,
    mark_post_mutation_checks,
    prepare_preview,
)


def _confirmed_session(operation: str = "CREATE") -> OwnerWritebetaSession:
    session = OwnerWritebetaSession()
    session.transition(OwnerWritebetaState.PREFLIGHT)
    prepare_preview(
        session,
        operation,
        {"private_account": "value", "splits": [{"amount": "synthetic"}]},
        count=1,
    )
    assert session.preview_hash is not None
    arm_confirmed_preview(
        session,
        preview_hash=session.preview_hash,
        backup_ref="bkp-manifest-link",
        restore_readiness_ref="rr-manifest-link",
    )
    session.transition(OwnerWritebetaState.MUTATING)
    return session


def test_successful_post_mutation_summary_links_all_opaque_manifest_refs():
    session = _confirmed_session()

    mark_post_mutation_checks(
        session,
        audit_ref="audit-manifest-link",
        restore_ref="restore-manifest-link",
        lock_released=True,
        defaults_reset=True,
    )

    assert session.state == OwnerWritebetaState.RESET_REQUIRED
    summary = session.redacted_summary()
    assert summary["operation_ref"] == session.operation_ref
    assert summary["backup_ref"] == "bkp-manifest-link"
    assert summary["audit_ref"] == "audit-manifest-link"
    assert summary["restore_ref"] == "restore-manifest-link"
    assert summary["lock_released"] is True
    assert summary["defaults_reset"] is True
    assert summary["preview_hash"] is None
    assert summary["confirmation_token_ref"] is None
    assert summary["restore_readiness_ref"] is None

    serialized = json.dumps(summary, sort_keys=True)
    for forbidden in [
        "private_account",
        "synthetic",
        "amount",
        "description",
        "memo",
        "/data/",
        ".gnucash",
        "sqlite",
    ]:
        assert forbidden not in serialized


def test_failed_post_mutation_summary_preserves_pre_mutation_manifest_refs_only():
    session = _confirmed_session("PATCH")
    operation_ref = session.operation_ref

    mark_post_mutation_checks(
        session,
        audit_ref="audit-not-recorded-on-failure",
        restore_ref="restore-not-recorded-on-failure",
        lock_released=False,
        defaults_reset=True,
    )

    assert session.state == OwnerWritebetaState.FAILED_HARD_STOP
    assert session.writes_blocked is True
    summary = session.redacted_summary()
    assert summary["operation_ref"] == operation_ref
    assert summary["backup_ref"] == "bkp-manifest-link"
    assert summary["audit_ref"] is None
    assert summary["restore_ref"] is None
    assert summary["preview_hash"] is None
    assert summary["confirmation_token_ref"] is None
    assert summary["restore_readiness_ref"] is None
    assert summary["failed_reason"] == "post-mutation verification incomplete"


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("backup_ref", "backup/path/ref"),
        ("backup_ref", "postgres://backup-ref"),
        ("restore_readiness_ref", "rr with spaces"),
        ("audit_ref", "audit/ref/path"),
        ("restore_ref", "restore\\path"),
    ],
)
def test_manifest_refs_reject_path_url_or_whitespace_values(field, value):
    session = OwnerWritebetaSession()
    session.transition(OwnerWritebetaState.PREFLIGHT)
    prepare_preview(session, "CREATE", {"shape": "synthetic"}, count=1)

    if field == "backup_ref":
        assert session.preview_hash is not None
        with pytest.raises(OwnerWritebetaTransitionError, match="opaque reference"):
            arm_confirmed_preview(
                session,
                preview_hash=session.preview_hash,
                backup_ref=value,
                restore_readiness_ref="rr-ok",
            )
        return
    if field == "restore_readiness_ref":
        assert session.preview_hash is not None
        with pytest.raises(OwnerWritebetaTransitionError, match="opaque reference"):
            arm_confirmed_preview(
                session,
                preview_hash=session.preview_hash,
                backup_ref="bkp-ok",
                restore_readiness_ref=value,
            )
        return

    assert session.preview_hash is not None
    arm_confirmed_preview(
        session,
        preview_hash=session.preview_hash,
        backup_ref="bkp-ok",
        restore_readiness_ref="rr-ok",
    )
    session.transition(OwnerWritebetaState.MUTATING)

    if field == "audit_ref":
        with pytest.raises(OwnerWritebetaTransitionError, match="opaque reference"):
            session.transition(OwnerWritebetaState.VERIFICATION, audit_ref=value)
    else:
        session.transition(OwnerWritebetaState.VERIFICATION, audit_ref="audit-ok")
        with pytest.raises(OwnerWritebetaTransitionError, match="opaque reference"):
            session.transition(OwnerWritebetaState.RESET_REQUIRED, restore_ref=value)
