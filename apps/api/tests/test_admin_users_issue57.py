"""Issue #57 B2 admin local-user API tests."""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker

from app.config import Settings, get_settings
from app.database import Base
from app.main import app
from app.models import AuditLog, Book, User, UserBookAccess
from app.routers.auth import get_db
from app.services.auth import hash_password

ADMIN_PASSWORD = "AdminPass123!"
VIEWER_PASSWORD = "ViewerPass123!"
OTHER_ADMIN_PASSWORD = "OtherAdmin123!"
JWT_SECRET = "test-secret-key-for-admin-users-issue57-32-bytes"


def _settings(tmp_path: Path) -> Settings:
    return Settings(
        app_env="test",
        app_database_url=f"sqlite:///{tmp_path / 'app.db'}",
        gnucash_book_allowed_roots=[str(tmp_path)],
        jwt_secret=JWT_SECRET,
        jwt_token_expire_minutes=30,
        app_admin_username="admin",
        app_admin_password=ADMIN_PASSWORD,
    )


@pytest.fixture
def engine(tmp_path):
    engine = create_engine(
        f"sqlite:///{tmp_path / 'admin-users.db'}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def session_factory(engine):
    return sessionmaker(bind=engine)


@pytest.fixture
def client(tmp_path, session_factory):
    settings = _settings(tmp_path)

    def override_get_db():
        with session_factory() as session:
            yield session

    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_db] = override_get_db

    with session_factory() as session:
        admin = User(
            username="admin",
            display_name="Admin",
            password_hash=hash_password(ADMIN_PASSWORD),
            is_admin=True,
        )
        viewer = User(
            username="viewer",
            display_name="Viewer",
            password_hash=hash_password(VIEWER_PASSWORD),
            is_admin=False,
        )
        other_admin = User(
            username="otheradmin",
            display_name="Other Admin",
            password_hash=hash_password(OTHER_ADMIN_PASSWORD),
            is_admin=True,
        )
        book = Book(
            name="Synthetic Book",
            storage_type="sqlite",
            uri_or_path=str(tmp_path / "synthetic.gnucash.sqlite"),
            is_default=True,
        )
        archived_book = Book(
            name="Archived Book",
            storage_type="sqlite",
            uri_or_path=str(tmp_path / "archived.gnucash.sqlite"),
            is_archived=True,
        )
        disabled_book = Book(
            name="Disabled Book",
            storage_type="sqlite",
            uri_or_path=str(tmp_path / "disabled.gnucash.sqlite"),
            is_enabled=False,
        )
        session.add_all([admin, viewer, other_admin, book, archived_book, disabled_book])
        session.flush()
        session.add_all(
            [
                UserBookAccess(user_id=viewer.id, book_id=book.id, role="viewer"),
                UserBookAccess(user_id=viewer.id, book_id=archived_book.id, role="editor"),
                UserBookAccess(user_id=viewer.id, book_id=disabled_book.id, role="owner"),
            ]
        )
        session.commit()

    test_client = TestClient(app)
    yield test_client

    app.dependency_overrides.clear()
    get_settings.cache_clear()


def _login(client: TestClient, username: str = "admin", password: str = ADMIN_PASSWORD) -> str:
    response = client.post("/auth/login", json={"username": username, "password": password})
    assert response.status_code == 200, response.text
    return response.json()["access_token"]


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _safe_code(response) -> str:
    detail = response.json()["detail"]
    assert set(detail) == {"safe_code"}
    return detail["safe_code"]


def _user_id(session_factory, username: str) -> int:
    with session_factory() as session:
        return session.query(User).filter(User.username == username).one().id


def _audit_payloads(session_factory) -> list[tuple[str, dict[str, object]]]:
    with session_factory() as session:
        rows = session.query(AuditLog).order_by(AuditLog.id).all()
        return [(row.action, json.loads(row.payload_json or "{}")) for row in rows]


def test_admin_lists_users_bounded_ordered_redacted_and_without_n_plus_one(
    client, session_factory, engine
):
    token = _login(client)
    select_count = 0

    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        nonlocal select_count
        if statement.lstrip().lower().startswith("select"):
            select_count += 1

    event.listen(engine, "before_cursor_execute", before_cursor_execute)
    try:
        response = client.get(
            "/admin/users?limit=100&offset=0&state=all",
            headers=_headers(token),
        )
    finally:
        event.remove(engine, "before_cursor_execute", before_cursor_execute)

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["total_count"] == 3
    assert data["limit"] == 100
    assert data["offset"] == 0
    assert data["has_next"] is False
    assert [item["username"] for item in data["items"]] == [
        "admin",
        "otheradmin",
        "viewer",
    ]
    viewer_item = data["items"][2]
    assert viewer_item["assignment_count"] == 1
    assert viewer_item["assignments"] == [
        {"book_id": 1, "book_name": "Synthetic Book", "is_default": True, "role": "viewer"}
    ]
    assert set(data["items"][0]) == {
        "id",
        "username",
        "display_name",
        "is_admin",
        "is_enabled",
        "assignment_count",
        "assignments",
        "created_at",
        "updated_at",
    }
    assert "password_hash" not in response.text
    assert "auth_version" not in response.text
    assert ADMIN_PASSWORD not in response.text
    with session_factory() as session:
        for password_hash in session.query(User.password_hash).all():
            assert password_hash[0] not in response.text
    assert select_count <= 4

    page = client.get("/admin/users?limit=1&offset=1", headers=_headers(token))
    assert page.status_code == 200
    assert page.json()["has_next"] is True
    assert [item["username"] for item in page.json()["items"]] == ["otheradmin"]

    disabled_only = client.get(
        "/admin/users?state=disabled",
        headers=_headers(token),
    )
    assert disabled_only.status_code == 200
    assert disabled_only.json()["items"] == []


def test_admin_creates_local_user_and_admin_without_assignments_and_duplicate_conflicts(
    client, session_factory
):
    headers = _headers(_login(client))

    user_response = client.post(
        "/admin/users",
        headers=headers,
        json={
            "username": " New.User ",
            "display_name": "  Ｎew User  ",
            "password": "NewUserPass123!",
        },
    )
    assert user_response.status_code == 201, user_response.text
    user_data = user_response.json()
    assert user_data["username"] == "new.user"
    assert user_data["display_name"] == "New User"
    assert user_data["is_admin"] is False
    assert user_data["is_enabled"] is True
    assert user_data["assignment_count"] == 0
    assert user_data["assignments"] == []
    assert "password" not in user_response.text
    assert "hash" not in user_response.text
    assert "auth_version" not in user_response.text

    admin_response = client.post(
        "/admin/users",
        headers=headers,
        json={
            "username": "new-admin",
            "display_name": "New Admin",
            "password": "NewAdminPass123!",
            "is_admin": True,
        },
    )
    assert admin_response.status_code == 201, admin_response.text
    assert admin_response.json()["is_admin"] is True
    assert admin_response.json()["assignment_count"] == 0
    assert admin_response.json()["assignments"] == []

    duplicate = client.post(
        "/admin/users",
        headers=headers,
        json={
            "username": "NEW.USER",
            "display_name": "Duplicate",
            "password": "AnotherPass123!",
        },
    )
    assert duplicate.status_code == 409
    assert _safe_code(duplicate) == "username_taken"
    assert "NEW.USER" not in duplicate.text

    actions = [action for action, _payload in _audit_payloads(session_factory)]
    assert actions == ["user_created", "user_created"]


def test_normal_user_receives_generic_403_for_admin_route_family(client, session_factory):
    viewer_headers = _headers(_login(client, "viewer", VIEWER_PASSWORD))
    viewer_id = _user_id(session_factory, "viewer")

    requests = [
        client.get("/admin/users", headers=viewer_headers),
        client.post(
            "/admin/users",
            headers=viewer_headers,
            json={
                "username": "blocked-user",
                "display_name": "Blocked User",
                "password": "BlockedPass123!",
            },
        ),
        client.get(f"/admin/users/{viewer_id}", headers=viewer_headers),
        client.patch(
            f"/admin/users/{viewer_id}",
            headers=viewer_headers,
            json={"display_name": "Blocked"},
        ),
        client.post(f"/admin/users/{viewer_id}/enable", headers=viewer_headers),
        client.post(f"/admin/users/{viewer_id}/disable", headers=viewer_headers),
        client.post(
            f"/admin/users/{viewer_id}/password-reset",
            headers=viewer_headers,
            json={"new_password": "BlockedReset123!"},
        ),
    ]

    for response in requests:
        assert response.status_code == 403
        assert _safe_code(response) == "admin_required"
        assert "viewer" not in response.text


def test_detail_patch_enable_disable_reset_invalidate_sessions_and_audit_redaction(
    client, session_factory
):
    admin_headers = _headers(_login(client))
    viewer_token = _login(client, "viewer", VIEWER_PASSWORD)
    viewer_id = _user_id(session_factory, "viewer")

    detail = client.get(f"/admin/users/{viewer_id}", headers=admin_headers)
    assert detail.status_code == 200
    assert detail.json()["username"] == "viewer"
    assert detail.json()["assignment_count"] == 1
    assert detail.json()["assignments"] == [
        {"book_id": 1, "book_name": "Synthetic Book", "is_default": True, "role": "viewer"}
    ]

    patch_response = client.patch(
        f"/admin/users/{viewer_id}",
        headers=admin_headers,
        json={"display_name": "  Маус 🐭  "},
    )
    assert patch_response.status_code == 200, patch_response.text
    assert patch_response.json()["display_name"] == "Маус 🐭"

    disable = client.post(f"/admin/users/{viewer_id}/disable", headers=admin_headers)
    assert disable.status_code == 200, disable.text
    assert disable.json()["is_enabled"] is False
    assert client.get("/auth/me", headers=_headers(viewer_token)).status_code == 401
    assert (
        client.post(
            "/auth/login",
            json={"username": "viewer", "password": VIEWER_PASSWORD},
        ).status_code
        == 401
    )

    second_disable = client.post(f"/admin/users/{viewer_id}/disable", headers=admin_headers)
    assert second_disable.status_code == 200
    assert second_disable.json()["is_enabled"] is False

    enable = client.post(f"/admin/users/{viewer_id}/enable", headers=admin_headers)
    assert enable.status_code == 200, enable.text
    assert enable.json()["is_enabled"] is True
    assert client.get("/auth/me", headers=_headers(viewer_token)).status_code == 401

    second_enable = client.post(f"/admin/users/{viewer_id}/enable", headers=admin_headers)
    assert second_enable.status_code == 200
    assert second_enable.json()["is_enabled"] is True

    reset = client.post(
        f"/admin/users/{viewer_id}/password-reset",
        headers=admin_headers,
        json={"new_password": "ResetPass123!"},
    )
    assert reset.status_code == 200, reset.text
    assert reset.json() == {
        "status": "password_reset",
        "subject_user_id": viewer_id,
        "session_invalidated": True,
    }
    assert client.get("/auth/me", headers=_headers(viewer_token)).status_code == 401
    assert (
        client.post(
            "/auth/login",
            json={"username": "viewer", "password": VIEWER_PASSWORD},
        ).status_code
        == 401
    )
    assert (
        client.post(
            "/auth/login",
            json={"username": "viewer", "password": "ResetPass123!"},
        ).status_code
        == 200
    )

    audit_payloads = _audit_payloads(session_factory)
    actions = [action for action, _payload in audit_payloads]
    assert actions == [
        "display_name_changed",
        "user_disabled",
        "user_enabled",
        "password_reset",
    ]
    forbidden_fragments = [
        "viewer",
        "Маус",
        "ResetPass123!",
        VIEWER_PASSWORD,
        "password_hash",
        "auth_version",
        "JWT",
        "cookie",
        "select ",
    ]
    for action, payload in audit_payloads:
        assert set(payload).issubset({"subject_user_id", "changed_fields", "result"})
        assert payload["subject_user_id"] == viewer_id
        payload_text = json.dumps(payload, ensure_ascii=False)
        for fragment in forbidden_fragments:
            assert fragment not in payload_text
        assert action in {
            "display_name_changed",
            "user_disabled",
            "user_enabled",
            "password_reset",
        }


def test_admin_self_password_reset_returns_exact_dto_and_invalidates_current_token(
    client, session_factory
):
    admin_token = _login(client)
    admin_headers = _headers(admin_token)
    admin_id = _user_id(session_factory, "admin")

    reset = client.post(
        f"/admin/users/{admin_id}/password-reset",
        headers=admin_headers,
        json={"new_password": "AdminReset123!"},
    )
    assert reset.status_code == 200, reset.text
    assert reset.json() == {
        "status": "password_reset",
        "subject_user_id": admin_id,
        "session_invalidated": True,
    }
    assert client.get("/auth/me", headers=admin_headers).status_code == 401
    assert client.post(
        "/auth/login",
        json={"username": "admin", "password": ADMIN_PASSWORD},
    ).status_code == 401
    assert client.post(
        "/auth/login",
        json={"username": "admin", "password": "AdminReset123!"},
    ).status_code == 200


def test_password_reset_hashes_before_sqlite_write_lock(client, session_factory, monkeypatch):
    from app.services import user_admin as user_admin_module

    admin_id = _user_id(session_factory, "admin")
    viewer_id = _user_id(session_factory, "viewer")
    calls: list[str] = []

    def fake_hash_password(password: str) -> str:
        calls.append("hash")
        assert "PreLockReset123!" == password
        return "$2b$12$abcdefghijklmnopqrstuuasOWC7UoDVRfLBBHG8DBSA4vi67BCEm"

    original_begin_immediate = user_admin_module.UserAdminService._begin_immediate

    def recording_begin_immediate(self):
        calls.append("begin")
        return original_begin_immediate(self)

    monkeypatch.setattr(user_admin_module, "hash_password", fake_hash_password)
    monkeypatch.setattr(
        user_admin_module.UserAdminService,
        "_begin_immediate",
        recording_begin_immediate,
    )

    with session_factory() as session:
        response = user_admin_module.UserAdminService(session).reset_password(
            actor_user_id=admin_id,
            subject_user_id=viewer_id,
            new_password="PreLockReset123!",
        )

    assert response.status == "password_reset"
    assert response.subject_user_id == viewer_id
    assert response.session_invalidated is True
    assert calls == ["hash", "begin"]


def test_self_disable_and_concurrent_admin_disable_preserve_enabled_admin(
    client, session_factory
):
    from app.services.user_admin import UserAdminError, UserAdminService

    admin_id = _user_id(session_factory, "admin")
    other_admin_id = _user_id(session_factory, "otheradmin")
    admin_headers = _headers(_login(client))

    self_disable = client.post(f"/admin/users/{admin_id}/disable", headers=admin_headers)
    assert self_disable.status_code == 409
    assert _safe_code(self_disable) == "self_disable_forbidden"

    disable_other = client.post(
        f"/admin/users/{other_admin_id}/disable",
        headers=admin_headers,
    )
    assert disable_other.status_code == 200, disable_other.text
    last_admin_self_disable = client.post(
        f"/admin/users/{admin_id}/disable",
        headers=admin_headers,
    )
    assert last_admin_self_disable.status_code == 409
    assert _safe_code(last_admin_self_disable) == "last_enabled_admin"

    enable_other = client.post(
        f"/admin/users/{other_admin_id}/enable",
        headers=admin_headers,
    )
    assert enable_other.status_code == 200, enable_other.text

    barrier = Barrier(2)

    def disable(actor_id: int, subject_id: int) -> int | str:
        with session_factory() as session:
            barrier.wait(timeout=5)
            try:
                UserAdminService(session).disable_user(
                    actor_user_id=actor_id,
                    subject_user_id=subject_id,
                )
                return "ok"
            except UserAdminError as exc:
                return exc.status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(
            pool.map(
                lambda pair: disable(*pair),
                [(admin_id, other_admin_id), (other_admin_id, admin_id)],
            )
        )

    assert results.count("ok") == 1
    assert any(result in {403, 409} for result in results)
    with session_factory() as session:
        enabled_admins = (
            session.query(User)
            .filter(User.is_admin.is_(True), User.is_enabled.is_(True))
            .count()
        )
    assert enabled_admins == 1


def test_invalid_inputs_are_fixed_safe_errors_and_patch_cannot_mutate_identity_or_role(
    client
):
    headers = _headers(_login(client))

    bad_username = client.post(
        "/admin/users",
        headers=headers,
        json={
            "username": "../Admin",
            "display_name": "Bad User",
            "password": "BadUserPass123!",
        },
    )
    assert bad_username.status_code == 422
    assert _safe_code(bad_username) == "username_invalid"
    assert "../Admin" not in bad_username.text

    weak_password = client.post(
        "/admin/users",
        headers=headers,
        json={
            "username": "weak-user",
            "display_name": "Weak User",
            "password": "Password1234",
        },
    )
    assert weak_password.status_code == 422
    assert _safe_code(weak_password) == "password_policy"
    assert "Password1234" not in weak_password.text

    oversized_password = client.post(
        "/admin/users",
        headers=headers,
        json={
            "username": "oversized-user",
            "display_name": "Oversized User",
            "password": "Aa1!" + "é" * 35,
        },
    )
    assert oversized_password.status_code == 422
    assert _safe_code(oversized_password) == "password_policy"

    admin_id = _login(client)
    current = client.get("/auth/me", headers=_headers(admin_id)).json()["id"]
    sentinel = "PlaintextSentinelSecret123!"
    malformed_password = client.post(
        f"/admin/users/{current}/password-reset",
        headers=headers,
        json={"new_password": {"secret": sentinel}},
    )
    assert malformed_password.status_code == 422
    assert _safe_code(malformed_password) == "password_policy"
    assert sentinel not in malformed_password.text
    assert "new_password" not in malformed_password.text

    extra_sentinel = client.post(
        "/admin/users",
        headers=headers,
        json={
            "username": "sentinel-user",
            "display_name": "Sentinel User",
            "password": "SentinelPass123!",
            "private_note": sentinel,
        },
    )
    assert extra_sentinel.status_code == 422
    assert _safe_code(extra_sentinel) == "invalid_state"
    assert sentinel not in extra_sentinel.text
    assert "private_note" not in extra_sentinel.text

    blocked_patch = client.patch(
        f"/admin/users/{current}",
        headers=headers,
        json={"username": "mutated", "is_admin": False, "display_name": "Still Admin"},
    )
    assert blocked_patch.status_code == 422
    assert _safe_code(blocked_patch) == "invalid_state"
    assert "mutated" not in blocked_patch.text
    assert "is_admin" not in blocked_patch.text

    bad_display = client.patch(
        f"/admin/users/{current}",
        headers=headers,
        json={"display_name": "Bad\x00Name"},
    )
    assert bad_display.status_code == 422
    assert _safe_code(bad_display) == "display_name_invalid"
    assert "Bad" not in bad_display.text


def test_admin_user_routes_are_app_db_only_and_do_not_touch_gnucash_sources(
    client, monkeypatch
):
    def fail_source(*args, **kwargs):
        raise AssertionError("GnuCash/source helper must not be called by admin-user API")

    monkeypatch.setattr("app.services.gnucash_book.piecash.open_book", fail_source)
    monkeypatch.setattr("app.services.book_preflight.run_book_health_probe", fail_source)
    monkeypatch.setattr("app.services.book_preflight._verify_sqlite_gnucash_schema", fail_source)
    monkeypatch.setattr("app.services.book_preflight.canonicalize_existing_book_path", fail_source)

    headers = _headers(_login(client))
    response = client.get("/admin/users", headers=headers)
    assert response.status_code == 200, response.text
    assert response.json()["total_count"] == 3

    create = client.post(
        "/admin/users",
        headers=headers,
        json={
            "username": "appdb-only",
            "display_name": "App DB Only",
            "password": "AppDbOnly123!",
        },
    )
    assert create.status_code == 201, create.text

def test_admin_users_limit_state_and_not_found_errors_are_bounded(client):
    headers = _headers(_login(client))

    bad_limit = client.get("/admin/users?limit=101", headers=headers)
    assert bad_limit.status_code == 422
    assert _safe_code(bad_limit) == "invalid_state"
    assert "input" not in bad_limit.text

    bad_state = client.get("/admin/users?state=archived", headers=headers)
    assert bad_state.status_code == 422
    assert _safe_code(bad_state) == "invalid_state"
    assert "archived" not in bad_state.text

    missing = client.get("/admin/users/999999", headers=headers)
    assert missing.status_code == 404
    assert _safe_code(missing) == "user_not_found"

    reset_missing = client.post(
        "/admin/users/999999/password-reset",
        headers=headers,
        json={"new_password": "ResetPass123!"},
    )
    assert reset_missing.status_code == 404
    assert _safe_code(reset_missing) == "user_not_found"


def test_admin_user_api_works_after_issue57_legacy_migration(tmp_path):
    db_path = tmp_path / "legacy-admin-users.db"
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    with engine.begin() as conn:
        conn.execute(
            text(
                "create table users ("
                "id integer primary key autoincrement, "
                "username varchar(128) not null unique, "
                "display_name varchar(256) not null, "
                "password_hash varchar(512) not null, "
                "is_admin boolean not null, "
                "created_at datetime not null)"
            )
        )
        conn.execute(
            text(
                "create table books ("
                "id integer primary key autoincrement, "
                "name varchar(256) not null, "
                "storage_type varchar(64) not null, "
                "uri_or_path varchar(1024) not null, "
                "base_currency varchar(16), "
                "is_default boolean not null, "
                "is_archived boolean not null, "
                "created_at datetime not null)"
            )
        )
        conn.execute(
            text(
                "create table user_book_access ("
                "user_id integer not null, "
                "book_id integer not null, "
                "role varchar(16) not null, "
                "primary key (user_id, book_id))"
            )
        )
        conn.execute(
            text(
                "create table audit_logs ("
                "id integer primary key autoincrement, "
                "user_id integer, "
                "book_id integer, "
                "action varchar(128) not null, "
                "payload_json text, "
                "created_at datetime not null)"
            )
        )
        conn.execute(
            text(
                "insert into users "
                "(id, username, display_name, password_hash, is_admin, created_at) "
                "values (1, 'Admin', 'Legacy Admin', :hash, 1, '2026-01-01 00:00:00.000000')"
            ),
            {"hash": hash_password(ADMIN_PASSWORD)},
        )

    from app.services.metadata_migrations import run_app_metadata_migrations

    settings = _settings(tmp_path)
    run_app_metadata_migrations(engine, settings)
    SessionLocal = sessionmaker(bind=engine)

    def override_get_db():
        with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_db] = override_get_db
    try:
        client = TestClient(app)
        headers = _headers(_login(client, "admin", ADMIN_PASSWORD))
        response = client.get("/admin/users", headers=headers)
        assert response.status_code == 200, response.text
        assert response.json()["items"][0]["username"] == "Admin"
        create = client.post(
            "/admin/users",
            headers=headers,
            json={
                "username": "migrated-new",
                "display_name": "Migrated New",
                "password": "MigratedNew123!",
            },
        )
        assert create.status_code == 201, create.text
    finally:
        app.dependency_overrides.clear()
        get_settings.cache_clear()
