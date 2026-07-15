"""Issue #57 B3 admin scoped book-access API and live revoke tests."""

from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from threading import Barrier

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.config import Settings, get_settings
from app.database import Base
from app.main import app
from app.models import AuditLog, Book, BookHealthSnapshot, User, UserBookAccess
from app.routers.auth import get_db
from app.services.auth import hash_password

ADMIN_PASSWORD = "AdminPass123!"
VIEWER_PASSWORD = "ViewerPass123!"
JWT_SECRET = "test-secret-key-for-admin-book-access-issue57-32-bytes"


def _settings(tmp_path: Path) -> Settings:
    return Settings(
        app_env="test",
        app_database_url=f"sqlite:///{tmp_path / 'book-access-app.db'}",
        jwt_secret=JWT_SECRET,
        jwt_token_expire_minutes=30,
        app_admin_username="admin",
        app_admin_password=ADMIN_PASSWORD,
        gnucash_book_allowed_roots=[str(tmp_path)],
    )


@pytest.fixture
def engine(tmp_path):
    engine = create_engine(
        f"sqlite:///{tmp_path / 'book-access.db'}",
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
        session.add_all([admin, viewer])
        session.flush()
        books = [
            Book(
                name="beta Book",
                storage_type="sqlite",
                uri_or_path=str(tmp_path / "beta.gnucash.sqlite"),
                base_currency="USD",
                is_default=False,
            ),
            Book(
                name="Alpha Book",
                storage_type="sqlite",
                uri_or_path=str(tmp_path / "alpha.gnucash.sqlite"),
                base_currency="USD",
                is_default=True,
            ),
            Book(
                name="disabled Book",
                storage_type="sqlite",
                uri_or_path=str(tmp_path / "disabled.gnucash.sqlite"),
                base_currency="USD",
                is_enabled=False,
            ),
            Book(
                name="archived Book",
                storage_type="sqlite",
                uri_or_path=str(tmp_path / "archived.gnucash.sqlite"),
                base_currency="USD",
                is_archived=True,
            ),
        ]
        session.add_all(books)
        session.flush()
        for book in books:
            session.add(
                BookHealthSnapshot(
                    book_id=book.id,
                    source_status="ready",
                    open_status="ready",
                    accounts_status="ready",
                    transactions_status="ready",
                    reports_status="ready",
                    safe_code="ready",
                )
            )
        session.add(UserBookAccess(user_id=viewer.id, book_id=books[2].id, role="owner"))
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


def _ids(session_factory) -> dict[str, int]:
    with session_factory() as session:
        users = {row.username: int(row.id) for row in session.query(User).all()}
        books = {row.name: int(row.id) for row in session.query(Book).all()}
    return {**users, **books}


def _audit_rows(session_factory) -> list[tuple[str, int | None, dict[str, object]]]:
    with session_factory() as session:
        rows = session.query(AuditLog).order_by(AuditLog.id).all()
        return [(row.action, row.book_id, json.loads(row.payload_json or "{}")) for row in rows]


def test_book_options_are_bounded_active_ordered_pathless_and_app_db_only(
    client, session_factory, engine, monkeypatch
):
    def fail_source(*args, **kwargs):  # pragma: no cover - regression guard
        raise AssertionError("admin book options must not touch GnuCash sources")

    monkeypatch.setattr("app.services.gnucash_book.piecash.open_book", fail_source)
    monkeypatch.setattr("app.services.book_preflight.run_book_health_probe", fail_source)
    admin_headers = _headers(_login(client))
    select_count = 0

    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        nonlocal select_count
        if statement.lstrip().lower().startswith("select"):
            select_count += 1

    event.listen(engine, "before_cursor_execute", before_cursor_execute)
    try:
        response = client.get(
            "/admin/book-access/books?limit=1&offset=1",
            headers=admin_headers,
        )
    finally:
        event.remove(engine, "before_cursor_execute", before_cursor_execute)

    assert response.status_code == 200, response.text
    data = response.json()
    assert data == {
        "items": [{"id": _ids(session_factory)["beta Book"], "name": "beta Book", "is_default": False}],
        "total_count": 2,
        "limit": 1,
        "offset": 1,
        "has_next": False,
    }
    assert "uri_or_path" not in response.text
    assert "health" not in response.text
    assert select_count <= 3


def test_book_options_empty_response_preserves_exact_bounded_shape(client, session_factory):
    with session_factory() as session:
        for book in session.query(Book).all():
            book.is_enabled = False
        session.commit()

    admin_headers = _headers(_login(client))
    response = client.get("/admin/book-access/books?limit=50&offset=0", headers=admin_headers)

    assert response.status_code == 200, response.text
    assert response.json() == {
        "items": [],
        "total_count": 0,
        "limit": 50,
        "offset": 0,
        "has_next": False,
    }


def test_admin_grants_updates_revokes_access_and_user_detail_counts_active_assignments(
    client, session_factory
):
    ids = _ids(session_factory)
    admin_headers = _headers(_login(client))
    viewer_id = ids["viewer"]
    alpha_id = ids["Alpha Book"]
    beta_id = ids["beta Book"]
    disabled_id = ids["disabled Book"]
    archived_id = ids["archived Book"]

    detail = client.get(f"/admin/users/{viewer_id}", headers=admin_headers)
    assert detail.status_code == 200
    assert detail.json()["assignment_count"] == 0
    assert detail.json()["assignments"] == []

    grant_beta = client.put(
        f"/admin/users/{viewer_id}/book-access/{beta_id}",
        headers=admin_headers,
        json={},
    )
    assert grant_beta.status_code == 200, grant_beta.text
    assert grant_beta.json() == {
        "book_id": beta_id,
        "book_name": "beta Book",
        "is_default": False,
        "role": "viewer",
    }

    grant_alpha = client.put(
        f"/admin/users/{viewer_id}/book-access/{alpha_id}",
        headers=admin_headers,
        json={"role": "owner"},
    )
    assert grant_alpha.status_code == 200, grant_alpha.text
    assert grant_alpha.json() == {
        "book_id": alpha_id,
        "book_name": "Alpha Book",
        "is_default": True,
        "role": "owner",
    }

    update_alpha = client.put(
        f"/admin/users/{viewer_id}/book-access/{alpha_id}",
        headers=admin_headers,
        json={"role": "editor"},
    )
    assert update_alpha.status_code == 200, update_alpha.text
    assert update_alpha.json()["role"] == "editor"

    idempotent_update = client.put(
        f"/admin/users/{viewer_id}/book-access/{alpha_id}",
        headers=admin_headers,
        json={"role": "editor"},
    )
    assert idempotent_update.status_code == 200

    for book_id in (disabled_id, archived_id, 999999):
        response = client.put(
            f"/admin/users/{viewer_id}/book-access/{book_id}",
            headers=admin_headers,
            json={"role": "viewer"},
        )
        assert response.status_code == 404
        assert _safe_code(response) == "book_not_found"

    detail = client.get(f"/admin/users/{viewer_id}", headers=admin_headers)
    assert detail.status_code == 200
    assert detail.json()["assignment_count"] == 2
    assert detail.json()["assignments"] == [
        {"book_id": alpha_id, "book_name": "Alpha Book", "is_default": True, "role": "editor"},
        {"book_id": beta_id, "book_name": "beta Book", "is_default": False, "role": "viewer"},
    ]

    revoke_alpha = client.delete(
        f"/admin/users/{viewer_id}/book-access/{alpha_id}",
        headers=admin_headers,
    )
    assert revoke_alpha.status_code == 204
    repeated_revoke = client.delete(
        f"/admin/users/{viewer_id}/book-access/{alpha_id}",
        headers=admin_headers,
    )
    assert repeated_revoke.status_code == 204

    detail = client.get(f"/admin/users/{viewer_id}", headers=admin_headers)
    assert detail.json()["assignment_count"] == 1
    assert detail.json()["assignments"] == [
        {"book_id": beta_id, "book_name": "beta Book", "is_default": False, "role": "viewer"}
    ]

    audit_rows = _audit_rows(session_factory)
    actions = [action for action, _book_id, _payload in audit_rows]
    assert actions == [
        "book_access_granted",
        "book_access_granted",
        "book_access_granted",
        "book_access_revoked",
    ]
    assert [book_id for _action, book_id, _payload in audit_rows] == [
        beta_id,
        alpha_id,
        alpha_id,
        alpha_id,
    ]
    for action, _book_id, payload in audit_rows:
        assert set(payload).issubset(
            {"subject_user_id", "role", "changed_fields", "result"}
        )
        assert payload["subject_user_id"] == viewer_id
        assert "book_id" not in payload
        assert "Alpha Book" not in json.dumps(payload)
        assert "beta Book" not in json.dumps(payload)
        assert action.startswith("book_access_")


def test_admin_book_access_audit_rejects_unallowlisted_actions_and_payload_book_id(
    client, session_factory,
):
    from app.services.user_admin import UserAdminService

    ids = _ids(session_factory)
    with session_factory() as session:
        service = UserAdminService(session)
        with pytest.raises(ValueError, match="audit_action_not_allowed"):
            service._audit_book_access(
                actor_user_id=ids["admin"],
                subject_user_id=ids["viewer"],
                book_id=ids["Alpha Book"],
                action="book_access_role_changed",
                changed_fields=["role"],
                result="changed",
                role="viewer",
            )
        with pytest.raises(ValueError, match="audit_payload_not_allowed"):
            service._audit_book_access(
                actor_user_id=ids["admin"],
                subject_user_id=ids["viewer"],
                book_id=ids["Alpha Book"],
                action="book_access_granted",
                changed_fields=["book_id"],
                result="granted",
                role="viewer",
            )


def test_admin_book_access_routes_require_admin(client, session_factory):
    ids = _ids(session_factory)
    viewer_headers = _headers(_login(client, "viewer", VIEWER_PASSWORD))
    viewer_id = ids["viewer"]
    beta_id = ids["beta Book"]

    responses = [
        client.get("/admin/book-access/books", headers=viewer_headers),
        client.put(
            f"/admin/users/{viewer_id}/book-access/{beta_id}",
            headers=viewer_headers,
            json={"role": "viewer"},
        ),
        client.delete(
            f"/admin/users/{viewer_id}/book-access/{beta_id}",
            headers=viewer_headers,
        ),
    ]
    for response in responses:
        assert response.status_code == 403
        assert _safe_code(response) == "admin_required"


def test_live_revoke_blocks_next_read_accounts_transactions_and_reports_before_source_open(
    client, session_factory, monkeypatch
):
    ids = _ids(session_factory)
    admin_headers = _headers(_login(client))
    viewer_headers = _headers(_login(client, "viewer", VIEWER_PASSWORD))
    viewer_id = ids["viewer"]
    beta_id = ids["beta Book"]

    grant = client.put(
        f"/admin/users/{viewer_id}/book-access/{beta_id}",
        headers=admin_headers,
        json={"role": "viewer"},
    )
    assert grant.status_code == 200

    calls: list[int] = []

    class ProbeService:
        def __init__(self, book):
            calls.append(int(book.id))

        def list_accounts(self):
            return []

    monkeypatch.setattr("app.routers.books.account_service_for", ProbeService)
    allowed = client.get(f"/books/{beta_id}/accounts", headers=viewer_headers)
    assert allowed.status_code == 200
    assert calls == [beta_id]

    revoke = client.delete(
        f"/admin/users/{viewer_id}/book-access/{beta_id}",
        headers=admin_headers,
    )
    assert revoke.status_code == 204
    calls.clear()
    def fail_source_open(*args, **kwargs):  # pragma: no cover - regression guard
        raise AssertionError("revoked read request must stop before source service open")

    monkeypatch.setattr("app.routers.books.account_service_for", fail_source_open)
    monkeypatch.setattr("app.routers.transactions.transaction_service_for", fail_source_open)
    monkeypatch.setattr("app.routers.reports.transaction_service_for", fail_source_open)
    denied_responses = [
        client.get(f"/books/{beta_id}/accounts", headers=viewer_headers),
        client.get(f"/books/{beta_id}/transactions", headers=viewer_headers),
        client.get(
            f"/books/{beta_id}/reports?date_from=2026-01-01&date_to=2026-01-31",
            headers=viewer_headers,
        ),
    ]
    for denied in denied_responses:
        assert denied.status_code == 403
        assert denied.json()["detail"] == "Book access denied"
    assert calls == []


def test_disabled_access_is_excluded_from_user_switcher_listing(client, session_factory):
    ids = _ids(session_factory)
    viewer_headers = _headers(_login(client, "viewer", VIEWER_PASSWORD))
    default_id = ids["Alpha Book"]
    disabled_id = ids["disabled Book"]
    response = client.get("/books", headers=viewer_headers)
    assert response.status_code == 200
    visible_ids = {item["id"] for item in response.json()}
    assert visible_ids == set()
    assert disabled_id not in visible_ids
    assert default_id not in visible_ids


def test_concurrent_duplicate_grants_converge_to_single_assignment(client, session_factory):
    with session_factory() as session:
        admin = session.query(User).filter(User.username == "admin").one()
        viewer = session.query(User).filter(User.username == "viewer").one()
        book = session.query(Book).filter(Book.name == "beta Book").one()
        admin_id = int(admin.id)
        viewer_id = int(viewer.id)
        book_id = int(book.id)

    from app.services.user_admin import UserAdminService

    barrier = Barrier(2)

    def grant(role: str) -> str:
        with session_factory() as session:
            barrier.wait(timeout=5)
            assignment = UserAdminService(session).set_book_access(
                actor_user_id=admin_id,
                subject_user_id=viewer_id,
                book_id=book_id,
                role=role,
            )
            return assignment.role

    with ThreadPoolExecutor(max_workers=2) as pool:
        roles = list(pool.map(grant, ["viewer", "editor"]))

    assert set(roles).issubset({"viewer", "editor"})
    with session_factory() as session:
        rows = session.query(UserBookAccess).filter_by(user_id=viewer_id, book_id=book_id).all()
        assert len(rows) == 1
        assert rows[0].role in {"viewer", "editor"}
