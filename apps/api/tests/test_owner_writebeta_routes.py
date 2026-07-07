"""Tests for routed owner-writebeta API state visibility."""
from __future__ import annotations

import pytest
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

TEST_SETTINGS = Settings(
    app_env="test",
    app_database_url="sqlite:///:memory:",
    jwt_secret="test-secret-key-for-unit-tests-32-bytes-minimum",
    app_admin_username="admin",
    app_admin_password="testpassword123",
    gnucash_writes_enabled=False,
)


@pytest.fixture
def session_factory():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)


@pytest.fixture
def client(session_factory):
    def override_get_db():
        with session_factory() as session:
            yield session

    app.dependency_overrides[get_settings] = lambda: TEST_SETTINGS
    app.dependency_overrides[get_db] = override_get_db
    with session_factory() as session:
        session.add(
            User(
                username="admin",
                display_name="Admin",
                password_hash=hash_password("testpassword123"),
                is_admin=True,
            )
        )
        session.commit()
    test_client = TestClient(app)
    yield test_client
    from app.routers.owner_writebeta import _SESSIONS

    _SESSIONS.clear()
    app.dependency_overrides.clear()
    get_settings.cache_clear()


@pytest.fixture
def auth_headers(client):
    response = client.post("/auth/login", json={"username": "admin", "password": "testpassword123"})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def sample_book(session_factory):
    with session_factory() as session:
        book = Book(
            name="Owner Writebeta Test Book",
            storage_type="sqlite",
            uri_or_path="/data/books/test.gnucash.sqlite",
            is_default=True,
        )
        session.add(book)
        session.flush()
        admin = session.query(User).filter(User.username == "admin").one()
        session.add(UserBookAccess(user_id=admin.id, book_id=book.id, role="owner"))
        session.commit()
        return book.id


def test_owner_writebeta_preflight_status_is_redacted_and_default_blocked(client, auth_headers, sample_book):
    response = client.post(f"/books/{sample_book}/owner-writebeta/preflight", headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["state"] == "preflight"
    assert payload["writes_blocked"] is True
    assert "writes_disabled_default" in payload["blocked_reasons"]
    assert "app_env_test_gate" in payload["pass_reasons"]
    assert "test.gnucash.sqlite" not in str(payload)


def test_owner_writebeta_preview_blocks_non_owned_patch(client, auth_headers, sample_book):
    client.post(f"/books/{sample_book}/owner-writebeta/preflight", headers=auth_headers)
    response = client.post(
        f"/books/{sample_book}/owner-writebeta/preview",
        headers=auth_headers,
        json={"operation": "PATCH", "payload_shape": {"description": "string"}, "target_is_write_alpha_owned": False},
    )
    assert response.status_code == 403
    assert "write-alpha/state-machine-created" in response.json()["detail"]


def test_owner_writebeta_preview_and_confirmation_use_opaque_refs(client, auth_headers, sample_book):
    client.post(f"/books/{sample_book}/owner-writebeta/preflight", headers=auth_headers)
    preview = client.post(
        f"/books/{sample_book}/owner-writebeta/preview",
        headers=auth_headers,
        json={"operation": "CREATE", "payload_shape": {"splits": [{"amount": "private"}]}, "count": 2},
    )
    assert preview.status_code == 200
    preview_hash = preview.json()["preview_hash"]
    assert preview_hash.startswith("owb-prev-")
    assert "private" not in str(preview.json())

    confirm = client.post(
        f"/books/{sample_book}/owner-writebeta/confirm",
        headers=auth_headers,
        json={"preview_hash": preview_hash, "backup_ref": "bkp-authorized-ref", "restore_readiness_ref": "rr-routed-test-ref"},
    )
    assert confirm.status_code == 200
    assert confirm.json()["state"] == "confirmation"
    assert confirm.json()["confirmation_token_ref"].startswith("owb-conf-")


def test_owner_writebeta_active_guard_requires_matching_operation_and_count(client, auth_headers, sample_book):
    from fastapi import HTTPException

    from app.routers.owner_writebeta import _SESSIONS, require_owner_writebeta_if_active

    client.post(f"/books/{sample_book}/owner-writebeta/preflight", headers=auth_headers)
    preview = client.post(
        f"/books/{sample_book}/owner-writebeta/preview",
        headers=auth_headers,
        json={
            "operation": "DELETE",
            "payload_shape": {"id": "opaque"},
            "count": 1,
            "target_is_write_alpha_owned": True,
        },
    )
    assert preview.status_code == 200
    preview_hash = preview.json()["preview_hash"]
    confirm = client.post(
        f"/books/{sample_book}/owner-writebeta/confirm",
        headers=auth_headers,
        json={
            "preview_hash": preview_hash,
            "backup_ref": "bkp-delete-ref",
            "restore_readiness_ref": "rr-delete-ref",
        },
    )
    assert confirm.status_code == 200

    with pytest.raises(HTTPException) as exc_info:
        require_owner_writebeta_if_active(
            book_id=sample_book,
            preview_hash=preview_hash,
            confirmation_token=confirm.json()["confirmation_token"],
            operation="CREATE",
            count=1,
        )

    assert exc_info.value.status_code == 403
    assert "does not match armed owner-writebeta operation" in exc_info.value.detail
    assert _SESSIONS[sample_book].state.value == "confirmation"

    with pytest.raises(HTTPException) as count_exc:
        require_owner_writebeta_if_active(
            book_id=sample_book,
            preview_hash=preview_hash,
            confirmation_token=confirm.json()["confirmation_token"],
            operation="DELETE",
            count=2,
        )

    assert count_exc.value.status_code == 403
    assert "does not match armed owner-writebeta operation" in count_exc.value.detail
    assert _SESSIONS[sample_book].state.value == "confirmation"


def test_owner_writebeta_confirm_stores_restore_readiness_ref_when_provided(client, auth_headers, sample_book):
    client.post(f"/books/{sample_book}/owner-writebeta/preflight", headers=auth_headers)
    preview = client.post(
        f"/books/{sample_book}/owner-writebeta/preview",
        headers=auth_headers,
        json={"operation": "CREATE", "payload_shape": {"splits": [{"amount": "opaque"}]}, "count": 1},
    )
    assert preview.status_code == 200
    preview_hash = preview.json()["preview_hash"]

    confirm = client.post(
        f"/books/{sample_book}/owner-writebeta/confirm",
        headers=auth_headers,
        json={"preview_hash": preview_hash, "backup_ref": "bkp-ok", "restore_readiness_ref": "rr-router-provided"},
    )
    assert confirm.status_code == 200
    assert confirm.json()["state"] == "confirmation"

    status = client.get(f"/books/{sample_book}/owner-writebeta/status", headers=auth_headers)
    assert status.status_code == 200
    assert status.json()["summary"]["restore_readiness_ref"] == "rr-router-provided"


def test_owner_writebeta_confirm_accepts_missing_restore_readiness_ref(client, auth_headers, sample_book):
    """Confirm endpoint stores None for restore_readiness_ref when omitted; gate lives at mutation time."""
    client.post(f"/books/{sample_book}/owner-writebeta/preflight", headers=auth_headers)
    preview = client.post(
        f"/books/{sample_book}/owner-writebeta/preview",
        headers=auth_headers,
        json={"operation": "CREATE", "payload_shape": {"tx": "opaque"}, "count": 1},
    )
    assert preview.status_code == 200
    preview_hash = preview.json()["preview_hash"]

    confirm = client.post(
        f"/books/{sample_book}/owner-writebeta/confirm",
        headers=auth_headers,
        json={"preview_hash": preview_hash, "backup_ref": "bkp-no-rr"},
    )
    assert confirm.status_code == 200
    assert confirm.json()["state"] == "confirmation"


def test_owner_writebeta_confirm_rejects_invalid_restore_readiness_ref(client, auth_headers, sample_book):
    client.post(f"/books/{sample_book}/owner-writebeta/preflight", headers=auth_headers)
    preview = client.post(
        f"/books/{sample_book}/owner-writebeta/preview",
        headers=auth_headers,
        json={"operation": "CREATE", "payload_shape": {}, "count": 1},
    )
    assert preview.status_code == 200
    preview_hash = preview.json()["preview_hash"]

    long_ref = "x" * 81
    confirm = client.post(
        f"/books/{sample_book}/owner-writebeta/confirm",
        headers=auth_headers,
        json={"preview_hash": preview_hash, "backup_ref": "bkp", "restore_readiness_ref": long_ref},
    )
    assert confirm.status_code == 422


def test_owner_writebeta_status_remains_default_disabled_without_preflight(client, auth_headers, sample_book):
    response = client.get(f"/books/{sample_book}/owner-writebeta/status", headers=auth_headers)

    assert response.status_code == 200
    payload = response.json()
    assert payload["state"] == "disabled"
    assert payload["writes_blocked"] is True
    assert "writes_disabled_default" in payload["blocked_reasons"]
    assert "app_env_test_gate" in payload["pass_reasons"]
    assert "test.gnucash.sqlite" not in str(payload)


def test_owner_writebeta_reset_disabled_fails_closed_before_verify_reset(client, auth_headers, sample_book):
    client.post(f"/books/{sample_book}/owner-writebeta/preflight", headers=auth_headers)
    preview = client.post(
        f"/books/{sample_book}/owner-writebeta/preview",
        headers=auth_headers,
        json={"operation": "CREATE", "payload_shape": {"splits": [{"amount": "private"}]}},
    )
    confirm = client.post(
        f"/books/{sample_book}/owner-writebeta/confirm",
        headers=auth_headers,
        json={"preview_hash": preview.json()["preview_hash"], "backup_ref": "bkp-authorized-ref"},
    )
    assert confirm.status_code == 200

    response = client.post(f"/books/{sample_book}/owner-writebeta/reset-disabled", headers=auth_headers)

    assert response.status_code == 409
    assert "Reset-disabled requires reset_required state" in response.json()["detail"]


def test_owner_writebeta_verify_reset_requires_all_post_mutation_evidence(client, auth_headers, sample_book):
    client.post(f"/books/{sample_book}/owner-writebeta/preflight", headers=auth_headers)
    preview = client.post(
        f"/books/{sample_book}/owner-writebeta/preview",
        headers=auth_headers,
        json={"operation": "CREATE", "payload_shape": {"splits": [{"amount": "private"}]}},
    )
    confirm = client.post(
        f"/books/{sample_book}/owner-writebeta/confirm",
        headers=auth_headers,
        json={"preview_hash": preview.json()["preview_hash"], "backup_ref": "bkp-authorized-ref"},
    )
    assert confirm.status_code == 200

    response = client.post(
        f"/books/{sample_book}/owner-writebeta/verify-reset",
        headers=auth_headers,
        json={"audit_ref": "audit-ok", "restore_ref": "restore-ok", "lock_released": True, "defaults_reset": False},
    )

    assert response.status_code == 409
    assert "verify-reset requires a mutating session" in response.json()["detail"]


def _balanced_transaction_payload():
    return {
        "date": "2026-05-16",
        "description": "Synthetic disabled probe",
        "splits": [
            {"account_id": "bank-guid", "amount": "-100.00", "currency": "SEK", "memo": ""},
            {"account_id": "food-guid", "amount": "100.00", "currency": "SEK", "memo": ""},
        ],
    }


def test_owner_writebeta_reset_disabled_clears_stale_arm_and_disabled_probes_fail_closed(
    client,
    auth_headers,
    sample_book,
):
    from app.owner_writebeta_state_machine import OwnerWritebetaState
    from app.routers.owner_writebeta import _SESSIONS

    client.post(f"/books/{sample_book}/owner-writebeta/preflight", headers=auth_headers)
    preview = client.post(
        f"/books/{sample_book}/owner-writebeta/preview",
        headers=auth_headers,
        json={"operation": "CREATE", "payload_shape": {"splits": [{"amount": "private"}]}},
    )
    confirm = client.post(
        f"/books/{sample_book}/owner-writebeta/confirm",
        headers=auth_headers,
        json={"preview_hash": preview.json()["preview_hash"], "backup_ref": "bkp-authorized-ref", "restore_readiness_ref": "rr-reset-disabled-test"},
    )
    assert confirm.status_code == 200
    assert confirm.json()["confirmation_token_ref"].startswith("owb-conf-")

    # Simulate the route guard having admitted exactly one already-routed mutation;
    # no GnuCash book or write service is opened in this reset/default-disabled test.
    _SESSIONS[sample_book].transition(OwnerWritebetaState.MUTATING)
    verify = client.post(
        f"/books/{sample_book}/owner-writebeta/verify-reset",
        headers=auth_headers,
        json={"audit_ref": "audit-ok", "restore_ref": "restore-ok", "lock_released": True, "defaults_reset": True},
    )
    assert verify.status_code == 200
    assert verify.json()["state"] == "reset_required"
    assert verify.json()["writes_blocked"] is True

    reset = client.post(f"/books/{sample_book}/owner-writebeta/reset-disabled", headers=auth_headers)

    assert reset.status_code == 200
    payload = reset.json()
    assert payload["state"] == "disabled"
    assert payload["writes_blocked"] is True
    assert "writes_disabled_default" in payload["blocked_reasons"]
    assert payload["summary"]["preview_hash"] is None
    assert payload["summary"]["confirmation_token_ref"] is None

    disabled_probes = [
        ("validate", client.post(f"/books/{sample_book}/transactions/validate", json=_balanced_transaction_payload(), headers=auth_headers)),
        ("create", client.post(f"/books/{sample_book}/transactions", json=_balanced_transaction_payload(), headers=auth_headers)),
        ("patch", client.patch(f"/books/{sample_book}/transactions/synthetic-tx-id", json={"description": "still disabled"}, headers=auth_headers)),
        ("delete", client.delete(f"/books/{sample_book}/transactions/synthetic-tx-id", headers=auth_headers)),
    ]
    status_codes = [probe.status_code for _, probe in disabled_probes]
    assert status_codes == [403, 403, 403, 403], f"Expected all 403 probes, got {status_codes}"
    for name, probe in disabled_probes:
        assert "read-only" in probe.json()["detail"], f"{name} probe missing read-only detail"

    # Critical #36-W1-E assertion: active-arm session refs must be fully cleared.
    # Audit evidence refs (operation_ref, backup_ref, audit_ref, restore_ref)
    # are intentionally preserved for non-mutating record, as are lock_released
    # and defaults_reset booleans. The arms that could re-activate without a
    # new CONFIRMATION must be None.
    assert payload["summary"]["preview_hash"] is None, "preview_hash must be cleared after reset"
    assert payload["summary"]["confirmation_token_ref"] is None, "confirmation_token_ref must be cleared after reset"
    assert payload["summary"]["restore_readiness_ref"] is None, "restore_readiness_ref must be cleared after reset"
    # The /status endpoint must also show default-disabled posture
    status_check = client.get(f"/books/{sample_book}/owner-writebeta/status", headers=auth_headers)
    assert status_check.status_code == 200
    status_payload = status_check.json()
    assert status_payload["state"] == "disabled"
    assert status_payload["writes_blocked"] is True
    assert "writes_disabled_default" in status_payload["blocked_reasons"]
    assert "state_disabled" not in status_payload["blocked_reasons"]  # state is normal disabled, not error
    assert status_payload["summary"]["preview_hash"] is None
    assert status_payload["summary"]["confirmation_token_ref"] is None
    assert status_payload["summary"]["restore_readiness_ref"] is None


def test_owner_writebeta_confirmation_expired_is_explicitly_blocked(client, auth_headers, sample_book):
    """Confirmation state with past expires_at must report confirmation_expired blocked reason."""
    from datetime import timedelta

    from app.owner_writebeta_state_machine import OwnerWritebetaState
    from app.routers.owner_writebeta import _SESSIONS

    client.post(f"/books/{sample_book}/owner-writebeta/preflight", headers=auth_headers)
    preview = client.post(
        f"/books/{sample_book}/owner-writebeta/preview",
        headers=auth_headers,
        json={"operation": "CREATE", "payload_shape": {"splits": [{"amount": "opaque"}]}},
    )
    confirm = client.post(
        f"/books/{sample_book}/owner-writebeta/confirm",
        headers=auth_headers,
        json={
            "preview_hash": preview.json()["preview_hash"],
            "backup_ref": "bkp-expired-test",
            "restore_readiness_ref": "rr-expired-test",
            "ttl_seconds": 1,
        },
    )
    assert confirm.status_code == 200
    assert confirm.json()["state"] == "confirmation"

    # Force the expiry into the past without sleeping
    session = _SESSIONS[sample_book]
    if session.expires_at is not None:
        session.expires_at = session.expires_at - timedelta(seconds=5)
    else:
        from datetime import datetime, timezone

        session.expires_at = datetime.now(timezone.utc) - timedelta(seconds=5)

    status = client.get(f"/books/{sample_book}/owner-writebeta/status", headers=auth_headers)
    assert status.status_code == 200
    payload = status.json()
    assert payload["state"] == "confirmation"
    assert "confirmation_expired" in payload["blocked_reasons"], (
        f"Expected confirmation_expired in blocked_reasons, got {payload['blocked_reasons']}"
    )
    assert payload["writes_blocked"] is True


def test_owner_writebeta_reset_required_is_explicitly_blocked(client, auth_headers, sample_book):
    """Reset_required state must report state_reset_required and clear active arms."""
    from app.owner_writebeta_state_machine import OwnerWritebetaState
    from app.routers.owner_writebeta import _SESSIONS

    client.post(f"/books/{sample_book}/owner-writebeta/preflight", headers=auth_headers)
    preview = client.post(
        f"/books/{sample_book}/owner-writebeta/preview",
        headers=auth_headers,
        json={"operation": "CREATE", "payload_shape": {"splits": [{"amount": "opaque"}]}},
    )
    confirm = client.post(
        f"/books/{sample_book}/owner-writebeta/confirm",
        headers=auth_headers,
        json={
            "preview_hash": preview.json()["preview_hash"],
            "backup_ref": "bkp-reset-req",
            "restore_readiness_ref": "rr-reset-req",
        },
    )
    assert confirm.status_code == 200

    _SESSIONS[sample_book].transition(OwnerWritebetaState.MUTATING)
    verify = client.post(
        f"/books/{sample_book}/owner-writebeta/verify-reset",
        headers=auth_headers,
        json={"audit_ref": "audit-ok", "restore_ref": "restore-ok", "lock_released": True, "defaults_reset": True},
    )
    assert verify.status_code == 200
    payload = verify.json()
    assert payload["state"] == "reset_required"
    assert payload["writes_blocked"] is True
    assert "state_reset_required" in payload["blocked_reasons"], (
        f"Expected state_reset_required in blocked_reasons, got {payload['blocked_reasons']}"
    )
    # Active arms must be cleared in summary
    assert payload["summary"]["preview_hash"] is None
    assert payload["summary"]["confirmation_token_ref"] is None
    assert payload["summary"]["restore_readiness_ref"] is None


def test_owner_writebeta_failed_hard_stop_is_explicitly_blocked(client, auth_headers, sample_book):
    """Failed hard stop must block writes and sanitize failed_reason in summary."""
    from app.owner_writebeta_state_machine import OwnerWritebetaState
    from app.routers.owner_writebeta import _SESSIONS

    client.post(f"/books/{sample_book}/owner-writebeta/preflight", headers=auth_headers)
    preview = client.post(
        f"/books/{sample_book}/owner-writebeta/preview",
        headers=auth_headers,
        json={"operation": "CREATE", "payload_shape": {"tx": "opaque"}},
    )
    assert preview.status_code == 200
    confirm = client.post(
        f"/books/{sample_book}/owner-writebeta/confirm",
        headers=auth_headers,
        json={
            "preview_hash": preview.json()["preview_hash"],
            "backup_ref": "bkp-hard-stop",
            "restore_readiness_ref": "rr-hard-stop",
        },
    )
    assert confirm.status_code == 200

    _SESSIONS[sample_book].transition(OwnerWritebetaState.MUTATING)
    verify = client.post(
        f"/books/{sample_book}/owner-writebeta/verify-reset",
        headers=auth_headers,
        json={
            "audit_ref": "audit-hs",
            "restore_ref": "restore-hs",
            "lock_released": True,
            "defaults_reset": False,
        },
    )
    assert verify.status_code == 200
    payload = verify.json()
    assert payload["state"] == "failed_hard_stop"
    assert payload["writes_blocked"] is True
    assert "state_failed_hard_stop" in payload["blocked_reasons"], (
        f"Expected state_failed_hard_stop in blocked_reasons, got {payload['blocked_reasons']}"
    )
    # Reason must be sanitized
    summary = payload["summary"]
    assert summary["failed_reason"] in {
        "post-mutation verification incomplete",
        "restore readiness failed",
        "owner-writebeta session failed; see opaque audit refs only.",
    }


def test_owner_writebeta_preflight_blocked_reasons_exclude_state_prefix(client, auth_headers, sample_book):
    """Preflight must not report state-based blocked reasons."""
    response = client.post(f"/books/{sample_book}/owner-writebeta/preflight", headers=auth_headers)
    assert response.status_code == 200
    payload = response.json()
    assert payload["state"] == "preflight"
    assert payload["writes_blocked"] is True
    assert "writes_disabled_default" in payload["blocked_reasons"]
    assert "app_env_test_gate" in payload["pass_reasons"]
    for reason in payload["blocked_reasons"]:
        assert not reason.startswith("state_"), (
            f"Preflight should not have state_* blocked reason, got: {reason}"
        )


def test_owner_writebeta_confirmation_without_restore_readiness_is_blocked(client, auth_headers, sample_book):
    """Confirmation without restore_readiness_ref should report restore_not_ready."""
    client.post(f"/books/{sample_book}/owner-writebeta/preflight", headers=auth_headers)
    preview = client.post(
        f"/books/{sample_book}/owner-writebeta/preview",
        headers=auth_headers,
        json={"operation": "CREATE", "payload_shape": {"splits": [{"amount": "opaque"}]}},
    )
    # Confirm WITHOUT restore_readiness_ref
    confirm = client.post(
        f"/books/{sample_book}/owner-writebeta/confirm",
        headers=auth_headers,
        json={
            "preview_hash": preview.json()["preview_hash"],
            "backup_ref": "bkp-no-rr",
        },
    )
    assert confirm.status_code == 200
    assert confirm.json()["state"] == "confirmation"

    status = client.get(f"/books/{sample_book}/owner-writebeta/status", headers=auth_headers)
    assert status.status_code == 200
    payload = status.json()
    assert "restore_not_ready" in payload["blocked_reasons"], (
        f"Expected restore_not_ready in blocked_reasons, got {payload['blocked_reasons']}"
    )
