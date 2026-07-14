"""Issue #56 B2 token-bound book lifecycle and cached health tests."""

from __future__ import annotations

import hashlib
import os
import shutil
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import Settings, get_settings
from app.database import Base
from app.main import app
from app.models import Book, BookHealthSnapshot, User, UserBookAccess
from app.routers.auth import get_db
from app.services.auth import hash_password
from app.services.book_preflight import canonical_path_hash, decode_preflight_token
from app.services.metadata_migrations import run_app_metadata_migrations

FIXTURE_BOOK = Path(__file__).parent / "fixtures" / "test-book.gnucash.sqlite"
JWT_SECRET = "test-secret-key-for-issue56-b2-lifecycle-32-bytes"


def _copy_fixture(target: Path) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(FIXTURE_BOOK, target)
    return target


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@pytest.fixture
def api_context(tmp_path):
    allowed_root = tmp_path / "allowed-root"
    allowed_root.mkdir()
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    settings = Settings(
        app_env="test",
        app_database_url="sqlite:///:memory:",
        gnucash_default_book_path="",
        gnucash_book_allowed_roots=[str(allowed_root)],
        jwt_secret=JWT_SECRET,
        jwt_token_expire_minutes=30,
        app_admin_username="admin",
        app_admin_password="testpassword123",
    )

    def override_get_db():
        with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_db] = override_get_db

    with SessionLocal() as session:
        session.add_all(
            [
                User(
                    username="admin",
                    display_name="Admin",
                    password_hash=hash_password("testpassword123"),
                    is_admin=True,
                ),
                User(
                    username="viewer",
                    display_name="Viewer",
                    password_hash=hash_password("viewerpass"),
                    is_admin=False,
                ),
            ]
        )
        session.commit()

    client = TestClient(app)
    admin_login = client.post(
        "/auth/login",
        json={"username": "admin", "password": "testpassword123"},
    )
    viewer_login = client.post(
        "/auth/login",
        json={"username": "viewer", "password": "viewerpass"},
    )
    assert admin_login.status_code == 200
    assert viewer_login.status_code == 200

    yield {
        "client": client,
        "engine": engine,
        "session_factory": SessionLocal,
        "settings": settings,
        "allowed_root": allowed_root,
        "admin_headers": {"Authorization": f"Bearer {admin_login.json()['access_token']}"},
        "viewer_headers": {"Authorization": f"Bearer {viewer_login.json()['access_token']}"},
    }

    app.dependency_overrides.clear()
    get_settings.cache_clear()
    engine.dispose()


def _book_payload(book_path: Path, **overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "name": "Lifecycle Copy",
        "storage_type": "sqlite",
        "uri_or_path": str(book_path),
        "base_currency": "USD",
        "make_default": False,
    }
    payload.update(overrides)
    return payload


def _preflight_register_payload(
    client: TestClient,
    headers: dict[str, str],
    book_path: Path,
    **overrides: Any,
) -> dict[str, Any]:
    payload = _book_payload(book_path, **overrides)
    preflight = client.post("/books/preflight", headers=headers, json=payload)
    assert preflight.status_code == 200
    payload["preflight_token"] = preflight.json()["preflight_token"]
    return payload


def _register_book(
    api_context,
    book_path: Path,
    **overrides: Any,
):
    payload = _preflight_register_payload(
        api_context["client"], api_context["admin_headers"], book_path, **overrides
    )
    response = api_context["client"].post(
        "/books", headers=api_context["admin_headers"], json=payload
    )
    assert response.status_code == 201
    return response


def _add_access(session, username: str, book_id: int, role: str = "owner") -> None:
    user = session.query(User).filter(User.username == username).one()
    session.add(UserBookAccess(user_id=user.id, book_id=book_id, role=role))


def _add_health_snapshot(session, book_id: int, safe_code: str = "ready", **overrides: Any) -> None:
    fields = {
        "book_id": book_id,
        "source_status": "ready" if safe_code == "ready" else safe_code,
        "open_status": "ready" if safe_code == "ready" else "not_checked",
        "accounts_status": "ready" if safe_code == "ready" else "not_checked",
        "transactions_status": "ready" if safe_code == "ready" else "not_checked",
        "reports_status": "ready" if safe_code == "ready" else "not_checked",
        "safe_code": safe_code,
    }
    fields.update(overrides)
    session.add(BookHealthSnapshot(**fields))


def test_books_list_is_empty_before_registration(api_context):
    response = api_context["client"].get("/books", headers=api_context["admin_headers"])

    assert response.status_code == 200
    assert response.json() == []


def test_register_requires_fresh_matching_token_and_exactly_one_readonly_open(api_context, monkeypatch):
    from app.services import book_preflight

    book_path = _copy_fixture(api_context["allowed_root"] / "healthy-register.gnucash.sqlite")
    payload = _preflight_register_payload(
        api_context["client"], api_context["admin_headers"], book_path, make_default=True
    )
    before_hash = _sha256(book_path)
    before_stat = book_path.stat()
    before_entries = sorted(item.name for item in book_path.parent.iterdir())

    real_open_book = book_preflight.piecash.open_book
    open_calls: list[dict[str, Any]] = []

    def counting_open_book(*args, **kwargs):
        open_calls.append({"args": args, "kwargs": kwargs})
        return real_open_book(*args, **kwargs)

    monkeypatch.setattr(book_preflight.piecash, "open_book", counting_open_book)
    response = api_context["client"].post(
        "/books", headers=api_context["admin_headers"], json=payload
    )

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Lifecycle Copy"
    assert data["base_currency"] == "USD"
    assert data["is_default"] is True
    assert data["status"] == "available"
    assert data["health"]["safe_code"] == "ready"
    assert "uri_or_path" not in data
    assert open_calls == [
        {"args": (str(book_path.resolve(strict=True)),), "kwargs": {"readonly": True}}
    ]
    assert _sha256(book_path) == before_hash
    assert book_path.stat().st_size == before_stat.st_size
    assert book_path.stat().st_mtime_ns == before_stat.st_mtime_ns
    assert sorted(item.name for item in book_path.parent.iterdir()) == before_entries
    assert not (book_path.parent / f"{book_path.name}-journal").exists()
    assert not (book_path.parent / f"{book_path.name}-wal").exists()

    with api_context["session_factory"]() as session:
        book = session.query(Book).filter(Book.id == data["id"]).one()
        assert book.canonical_path_hash == canonical_path_hash(str(book_path.resolve(strict=True)))
        access = session.query(UserBookAccess).filter(UserBookAccess.book_id == book.id).one()
        assert access.role == "owner"
        snapshot = session.query(BookHealthSnapshot).filter_by(book_id=book.id).one()
        assert snapshot.safe_code == "ready"
        assert snapshot.checked_at is not None
        assert snapshot.last_successful_at == snapshot.checked_at


def _tamper_token(payload: dict[str, Any]) -> None:
    payload_part, signature_part = payload["preflight_token"].split(".", 1)
    replacement = "A" if signature_part[0] != "A" else "B"
    payload["preflight_token"] = f"{payload_part}.{replacement}{signature_part[1:]}"


@pytest.mark.parametrize(
    ("case", "mutate_payload", "expected_status", "expected_code"),
    [
        ("missing", lambda payload: payload.pop("preflight_token"), 422, "missing_preflight_token"),
        ("tampered", _tamper_token, 422, "invalid_preflight_token"),
        ("request_mismatch", lambda payload: payload.__setitem__("name", "Changed Name"), 422, "preflight_request_mismatch"),
    ],
)
def test_register_rejects_missing_tampered_and_request_mismatched_tokens(
    api_context, case, mutate_payload, expected_status, expected_code
):
    book_path = _copy_fixture(api_context["allowed_root"] / f"{case}.gnucash.sqlite")
    payload = _preflight_register_payload(
        api_context["client"], api_context["admin_headers"], book_path
    )
    mutate_payload(payload)

    response = api_context["client"].post(
        "/books", headers=api_context["admin_headers"], json=payload
    )

    assert response.status_code == expected_status
    assert response.json()["detail"]["code"] == expected_code
    assert str(book_path) not in response.text
    assert book_path.name not in response.text
    with api_context["session_factory"]() as session:
        assert session.query(Book).count() == 0


def test_register_rejects_expired_token(api_context, monkeypatch):
    book_path = _copy_fixture(api_context["allowed_root"] / "expired.gnucash.sqlite")
    payload = _preflight_register_payload(
        api_context["client"], api_context["admin_headers"], book_path
    )
    token_payload = decode_preflight_token(payload["preflight_token"], api_context["settings"])
    assert token_payload is not None
    monkeypatch.setattr(
        "app.services.book_preflight.time.time",
        lambda: int(token_payload["exp"]) + 1,
    )

    response = api_context["client"].post(
        "/books", headers=api_context["admin_headers"], json=payload
    )

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "invalid_preflight_token"
    assert str(book_path) not in response.text
    assert book_path.name not in response.text


def test_register_rejects_changed_source_identity_after_preflight(api_context):
    book_path = _copy_fixture(api_context["allowed_root"] / "changed-source.gnucash.sqlite")
    payload = _preflight_register_payload(
        api_context["client"], api_context["admin_headers"], book_path
    )
    os.utime(book_path, None)

    response = api_context["client"].post(
        "/books", headers=api_context["admin_headers"], json=payload
    )

    assert response.status_code == 409
    assert response.json()["detail"]["code"] == "preflight_source_mismatch"
    assert str(book_path) not in response.text
    assert book_path.name not in response.text


def test_duplicate_canonical_path_precheck_and_db_race_use_fixed_409(api_context, monkeypatch):
    first_path = _copy_fixture(api_context["allowed_root"] / "duplicate-source.gnucash.sqlite")
    first = _register_book(api_context, first_path)
    duplicate_payload = _preflight_register_payload(
        api_context["client"], api_context["admin_headers"], first_path, name="Same Source Again"
    )

    duplicate = api_context["client"].post(
        "/books", headers=api_context["admin_headers"], json=duplicate_payload
    )

    assert first.status_code == 201
    assert duplicate.status_code == 409
    assert duplicate.json()["detail"]["code"] == "duplicate_canonical_path"

    race_path = _copy_fixture(api_context["allowed_root"] / "race-source.gnucash.sqlite")
    race_payload = _preflight_register_payload(
        api_context["client"], api_context["admin_headers"], race_path, name="Race Source"
    )

    def insert_racing_row(session, canonical_hash: str) -> None:
        session.add(
            Book(
                name="Racing row",
                storage_type="sqlite",
                uri_or_path=str(race_path),
                canonical_path=str(race_path.resolve(strict=True)),
                canonical_path_hash=canonical_hash,
                base_currency="USD",
                is_archived=False,
                is_enabled=True,
            )
        )
        session.flush()

    monkeypatch.setattr("app.routers.books._reject_duplicate_canonical_registration", insert_racing_row)
    race = api_context["client"].post(
        "/books", headers=api_context["admin_headers"], json=race_payload
    )

    assert race.status_code == 409
    assert race.json()["detail"]["code"] == "duplicate_canonical_path"


def test_duplicate_display_names_are_allowed_when_canonical_sources_differ(api_context):
    first_path = _copy_fixture(api_context["allowed_root"] / "same-name-one.gnucash.sqlite")
    second_path = _copy_fixture(api_context["allowed_root"] / "same-name-two.gnucash.sqlite")

    first = _register_book(api_context, first_path, name="Same Display Name")
    second = _register_book(api_context, second_path, name="Same Display Name")

    assert first.status_code == 201
    assert second.status_code == 201
    assert first.json()["id"] != second.json()["id"]
    assert first.json()["name"] == second.json()["name"] == "Same Display Name"


def test_list_detail_and_health_use_only_cached_health_and_never_probe_source(
    api_context, monkeypatch
):
    source_probe_calls: list[str] = []

    def forbidden_source_probe(name: str):
        def fail(*args, **kwargs):  # pragma: no cover - fails only on regression
            source_probe_calls.append(name)
            raise AssertionError(f"list/detail/health must not touch source helper {name}")

        return fail

    monkeypatch.setattr(
        "app.routers.books._legacy_uncached_storage_status_for",
        forbidden_source_probe("legacy_uncached_storage_status"),
    )
    monkeypatch.setattr(
        "app.routers.books._local_sqlite_gnucash_shape_is_valid",
        forbidden_source_probe("local_sqlite_shape_is_valid"),
    )
    monkeypatch.setattr(
        "app.routers.books._sqlite_gnucash_shape_error",
        forbidden_source_probe("sqlite_gnucash_shape_error"),
    )
    monkeypatch.setattr(
        "app.routers.books.Path",
        forbidden_source_probe("path_constructor"),
    )
    monkeypatch.setattr(
        "app.routers.books.sqlite3.connect",
        forbidden_source_probe("sqlite_connect"),
    )
    monkeypatch.setattr(
        "app.routers.books.run_book_health_probe",
        forbidden_source_probe("router_health_probe"),
    )
    monkeypatch.setattr(
        "app.services.book_preflight.inspect_source_file",
        forbidden_source_probe("inspect_source_file"),
    )
    monkeypatch.setattr(
        "app.services.book_preflight._verify_sqlite_gnucash_schema",
        forbidden_source_probe("verify_sqlite_schema"),
    )
    monkeypatch.setattr(
        "app.services.book_preflight._open_piecash_readonly_once",
        forbidden_source_probe("piecash_readonly_open"),
    )
    monkeypatch.setattr(
        "app.services.book_preflight.run_book_health_probe",
        forbidden_source_probe("service_health_probe"),
    )
    monkeypatch.setattr(
        "app.services.book_preflight.piecash.open_book",
        forbidden_source_probe("piecash_open_book"),
    )

    with api_context["session_factory"]() as session:
        ready = Book(
            name="Cached Ready",
            storage_type="sqlite",
            uri_or_path=str(api_context["allowed_root"] / "ready-private.gnucash.sqlite"),
            base_currency="USD",
        )
        malformed = Book(
            name="Malformed Cached",
            storage_type="sqlite",
            uri_or_path=str(api_context["allowed_root"] / "malformed-private.gnucash.sqlite"),
            base_currency="USD",
        )
        missing_snapshot = Book(
            name="Missing Snapshot",
            storage_type="sqlite",
            uri_or_path=str(api_context["allowed_root"] / "missing-snapshot-private.gnucash.sqlite"),
            base_currency="USD",
        )
        session.add_all([ready, malformed, missing_snapshot])
        session.flush()
        _add_access(session, "admin", ready.id)
        _add_access(session, "admin", malformed.id)
        _add_access(session, "admin", missing_snapshot.id)
        _add_health_snapshot(session, ready.id, "ready")
        _add_health_snapshot(
            session,
            malformed.id,
            "ready",
            source_status="",
            open_status="ready",
            accounts_status="ready",
            transactions_status="ready",
            reports_status="ready",
        )
        ready_id = ready.id
        malformed_id = malformed.id
        missing_snapshot_id = missing_snapshot.id
        session.commit()

    listing = api_context["client"].get("/books", headers=api_context["admin_headers"])
    detail = api_context["client"].get(
        f"/books/{missing_snapshot_id}", headers=api_context["admin_headers"]
    )
    health = api_context["client"].get(
        f"/books/{malformed_id}/health", headers=api_context["admin_headers"]
    )

    assert listing.status_code == 200
    assert detail.status_code == 200
    by_id = {item["id"]: item for item in listing.json()}
    assert by_id[ready_id]["status"] == "available"
    assert by_id[ready_id]["can_open_read_only_views"] is True
    assert by_id[malformed_id]["status"] == "not_checked"
    assert by_id[malformed_id]["health"]["safe_code"] == "not_checked"
    assert by_id[malformed_id]["can_open_read_only_views"] is True
    assert by_id[missing_snapshot_id]["status"] == "not_checked"
    assert by_id[missing_snapshot_id]["health"]["safe_code"] == "not_checked"
    assert by_id[missing_snapshot_id]["can_open_read_only_views"] is True
    assert detail.json()["status"] == "not_checked"
    assert detail.json()["health"]["safe_code"] == "not_checked"
    assert detail.json()["can_open_read_only_views"] is True
    assert health.status_code == 200
    assert health.json()["safe_code"] == "not_checked"
    assert source_probe_calls == []
    for forbidden in (
        "ready-private.gnucash.sqlite",
        "malformed-private.gnucash.sqlite",
        "missing-snapshot-private.gnucash.sqlite",
    ):
        assert forbidden not in listing.text


def _request_with_app_db_statement_count(api_context, method: str, path: str):
    statements: list[str] = []

    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        statements.append(str(statement))

    event.listen(api_context["engine"], "before_cursor_execute", before_cursor_execute)
    try:
        response = api_context["client"].request(
            method,
            path,
            headers=api_context["admin_headers"],
        )
    finally:
        event.remove(api_context["engine"], "before_cursor_execute", before_cursor_execute)
    return response, len(statements)


def test_cached_metadata_routes_have_bounded_app_db_query_count_independent_of_book_count(
    api_context, monkeypatch
):
    def forbidden_source_probe(*args, **kwargs):  # pragma: no cover - regression guard
        raise AssertionError("cached metadata route must not probe GnuCash source")

    monkeypatch.setattr("app.routers.books.run_book_health_probe", forbidden_source_probe)
    monkeypatch.setattr("app.services.book_preflight.piecash.open_book", forbidden_source_probe)

    with api_context["session_factory"]() as session:
        admin = session.query(User).filter(User.username == "admin").one()
        first_book_id: int | None = None
        for index in range(6):
            book = Book()
            book.name = f"Cached Book {index}"
            book.storage_type = "sqlite"
            book.uri_or_path = str(api_context["allowed_root"] / f"private-{index}.gnucash.sqlite")
            book.base_currency = "USD"
            book.is_enabled = True
            session.add(book)
            session.flush()
            if first_book_id is None:
                first_book_id = int(book.id)
            access = UserBookAccess()
            access.user_id = admin.id
            access.book_id = book.id
            access.role = "owner"
            session.add(access)
            _add_health_snapshot(session, book.id, "ready")
        session.commit()
    assert first_book_id is not None

    listing, list_statements = _request_with_app_db_statement_count(api_context, "GET", "/books")
    detail, detail_statements = _request_with_app_db_statement_count(
        api_context, "GET", f"/books/{first_book_id}"
    )
    health, health_statements = _request_with_app_db_statement_count(
        api_context, "GET", f"/books/{first_book_id}/health"
    )

    assert listing.status_code == 200
    assert len(listing.json()) == 6
    assert detail.status_code == 200
    assert health.status_code == 200
    assert list_statements <= 2
    assert detail_statements <= 2
    assert health_statements <= 2


def test_patch_default_disable_enable_and_soft_unregister_are_metadata_only(api_context, monkeypatch):
    book_path = _copy_fixture(api_context["allowed_root"] / "lifecycle-metadata.gnucash.sqlite")
    before_hash = _sha256(book_path)
    registered = _register_book(api_context, book_path, make_default=True)
    book_id = registered.json()["id"]

    patch_response = api_context["client"].patch(
        f"/books/{book_id}",
        headers=api_context["admin_headers"],
        json={"name": "Renamed Lifecycle", "base_currency": "eur", "uri_or_path": "/private/ignored"},
    )
    assert patch_response.status_code == 200
    assert patch_response.json()["name"] == "Renamed Lifecycle"
    assert patch_response.json()["base_currency"] == "EUR"
    assert "/private/ignored" not in patch_response.text

    def forbidden_probe(*args, **kwargs):  # pragma: no cover - fails only on regression
        raise AssertionError("disable must not open or probe the source")

    monkeypatch.setattr("app.routers.books.run_book_health_probe", forbidden_probe)
    disabled = api_context["client"].post(
        f"/books/{book_id}/disable", headers=api_context["admin_headers"]
    )
    assert disabled.status_code == 200
    assert disabled.json()["is_enabled"] is False
    assert disabled.json()["is_default"] is False
    blocked = api_context["client"].get(
        f"/books/{book_id}/accounts", headers=api_context["admin_headers"]
    )
    assert blocked.status_code == 503
    assert "disabled" in blocked.json()["detail"]

    monkeypatch.undo()
    enable_preflight_payload = _book_payload(
        book_path,
        name="Renamed Lifecycle",
        base_currency="EUR",
        make_default=True,
    )
    enable_preflight = api_context["client"].post(
        "/books/preflight", headers=api_context["admin_headers"], json=enable_preflight_payload
    )
    assert enable_preflight.status_code == 200
    enabled = api_context["client"].post(
        f"/books/{book_id}/enable",
        headers=api_context["admin_headers"],
        json={"preflight_token": enable_preflight.json()["preflight_token"], "make_default": True},
    )
    assert enabled.status_code == 200
    assert enabled.json()["is_enabled"] is True
    assert enabled.json()["is_default"] is True

    delete_response = api_context["client"].delete(
        f"/books/{book_id}", headers=api_context["admin_headers"]
    )
    assert delete_response.status_code == 200
    assert delete_response.json() == {
        "id": book_id,
        "removed_from_registry": True,
        "underlying_file_deleted": False,
    }
    assert book_path.exists()
    assert _sha256(book_path) == before_hash
    with api_context["session_factory"]() as session:
        book = session.query(Book).filter(Book.id == book_id).one()
        assert book.uri_or_path == str(book_path)
        assert book.is_archived is True
        assert book.is_enabled is False
        assert book.is_default is False


def test_lifecycle_routes_require_admin_for_non_admin_viewer(api_context):
    book_path = _copy_fixture(api_context["allowed_root"] / "admin-only.gnucash.sqlite")
    registered = _register_book(api_context, book_path)
    book_id = registered.json()["id"]
    with api_context["session_factory"]() as session:
        _add_access(session, "viewer", book_id, "viewer")
        session.commit()

    forbidden = [
        api_context["client"].patch(
            f"/books/{book_id}", headers=api_context["viewer_headers"], json={"name": "Nope"}
        ),
        api_context["client"].post(
            f"/books/{book_id}/health/recheck", headers=api_context["viewer_headers"]
        ),
        api_context["client"].post(
            f"/books/{book_id}/disable", headers=api_context["viewer_headers"]
        ),
        api_context["client"].post(
            f"/books/{book_id}/enable",
            headers=api_context["viewer_headers"],
            json={"preflight_token": "not-a-real-token"},
        ),
        api_context["client"].delete(
            f"/books/{book_id}", headers=api_context["viewer_headers"]
        ),
    ]

    for response in forbidden:
        assert response.status_code == 403
        assert response.json()["detail"] == "Admin privileges are required for book registry management."


def test_recheck_failure_preserves_last_successful_and_blocks_known_unavailable_routes(api_context):
    book_path = _copy_fixture(api_context["allowed_root"] / "recheck-source.gnucash.sqlite")
    registered = _register_book(api_context, book_path)
    book_id = registered.json()["id"]
    with api_context["session_factory"]() as session:
        before_snapshot = session.query(BookHealthSnapshot).filter_by(book_id=book_id).one()
        last_successful = before_snapshot.last_successful_at
        assert last_successful is not None

    book_path.unlink()
    recheck = api_context["client"].post(
        f"/books/{book_id}/health/recheck", headers=api_context["admin_headers"]
    )
    listing = api_context["client"].get("/books", headers=api_context["admin_headers"])
    blocked = api_context["client"].get(
        f"/books/{book_id}/transactions", headers=api_context["admin_headers"]
    )

    assert recheck.status_code == 200
    assert recheck.json()["safe_code"] == "missing_file"
    assert recheck.json()["last_successful_at"] is not None
    assert str(book_path) not in recheck.text
    assert book_path.name not in recheck.text
    assert blocked.status_code == 503
    assert blocked.json()["detail"] == "Configured GnuCash book storage is unavailable from this runtime."
    listed = next(item for item in listing.json() if item["id"] == book_id)
    assert listed["status"] == "missing_file"
    assert listed["can_open_read_only_views"] is False
    with api_context["session_factory"]() as session:
        after_snapshot = session.query(BookHealthSnapshot).filter_by(book_id=book_id).one()
        assert after_snapshot.checked_at is not None
        assert after_snapshot.last_successful_at == last_successful


def test_metadata_migration_adds_idempotent_health_last_successful_for_legacy_rows(tmp_path):
    db_path = tmp_path / "legacy-app.db"
    engine = create_engine(f"sqlite:///{db_path}")
    with engine.begin() as conn:
        conn.execute(
            text(
                "create table books ("
                "id integer primary key, "
                "name varchar(256) not null, "
                "storage_type varchar(64) not null, "
                "uri_or_path varchar(1024) not null, "
                "base_currency varchar(16), "
                "is_default boolean not null default 0, "
                "is_archived boolean not null default 0, "
                "created_at datetime not null)"
            )
        )
        conn.execute(
            text(
                "insert into books (id, name, storage_type, uri_or_path, base_currency, is_default, is_archived, created_at) "
                "values (1, 'Legacy', 'sqlite', '', 'USD', 1, 0, '2026-01-01T00:00:00+00:00')"
            )
        )
    settings = Settings(
        app_env="test",
        app_database_url=f"sqlite:///{db_path}",
        gnucash_book_allowed_roots=[str(tmp_path)],
        jwt_secret=JWT_SECRET,
    )

    run_app_metadata_migrations(engine, settings)
    run_app_metadata_migrations(engine, settings)

    with engine.begin() as conn:
        health_columns = {row[1] for row in conn.execute(text("pragma table_info(book_health_snapshots)"))}
        book_columns = {row[1] for row in conn.execute(text("pragma table_info(books)"))}
        row = conn.execute(text("select safe_code, last_successful_at from book_health_snapshots where book_id = 1")).one()
        enabled = conn.execute(text("select is_enabled from books where id = 1")).scalar_one()

    assert {"canonical_path", "canonical_path_hash", "is_enabled", "updated_at"}.issubset(book_columns)
    assert "last_successful_at" in health_columns
    assert row.safe_code == "not_checked"
    assert row.last_successful_at is None
    assert enabled == 0
    engine.dispose()
