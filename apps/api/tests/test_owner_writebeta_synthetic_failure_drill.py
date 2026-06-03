"""
Synthetic failure/hard-stop drill for owner-writebeta.

Issue #36-W2-C: prove that when read-back/restore/audit/lock/default-reset
verification fails after a synthetic mutation attempt, the owner-writebeta
state machine / route reports failed hard stop and future mutation is blocked.

Only opaque references and synthetic sessions are used. No real/private/original
books, no financial evidence, no public write UI.
"""
from __future__ import annotations

import json

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
from app.services.auth import hash_password as _hash_password

TEST_ADMIN_PASSWORD = "test" + "password123"
TEST_JWT_SECRET = "test-secret-key-for-unit-tests-" + "32-bytes-minimum"

TEST_SETTINGS = Settings(
    app_env="test",
    app_database_url="sqlite:///:memory:",
    jwt_secret=TEST_JWT_SECRET,
    app_admin_username="admin",
    app_admin_password=TEST_ADMIN_PASSWORD,
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
                password_hash=_hash_password(TEST_ADMIN_PASSWORD),
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
    response = client.post(
        "/auth/login",
        json={"username": "admin", "password": TEST_ADMIN_PASSWORD},
    )
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def synthetic_book_id(session_factory):
    with session_factory() as session:
        book = Book(
            name="Synthetic Failure Drill Book",
            storage_type="sqlite",
            uri_or_path="/data/books/synthetic-failure-drill.sqlite",
            is_default=True,
        )
        session.add(book)
        session.flush()
        admin = session.query(User).filter(User.username == "admin").one()
        session.add(UserBookAccess(user_id=admin.id, book_id=book.id, role="owner"))
        session.commit()
        return book.id


# ---------------------------------------------------------------------------
# State-machine-only tests (no HTTP, no route) -- pure TDD on the state machine
# ---------------------------------------------------------------------------


def test_synthetic_missing_audit_ref_triggers_hard_stop():
    """State machine: missing audit_ref causes FAILED_HARD_STOP and writes_blocked."""
    from app.owner_writebeta_state_machine import (
        OwnerWritebetaSession,
        OwnerWritebetaState,
        arm_confirmed_preview,
        mark_post_mutation_checks,
        prepare_preview,
    )

    session = OwnerWritebetaSession()
    session.transition(OwnerWritebetaState.PREFLIGHT)
    prepare_preview(session, "CREATE", {"splits": [{"amount": "synthetic"}]}, count=1)
    arm_confirmed_preview(
        session,
        preview_hash=session.preview_hash,
        backup_ref="bkp-synth-audit",
        restore_readiness_ref="rr-synth-audit",
    )
    session.transition(OwnerWritebetaState.MUTATING)

    # Deliberately provide empty audit_ref and valid other fields
    mark_post_mutation_checks(
        session,
        audit_ref="",
        restore_ref="restore-synth-audit",
        lock_released=True,
        defaults_reset=True,
    )
    assert session.state == OwnerWritebetaState.FAILED_HARD_STOP, (
        f"Expected failed_hard_stop when audit_ref is empty, got {session.state}"
    )
    assert session.writes_blocked is True
    assert session.failed_reason == "post-mutation verification incomplete"
    summary = session.redacted_summary()
    assert summary["writes_blocked"] is True
    assert summary["state"] == "failed_hard_stop"


def test_synthetic_missing_restore_ref_triggers_hard_stop():
    """State machine: missing restore_ref causes FAILED_HARD_STOP and writes_blocked."""
    from app.owner_writebeta_state_machine import (
        OwnerWritebetaSession,
        OwnerWritebetaState,
        arm_confirmed_preview,
        mark_post_mutation_checks,
        prepare_preview,
    )

    session = OwnerWritebetaSession()
    session.transition(OwnerWritebetaState.PREFLIGHT)
    prepare_preview(session, "PATCH", {"fields": ["description"]}, count=1)
    arm_confirmed_preview(
        session,
        preview_hash=session.preview_hash,
        backup_ref="bkp-synth-restore",
        restore_readiness_ref="rr-synth-restore",
    )
    session.transition(OwnerWritebetaState.MUTATING)

    # Deliberately omit restore_ref
    mark_post_mutation_checks(
        session,
        audit_ref="audit-synth-restore",
        restore_ref="",
        lock_released=True,
        defaults_reset=True,
    )
    assert session.state == OwnerWritebetaState.FAILED_HARD_STOP
    assert session.writes_blocked is True
    summary = session.redacted_summary()
    assert summary["writes_blocked"] is True
    assert summary["state"] == "failed_hard_stop"


def test_synthetic_lock_not_released_triggers_hard_stop():
    """State machine: lock_released=False causes FAILED_HARD_STOP."""
    from app.owner_writebeta_state_machine import (
        OwnerWritebetaSession,
        OwnerWritebetaState,
        arm_confirmed_preview,
        mark_post_mutation_checks,
        prepare_preview,
    )

    session = OwnerWritebetaSession()
    session.transition(OwnerWritebetaState.PREFLIGHT)
    prepare_preview(session, "DELETE", {"transaction_id": "synthetic-id"}, count=1)
    arm_confirmed_preview(
        session,
        preview_hash=session.preview_hash,
        backup_ref="bkp-synth-lock",
        restore_readiness_ref="rr-synth-lock",
    )
    session.transition(OwnerWritebetaState.MUTATING)

    mark_post_mutation_checks(
        session,
        audit_ref="audit-synth-lock",
        restore_ref="restore-synth-lock",
        lock_released=False,
        defaults_reset=True,
    )
    assert session.state == OwnerWritebetaState.FAILED_HARD_STOP
    assert session.writes_blocked is True
    assert session.lock_released is False


def test_synthetic_defaults_not_reset_triggers_hard_stop():
    """State machine: defaults_reset=False causes FAILED_HARD_STOP."""
    from app.owner_writebeta_state_machine import (
        OwnerWritebetaSession,
        OwnerWritebetaState,
        arm_confirmed_preview,
        mark_post_mutation_checks,
        prepare_preview,
    )

    session = OwnerWritebetaSession()
    session.transition(OwnerWritebetaState.PREFLIGHT)
    prepare_preview(session, "CREATE", {"splits": [{"amount": "synthetic"}]}, count=1)
    arm_confirmed_preview(
        session,
        preview_hash=session.preview_hash,
        backup_ref="bkp-synth-defaults",
        restore_readiness_ref="rr-synth-defaults",
    )
    session.transition(OwnerWritebetaState.MUTATING)

    mark_post_mutation_checks(
        session,
        audit_ref="audit-synth-defaults",
        restore_ref="restore-synth-defaults",
        lock_released=True,
        defaults_reset=False,
    )
    assert session.state == OwnerWritebetaState.FAILED_HARD_STOP
    assert session.writes_blocked is True
    assert session.defaults_reset is False


def test_synthetic_hard_stop_blocks_all_further_transitions():
    """FAILED_HARD_STOP is terminal -- no further state transitions are allowed."""
    from app.owner_writebeta_state_machine import (
        OwnerWritebetaSession,
        OwnerWritebetaState,
        OwnerWritebetaTransitionError,
        arm_confirmed_preview,
        mark_post_mutation_checks,
        prepare_preview,
    )

    session = OwnerWritebetaSession()
    session.transition(OwnerWritebetaState.PREFLIGHT)
    prepare_preview(session, "CREATE", {"splits": [{"amount": "synthetic"}]}, count=1)
    arm_confirmed_preview(
        session,
        preview_hash=session.preview_hash,
        backup_ref="bkp-synth-terminal",
        restore_readiness_ref="rr-synth-terminal",
    )
    session.transition(OwnerWritebetaState.MUTATING)
    mark_post_mutation_checks(
        session,
        audit_ref="",
        restore_ref="",
        lock_released=False,
        defaults_reset=False,
    )
    assert session.state == OwnerWritebetaState.FAILED_HARD_STOP
    assert session.writes_blocked is True

    for target in OwnerWritebetaState:
        if target == OwnerWritebetaState.FAILED_HARD_STOP:
            continue
        with pytest.raises(OwnerWritebetaTransitionError):
            session.transition(target)


def test_synthetic_hard_stop_summary_is_safe_and_redacted():
    """Hard-stop summary exposes state/blocked but no raw evidence or unsafe reasons."""
    from app.owner_writebeta_state_machine import (
        OwnerWritebetaSession,
        OwnerWritebetaState,
        arm_confirmed_preview,
        mark_post_mutation_checks,
        prepare_preview,
    )

    session = OwnerWritebetaSession()
    session.transition(OwnerWritebetaState.PREFLIGHT)
    prepare_preview(
        session,
        "CREATE",
        {"splits": [{"amount": "synthetic", "account_id": "secret-guid"}]},
        count=1,
    )
    arm_confirmed_preview(
        session,
        preview_hash=session.preview_hash,
        backup_ref="bkp-summary-safe",
        restore_readiness_ref="rr-summary-safe",
    )
    session.transition(OwnerWritebetaState.MUTATING)
    mark_post_mutation_checks(
        session,
        audit_ref="",
        restore_ref="",
        lock_released=False,
        defaults_reset=False,
    )

    summary = session.redacted_summary()
    assert summary["state"] == "failed_hard_stop"
    assert summary["writes_blocked"] is True
    # Opaque refs only; no account IDs, amounts, descriptions, paths
    summary_json = json.dumps(summary)
    assert "secret-guid" not in summary_json
    # Amount must not leak
    assert "synthetic" not in summary_json or "session_ref" in summary_json
    # The failed_reason must be sanitized
    failed_reason = summary["failed_reason"]
    assert failed_reason in {
        "post-mutation verification incomplete",
        "restore readiness failed",
        "owner-writebeta session failed; see opaque audit refs only.",
    }


# ---------------------------------------------------------------------------
# Route-level tests (HTTP, state machine behind route)
# ---------------------------------------------------------------------------


def _prepare_mutating_session(client, auth_headers, book_id):
    """Arm a CONFIRMATION session and transition to MUTATING, ready for verify-reset."""
    from app.owner_writebeta_state_machine import OwnerWritebetaSession, OwnerWritebetaState
    from app.routers.owner_writebeta import _SESSIONS

    client.post(f"/books/{book_id}/owner-writebeta/preflight", headers=auth_headers)
    preview = client.post(
        f"/books/{book_id}/owner-writebeta/preview",
        headers=auth_headers,
        json={
            "operation": "CREATE",
            "payload_shape": {"splits": [{"amount": "synthetic"}]},
            "count": 1,
        },
    )
    assert preview.status_code == 200
    preview_hash = preview.json()["preview_hash"]

    confirm = client.post(
        f"/books/{book_id}/owner-writebeta/confirm",
        headers=auth_headers,
        json={
            "preview_hash": preview_hash,
            "backup_ref": "bkp-synthetic",
            "restore_readiness_ref": "rr-synthetic",
        },
    )
    assert confirm.status_code == 200
    assert confirm.json()["state"] == "confirmation"

    # Transition to MUTATING (as the route guard would during an actual mutation)
    _SESSIONS[book_id].transition(OwnerWritebetaState.MUTATING)
    return book_id


def test_synthetic_route_mutation_after_hard_stop_is_blocked(
    client, auth_headers, session_factory
):
    """
    Route-level: a MUTATE session that hard-stops must yield writes_blocked
    True in /status, and subsequent /status calls continue showing failed_hard_stop.
    """
    from app.routers.owner_writebeta import _SESSIONS

    book_id = _prepare_mutating_session_with_fixtures(client, auth_headers, session_factory)

    # Synthetic verification failure: defaults_reset=False
    verify = client.post(
        f"/books/{book_id}/owner-writebeta/verify-reset",
        headers=auth_headers,
        json={
            "audit_ref": "audit-route-drill",
            "restore_ref": "restore-route-drill",
            "lock_released": True,
            "defaults_reset": False,
        },
    )
    assert verify.status_code == 200
    payload = verify.json()
    assert payload["state"] == "failed_hard_stop"
    assert payload["writes_blocked"] is True
    assert "state_failed_hard_stop" in payload["blocked_reasons"]
    summary = payload["summary"]
    assert summary["state"] == "failed_hard_stop"
    assert summary["writes_blocked"] is True

    # /status must continue to show hard stop and writes blocked
    status = client.get(
        f"/books/{book_id}/owner-writebeta/status",
        headers=auth_headers,
    )
    assert status.status_code == 200
    status_payload = status.json()
    assert status_payload["state"] == "failed_hard_stop"
    assert status_payload["writes_blocked"] is True
    assert "state_failed_hard_stop" in status_payload["blocked_reasons"]
    assert status_payload["summary"]["preview_hash"] is None
    assert status_payload["summary"]["confirmation_token_ref"] is None
    assert status_payload["summary"]["restore_readiness_ref"] is None


def test_synthetic_route_preflight_after_hard_stop_is_blocked(
    client, auth_headers, session_factory
):
    """After a hard stop, /preflight must be 409 because transition is blocked."""
    from app.routers.owner_writebeta import _SESSIONS

    book_id = _prepare_mutating_session_with_fixtures(client, auth_headers, session_factory)

    # Trigger hard stop via verify-reset (missing audit_ref)
    client.post(
        f"/books/{book_id}/owner-writebeta/verify-reset",
        headers=auth_headers,
        json={
            "audit_ref": "",
            "restore_ref": "restore-synth-preflight",
            "lock_released": True,
            "defaults_reset": True,
        },
    )

    preflight = client.post(
        f"/books/{book_id}/owner-writebeta/preflight",
        headers=auth_headers,
    )
    assert preflight.status_code == 409
    assert "blocked by current state" in preflight.json()["detail"]


def test_synthetic_route_preview_and_confirm_after_hard_stop_are_blocked(
    client, auth_headers, session_factory
):
    """After hard stop, /preview and /confirm must both be 409."""
    from app.routers.owner_writebeta import _SESSIONS

    book_id = _prepare_mutating_session_with_fixtures(client, auth_headers, session_factory)

    # Trigger hard stop
    client.post(
        f"/books/{book_id}/owner-writebeta/verify-reset",
        headers=auth_headers,
        json={
            "audit_ref": "audit-synth-preview",
            "restore_ref": "",
            "lock_released": False,
            "defaults_reset": False,
        },
    )

    # /preview requires PREFLIGHT state
    preview = client.post(
        f"/books/{book_id}/owner-writebeta/preview",
        headers=auth_headers,
        json={
            "operation": "CREATE",
            "payload_shape": {"splits": [{"amount": "synthetic"}]},
            "count": 1,
        },
    )
    assert preview.status_code == 409

    # /confirm requires PREVIEW state
    confirm = client.post(
        f"/books/{book_id}/owner-writebeta/confirm",
        headers=auth_headers,
        json={
            "preview_hash": "owb-prev-nonexistent",
            "backup_ref": "bkp-hard-stopped",
        },
    )
    assert confirm.status_code == 409


def test_synthetic_multiple_distinct_failure_modes_are_hard_stop(
    client, auth_headers, session_factory
):
    """
    End-to-end: two distinct verification failure modes each produce
    failed_hard_stop from fresh sessions with safe summaries.
    """
    from app.owner_writebeta_state_machine import OwnerWritebetaSession, OwnerWritebetaState
    from app.routers.owner_writebeta import _SESSIONS

    book_id = _create_book_with_owner(session_factory)
    failure_cases = [
        {
            # audit_ref present but restore_ref present & empty -> hard stop
            "name": "lock_not_released_defaults_pending",
            "audit_ref": "audit-multi-drill",
            "restore_ref": "restore-multi-drill",
            "lock_released": False,
            "defaults_reset": False,
        },
        {
            # Only lock_released True, defaults_reset False -> hard stop
            "name": "defaults_not_reset",
            "audit_ref": "audit-multi-drill-2",
            "restore_ref": "restore-multi-drill-2",
            "lock_released": True,
            "defaults_reset": False,
        },
    ]

    for case in failure_cases:
        _SESSIONS.clear()

        _prepare_mutating_session_with_fixtures(client, auth_headers, session_factory, book_id=book_id)

        verify = client.post(
            f"/books/{book_id}/owner-writebeta/verify-reset",
            headers=auth_headers,
            json={
                "audit_ref": case["audit_ref"],
                "restore_ref": case["restore_ref"],
                "lock_released": case["lock_released"],
                "defaults_reset": case["defaults_reset"],
            },
        )
        assert verify.status_code == 200, (
            f"Case {case['name']}: expected 200, got {verify.status_code}"
        )
        payload = verify.json()
        assert payload["state"] == "failed_hard_stop", (
            f"Case {case['name']}: expected failed_hard_stop, got {payload['state']}"
        )
        assert payload["writes_blocked"] is True, (
            f"Case {case['name']}: expected writes_blocked True"
        )
        assert "state_failed_hard_stop" in payload["blocked_reasons"], (
            f"Case {case['name']}: missing state_failed_hard_stop in blocked_reasons"
        )
        summary = payload["summary"]
        assert summary["state"] == "failed_hard_stop"
        assert summary["writes_blocked"] is True
        assert summary["preview_hash"] is None
        assert summary["confirmation_token_ref"] is None
        assert summary["restore_readiness_ref"] is None


def test_synthetic_two_failure_modes_summary_sanitized_redirect(
    client, auth_headers, session_factory
):
    """
    Prove that both missing-audit-ref AND lock-not-released failure modes
    produce sanitized failed_reason in the summary (not raw evidence).
    """
    from app.owner_writebeta_state_machine import OwnerWritebetaSession, OwnerWritebetaState
    from app.routers.owner_writebeta import _SESSIONS

    book_id = _create_book_with_owner(session_factory)
    cases = [
        {"audit_ref": "audit-sanitize-a", "restore_ref": "rr-sanitize-a", "lock_released": False, "defaults_reset": True},
        {"audit_ref": "audit-sanitize-b", "restore_ref": "restore-sanitize-b", "lock_released": True, "defaults_reset": False},
    ]
    safe_reasons = {
        "post-mutation verification incomplete",
        "restore readiness failed",
        "owner-writebeta session failed; see opaque audit refs only.",
    }

    for case in cases:
        _SESSIONS.clear()
        _prepare_mutating_session_with_fixtures(client, auth_headers, session_factory, book_id=book_id)

        verify = client.post(
            f"/books/{book_id}/owner-writebeta/verify-reset",
            headers=auth_headers,
            json={
                "audit_ref": case["audit_ref"],
                "restore_ref": case["restore_ref"],
                "lock_released": case["lock_released"],
                "defaults_reset": case["defaults_reset"],
            },
        )
        assert verify.status_code == 200
        payload = verify.json()
        assert payload["state"] == "failed_hard_stop"
        failed_reason = payload["summary"]["failed_reason"]
        assert failed_reason in safe_reasons, (
            f"failed_reason {failed_reason!r} is not a safe reason"
        )


# ---------------------------------------------------------------------------
# Shared fixtures / helpers
# ---------------------------------------------------------------------------


def _create_book_with_owner(session_factory):
    with session_factory() as session:
        admin = session.query(User).filter(User.username == "admin").first()
        if admin is None:
            session.add(
                User(
                    username="admin",
                    display_name="Admin",
                    password_hash=_hash_password(TEST_ADMIN_PASSWORD),
                    is_admin=True,
                )
            )
            session.flush()
            admin = session.query(User).filter(User.username == "admin").one()
        book = Book(
            name="Synthetic Failure Drill Book",
            storage_type="sqlite",
            uri_or_path="/data/books/synthetic-failure-drill.sqlite",
            is_default=True,
        )
        session.add(book)
        session.flush()
        # Ensure the user-book access exists
        existing_access = session.query(UserBookAccess).filter(
            UserBookAccess.user_id == admin.id,
            UserBookAccess.book_id == book.id,
        ).first()
        if existing_access is None:
            session.add(UserBookAccess(user_id=admin.id, book_id=book.id, role="owner"))
        session.commit()
        return book.id


def _prepare_mutating_session_with_fixtures(client, auth_headers, session_factory, book_id=None):
    """Arm a fresh MUTATING session for the given (or new) book."""
    from app.owner_writebeta_state_machine import OwnerWritebetaState
    from app.routers.owner_writebeta import _SESSIONS

    if book_id is None:
        book_id = _create_book_with_owner(session_factory)

    _SESSIONS.clear()

    client.post(f"/books/{book_id}/owner-writebeta/preflight", headers=auth_headers)
    preview = client.post(
        f"/books/{book_id}/owner-writebeta/preview",
        headers=auth_headers,
        json={
            "operation": "CREATE",
            "payload_shape": {"splits": [{"amount": "synthetic"}]},
            "count": 1,
        },
    )
    assert preview.status_code == 200
    preview_hash = preview.json()["preview_hash"]

    confirm = client.post(
        f"/books/{book_id}/owner-writebeta/confirm",
        headers=auth_headers,
        json={
            "preview_hash": preview_hash,
            "backup_ref": "bkp-synth-route",
            "restore_readiness_ref": "rr-synth-route",
        },
    )
    assert confirm.status_code == 200

    # Transition to MUTATING as the route guard would during mutation
    _SESSIONS[book_id].transition(OwnerWritebetaState.MUTATING)
    return book_id
