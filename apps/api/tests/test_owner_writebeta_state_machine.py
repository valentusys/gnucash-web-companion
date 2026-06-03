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


def test_owner_writebeta_redacted_summary_sanitizes_safe_shape_keys_and_values():
    """Prove _safe_shape redacts both user-provided keys and values (RED first)."""
    from app.owner_writebeta_state_machine import _safe_shape

    shape = _safe_shape({
        "secret_account": "Assets:Private Checking",
        "private_amount": "12345.67",
        "RAW PRIVATE DESCRIPTION": "oops",
        "memo": "MEMO",
        "nested": {
            "account_id": "bank-guid",
            "description": "PRIVATE DESC",
            "amount": "999.01",
        },
        "items": [100.00, 200.00, 300.00],
    })

    encoded = str(shape)
    # Values must not leak
    for forbidden in [
        "Assets:Private",
        "12345.67",
        "PRIVATE DESC",
        "PRIVATE DESCRIPTION",
        "MEMO",
        "999.01",
        "100.0",
        "200.0",
        "300.0",
    ]:
        assert forbidden not in encoded, f"Value leak: {forbidden!r} found in shape"

    # User-provided keys carrying private meaning must also not leak
    for forbidden_key in [
        "secret_account",
        "private_amount",
        "account_id",
        "description",
        "amount",
        "memo",
    ]:
        assert forbidden_key not in encoded, f"Key leak: {forbidden_key!r} found in shape"


def test_owner_writebeta_route_status_and_preview_redact_private_payload_values():
    """Prove /status and /preview responses never expose raw payload values."""
    import json
    from fastapi.testclient import TestClient
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy.pool import StaticPool

    from app.config import Settings, get_settings
    from app.database import Base
    from app.main import app
    from app.models import Book, User, UserBookAccess
    from app.routers.auth import get_db
    from app.services.auth import hash_password

    admin_pass = "test" + "password123"
    jwt_key = "test-secret-key-for-unit-tests-" + "32-bytes-minimum"
    test_settings = Settings(
        app_env="test",
        app_database_url="sqlite:///:memory:",
        jwt_secret=jwt_key,
        app_admin_username="admin",
        app_admin_password=admin_pass,
        gnucash_writes_enabled=False,
    )

    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine)

    def override_get_db():
        with factory() as session:
            yield session

    app.dependency_overrides[get_settings] = lambda: test_settings
    app.dependency_overrides[get_db] = override_get_db

    with factory() as session:
        session.add(
            User(
                username="admin",
                display_name="Admin",
                password_hash=hash_password(admin_pass),
                is_admin=True,
            )
        )
        session.commit()

    client = TestClient(app)
    from app.routers.owner_writebeta import _SESSIONS
    _SESSIONS.clear()

    try:
        login = client.post(
            "/auth/login",
            json={"username": "admin", "password": admin_pass},
        )
        headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

        with factory() as session:
            book = Book(
                name="Private Probe Book",
                storage_type="sqlite",
                uri_or_path="/data/books/private-test-book.gnucash.sqlite",
                is_default=True,
            )
            session.add(book)
            session.flush()
            admin = session.query(User).filter(User.username == "admin").one()
            session.add(UserBookAccess(user_id=admin.id, book_id=book.id, role="owner"))
            session.commit()
            book_id = book.id

        # /status must not leak the book filename
        status_resp = client.get(f"/books/{book_id}/owner-writebeta/status", headers=headers)
        assert status_resp.status_code == 200
        status_data = status_resp.json()
        status_summary = json.dumps(status_data["summary"])
        assert "private-test-book" not in status_summary, "Book filename leaked in /status summary"

        # /preflight then /preview with a payload containing private values
        client.post(f"/books/{book_id}/owner-writebeta/preflight", headers=headers)

        private_shape = {
            "secret_account_name": "Assets:Private Savings",
            "RAW PRIVATE DESCRIPTION": "grocery shopping at secret store",
            "amount_split": "12345.67",
            "split_memo": "PRIVATE MEMO",
            "nested": {
                "description": "SECRET DESC",
                "amount": "999.99",
                "account_id": "private-guid",
                "private_key": "PRIVATE KEY MATERIAL",
            },
        }

        preview_resp = client.post(
            f"/books/{book_id}/owner-writebeta/preview",
            headers=headers,
            json={"operation": "CREATE", "payload_shape": private_shape, "count": 2},
        )
        assert preview_resp.status_code == 200
        preview_data = preview_resp.json()
        preview_redacted = json.dumps(preview_data["redacted_summary"])

        # The redacted_summary must not contain any user-provided key names or values
        forbidden_in_summary = [
            "secret_account_name",
            "Assets:Private",
            "RAW PRIVATE DESCRIPTION",
            "PRIVATE DESCRIPTION",
            "amount_split",
            "12345.67",
            "split_memo",
            "PRIVATE MEMO",
            "SECRET DESC",
            "999.99",
            "private-guid",
            "PRIVATE KEY",
            "private-test-book",
            "account_id",
            "private_key",
        ]
        for forbidden in forbidden_in_summary:
            assert forbidden not in preview_redacted, f"Private value leak in redacted_summary: {forbidden!r}"

        # The opaque refs in the summary must be present instead
        assert preview_data["preview_hash"].startswith("owb-prev-")

        # /confirm must refuse path-like evidence refs before they can enter
        # status/audit summaries.
        preview_hash = preview_data["preview_hash"]
        path_ref_confirm = client.post(
            f"/books/{book_id}/owner-writebeta/confirm",
            headers=headers,
            json={
                "preview_hash": preview_hash,
                "backup_ref": "/data/backups/private/secret-backup.gnucash.sqlite",
                "restore_readiness_ref": "rr-provided",
            },
        )
        assert path_ref_confirm.status_code == 409
        assert "opaque reference" in path_ref_confirm.json()["detail"]

        confirm_resp = client.post(
            f"/books/{book_id}/owner-writebeta/confirm",
            headers=headers,
            json={
                "preview_hash": preview_hash,
                "backup_ref": "bkp-opaque-ref",
                "restore_readiness_ref": "rr-provided",
            },
        )
        assert confirm_resp.status_code == 200
        confirm_data = confirm_resp.json()
        assert confirm_data["confirmation_token_ref"].startswith("owb-conf-")

        # /status after confirm: redacted_summary must not contain payload values
        status2 = client.get(f"/books/{book_id}/owner-writebeta/status", headers=headers)
        assert status2.status_code == 200
        status2_data = status2.json()
        status2_summary = json.dumps(status2_data["summary"])
        for forbidden in forbidden_in_summary:
            assert forbidden not in status2_summary, f"Private value leak in /status summary after confirm: {forbidden!r}"

        # failed_reason sanitization: prove arbitrary reason strings are redacted
        from app.routers.owner_writebeta import _SESSIONS as test_sessions
        # Session is in CONFIRMation state; transition directly to FAILED_HARD_STOP
        # with a reason containing sensitive data
        test_sessions[book_id].transition(
            OwnerWritebetaState.FAILED_HARD_STOP,
            reason="postgres:///private/db with secret_password and /data/books/private.gnucash.sqlite",
        )
        status3 = client.get(f"/books/{book_id}/owner-writebeta/status", headers=headers)
        assert status3.status_code == 200
        status3_data = status3.json()
        failed_reason = status3_data["summary"]["failed_reason"]
        # The failed_reason must NOT contain the raw path/secret text
        if failed_reason is not None:
            assert "postgres://" not in failed_reason, "Raw DB URL leaked in failed_reason"
            assert "secret_password" not in failed_reason, "Secret leaked in failed_reason"
            assert "/data/books" not in failed_reason, "File path leaked in failed_reason"
    finally:
        _SESSIONS.clear()
        app.dependency_overrides.clear()
        get_settings.cache_clear()
