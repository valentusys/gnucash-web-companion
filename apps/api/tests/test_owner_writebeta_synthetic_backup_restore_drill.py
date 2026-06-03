"""#36-W2-B synthetic backup/restore drill regressions.

Synthetic state-machine and route checks only. No GnuCash book, backup file,
private path, app DB file, account name, memo, description, amount, or raw
private evidence is used.
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
from app.owner_writebeta_state_machine import (
    OwnerWritebetaSession,
    OwnerWritebetaState,
    OwnerWritebetaTransitionError,
    arm_confirmed_preview,
    mark_post_mutation_checks,
    prepare_preview,
)
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
    from app.routers.owner_writebeta import _SESSIONS

    _SESSIONS.clear()
    test_client = TestClient(app)
    yield test_client
    _SESSIONS.clear()
    app.dependency_overrides.clear()
    get_settings.cache_clear()


@pytest.fixture
def auth_headers(client):
    response = client.post("/auth/login", json={"username": "admin", "password": "testpassword123"})
    return {"Authorization": f"Bearer {response.json()['access_token']}"}


@pytest.fixture
def synthetic_book(session_factory):
    with session_factory() as session:
        book = Book(
            name="Synthetic backup restore readiness fixture",
            storage_type="sqlite",
            uri_or_path="synthetic://backup-restore-readiness",
            is_default=True,
        )
        session.add(book)
        session.flush()
        admin = session.query(User).filter(User.username == "admin").one()
        session.add(UserBookAccess(user_id=admin.id, book_id=book.id, role="owner"))
        session.commit()
        return book.id


def _mutating_session() -> OwnerWritebetaSession:
    session = OwnerWritebetaSession()
    session.transition(OwnerWritebetaState.PREFLIGHT)
    prepare_preview(session, "CREATE", {"synthetic": {"shape": "only"}}, count=1)
    assert session.preview_hash is not None
    arm_confirmed_preview(
        session,
        preview_hash=session.preview_hash,
        backup_ref="bkp-synthetic-drill",
        restore_readiness_ref="rr-synthetic-drill",
    )
    session.transition(OwnerWritebetaState.MUTATING)
    return session


def test_synthetic_backup_restore_success_requires_all_opaque_refs_and_redacts_summary():
    session = _mutating_session()

    mark_post_mutation_checks(
        session,
        audit_ref="audit-synthetic-drill",
        restore_ref="restore-synthetic-drill",
        lock_released=True,
        defaults_reset=True,
    )

    assert session.state == OwnerWritebetaState.RESET_REQUIRED
    summary = session.redacted_summary()
    assert summary["backup_ref"] == "bkp-synthetic-drill"
    assert summary["restore_ref"] == "restore-synthetic-drill"
    assert summary["audit_ref"] == "audit-synthetic-drill"
    assert summary["preview_hash"] is None
    assert summary["confirmation_token_ref"] is None
    assert summary["restore_readiness_ref"] is None
    serialized = json.dumps(summary, sort_keys=True)
    for forbidden in ["/", "\\", ".gnucash", "sqlite", "amount", "memo", "description", "account"]:
        assert forbidden not in serialized


def test_synthetic_restore_failure_hard_stops_and_blocks_further_mutation():
    session = _mutating_session()

    mark_post_mutation_checks(
        session,
        audit_ref="audit-restore-failure",
        restore_ref="restore-restore-failure",
        lock_released=True,
        defaults_reset=False,
    )

    assert session.state == OwnerWritebetaState.FAILED_HARD_STOP
    assert session.writes_blocked is True
    assert session.redacted_summary()["restore_ref"] is None
    with pytest.raises(OwnerWritebetaTransitionError):
        session.transition(OwnerWritebetaState.MUTATING)


@pytest.mark.parametrize(
    ("audit_ref", "restore_ref"),
    [
        ("audit-ok", "/tmp/private-restore.sqlite"),
        ("audit ok", "restore-ok"),
        ("https://audit.example/private", "restore-ok"),
    ],
)
def test_synthetic_backup_restore_rejects_path_like_refs_even_when_hard_stop_would_follow(audit_ref, restore_ref):
    session = _mutating_session()

    with pytest.raises(OwnerWritebetaTransitionError, match="opaque reference"):
        mark_post_mutation_checks(
            session,
            audit_ref=audit_ref,
            restore_ref=restore_ref,
            lock_released=False,
            defaults_reset=False,
        )
    assert session.state == OwnerWritebetaState.MUTATING
    assert session.redacted_summary()["audit_ref"] is None
    assert session.redacted_summary()["restore_ref"] is None


def test_synthetic_route_verify_reset_rejects_path_like_restore_refs_before_summary(client, auth_headers, synthetic_book):
    from app.routers.owner_writebeta import _SESSIONS

    client.post(f"/books/{synthetic_book}/owner-writebeta/preflight", headers=auth_headers)
    preview = client.post(
        f"/books/{synthetic_book}/owner-writebeta/preview",
        headers=auth_headers,
        json={"operation": "CREATE", "payload_shape": {"synthetic": "shape"}},
    )
    confirm = client.post(
        f"/books/{synthetic_book}/owner-writebeta/confirm",
        headers=auth_headers,
        json={
            "preview_hash": preview.json()["preview_hash"],
            "backup_ref": "bkp-route-drill",
            "restore_readiness_ref": "rr-route-drill",
        },
    )
    assert confirm.status_code == 200
    _SESSIONS[synthetic_book].transition(OwnerWritebetaState.MUTATING)

    response = client.post(
        f"/books/{synthetic_book}/owner-writebeta/verify-reset",
        headers=auth_headers,
        json={
            "audit_ref": "audit-route-drill",
            "restore_ref": "/tmp/private-restore.sqlite",
            "lock_released": False,
            "defaults_reset": False,
        },
    )

    assert response.status_code == 409
    assert "opaque reference" in response.json()["detail"]
    summary = client.get(f"/books/{synthetic_book}/owner-writebeta/status", headers=auth_headers).json()["summary"]
    assert "/tmp/private-restore.sqlite" not in json.dumps(summary)
    assert summary["restore_ref"] is None
