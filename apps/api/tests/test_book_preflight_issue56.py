"""Issue #56 backend preflight and source-safety foundation tests."""

from __future__ import annotations

import gzip
import hashlib
import json
import os
import shutil
from pathlib import Path
from typing import Any
from urllib.parse import unquote

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import Settings, get_settings
from app.database import Base
from app.main import app
from app.models import Book, BookHealthSnapshot, User, UserBookAccess
from app.routers.auth import get_db
from app.services.auth import hash_password
from app.services.book_preflight import canonical_path_hash, decode_preflight_token

FIXTURE_BOOK = Path(__file__).parent / "fixtures" / "test-book.gnucash.sqlite"
JWT_SECRET = "test-secret-key-for-issue56-preflight-32-bytes"


def _copy_fixture(target: Path) -> Path:
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(FIXTURE_BOOK, target)
    return target


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _sqlite_database_path(database: object) -> Path:
    text = str(database)
    if text.startswith("file:"):
        text = text[5:].split("?", 1)[0]
        text = unquote(text)
    return Path(text)


def _path_resolves_to(candidate: object, expected: Path) -> bool:
    try:
        return Path(str(candidate)).resolve(strict=True) == expected.resolve(strict=True)
    except OSError:
        return False


def _same_inode(left: os.stat_result, right: os.stat_result) -> bool:
    return int(left.st_dev) == int(right.st_dev) and int(left.st_ino) == int(right.st_ino)


def _fd_targets_containing(needle: str) -> list[str]:
    proc_fd = Path("/proc/self/fd")
    if not proc_fd.exists():
        pytest.skip("/proc/self/fd is required for fd leak inspection")
    matches: list[str] = []
    for entry in proc_fd.iterdir():
        try:
            target = os.readlink(entry)
        except OSError:
            continue
        if needle in target:
            matches.append(target)
    return sorted(matches)


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

    context = {
        "client": client,
        "session_factory": SessionLocal,
        "settings": settings,
        "allowed_root": allowed_root,
        "admin_headers": {"Authorization": f"Bearer {admin_login.json()['access_token']}"},
        "viewer_headers": {"Authorization": f"Bearer {viewer_login.json()['access_token']}"},
    }
    yield context

    app.dependency_overrides.clear()
    get_settings.cache_clear()
    engine.dispose()


def _preflight_payload(book_path: Path, **overrides: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "name": "Synthetic preflight book",
        "storage_type": "sqlite",
        "uri_or_path": str(book_path),
        "base_currency": "USD",
        "make_default": False,
    }
    payload.update(overrides)
    return payload


def _post_preflight(api_context, book_path: Path | str, **overrides: Any):
    path = Path(book_path) if not isinstance(book_path, str) else book_path
    return api_context["client"].post(
        "/books/preflight",
        headers=api_context["admin_headers"],
        json=_preflight_payload(path, **overrides),
    )


def test_preflight_requires_admin_and_never_registers_for_viewer(api_context):
    book_path = _copy_fixture(api_context["allowed_root"] / "viewer-attempt.gnucash.sqlite")

    no_auth = api_context["client"].post("/books/preflight", json=_preflight_payload(book_path))
    viewer = api_context["client"].post(
        "/books/preflight",
        headers=api_context["viewer_headers"],
        json=_preflight_payload(book_path),
    )

    assert no_auth.status_code == 401
    assert viewer.status_code == 403
    assert viewer.json()["detail"] == "Admin privileges are required for book registry management."
    with api_context["session_factory"]() as session:
        assert session.query(Book).count() == 0
        assert session.query(UserBookAccess).count() == 0
        assert session.query(BookHealthSnapshot).count() == 0


def test_preflight_success_is_typed_path_safe_and_has_no_metadata_or_source_side_effects(api_context):
    book_path = _copy_fixture(api_context["allowed_root"] / "content-first.no-extension")
    before_hash = _sha256(book_path)
    before_mtime = book_path.stat().st_mtime_ns
    before_entries = sorted(item.name for item in book_path.parent.iterdir())

    first = _post_preflight(api_context, book_path)
    second = _post_preflight(api_context, book_path)

    assert first.status_code == 200
    assert second.status_code == 200
    data = first.json()
    assert data["status"] == "ready"
    assert data["format"] == "gnucash_sqlite"
    assert data["safe_code"] == "ready"
    assert data["registration_status"]["status"] == "available"
    assert data["source_status"]["status"] == "ready"
    assert data["open_status"]["status"] == "ready"
    assert data["accounts"]["status"] in {"ready", "empty"}
    assert data["transactions"]["status"] in {"ready", "empty"}
    assert data["reports"]["status"] == "ready"
    assert data["capabilities"] == {
        "read_only": True,
        "can_register_metadata": True,
        "can_open_accounts": True,
        "can_open_transactions": True,
        "can_open_reports": True,
        "can_upload": False,
        "can_edit": False,
        "can_delete": False,
        "can_edit_gnucash": False,
        "can_delete_source": False,
    }
    assert isinstance(data["preflight_token"], str) and len(data["preflight_token"]) > 40
    assert second.json()["preflight_token"] != data["preflight_token"]
    token_payload = decode_preflight_token(data["preflight_token"], api_context["settings"])
    assert token_payload is not None
    assert token_payload["request"] == {
        "name": "Synthetic preflight book",
        "storage_type": "sqlite",
        "base_currency": "USD",
        "make_default": False,
    }
    assert token_payload["source"]["canonical_path_hash"] == canonical_path_hash(
        str(book_path.resolve(strict=True))
    )
    assert "canonical_path" not in token_payload["source"]
    assert decode_preflight_token(
        data["preflight_token"],
        api_context["settings"],
        now_epoch=int(token_payload["exp"]) - 1,
    ) is not None
    assert decode_preflight_token(
        data["preflight_token"],
        api_context["settings"],
        now_epoch=int(token_payload["exp"]),
    ) is None
    tampered_token = data["preflight_token"][:-1] + (
        "A" if data["preflight_token"][-1] != "A" else "B"
    )
    assert decode_preflight_token(tampered_token, api_context["settings"]) is None
    token_json = json.dumps(token_payload, sort_keys=True)
    assert str(book_path) not in token_json
    assert book_path.name not in token_json
    assert data["read_counters"] == {
        "sqlite_query_count": 5,
        "piecash_open_count": 1,
        "account_materialization_count": 0,
        "transaction_materialization_count": 0,
    }
    assert str(book_path) not in first.text
    assert book_path.name not in first.text

    assert _sha256(book_path) == before_hash
    assert book_path.stat().st_mtime_ns == before_mtime
    assert sorted(item.name for item in book_path.parent.iterdir()) == before_entries
    assert not (book_path.parent / f"{book_path.name}-journal").exists()
    assert not (book_path.parent / f"{book_path.name}-wal").exists()
    assert not (book_path.parent / f"{book_path.name}.backup").exists()

    with api_context["session_factory"]() as session:
        assert session.query(Book).count() == 0
        assert session.query(UserBookAccess).count() == 0
        assert session.query(BookHealthSnapshot).count() == 0


def test_preflight_registration_status_reports_existing_canonical_duplicate_without_writing(api_context):
    book_path = _copy_fixture(api_context["allowed_root"] / "already-registered.gnucash.sqlite")
    canonical = str(book_path.resolve(strict=True))
    with api_context["session_factory"]() as session:
        session.add(
            Book(
                name="Existing",
                storage_type="sqlite",
                uri_or_path=str(book_path),
                canonical_path=canonical,
                canonical_path_hash=canonical_path_hash(canonical),
                base_currency="USD",
            )
        )
        session.commit()
        before_count = session.query(Book).count()

    response = _post_preflight(api_context, book_path)

    assert response.status_code == 200
    assert response.json()["registration_status"] == {
        "status": "already_registered",
        "safe_code": "duplicate_canonical_path",
        "message": "A book with the same canonical source is already registered.",
        "retryable": False,
    }
    with api_context["session_factory"]() as session:
        assert session.query(Book).count() == before_count


@pytest.mark.parametrize(
    ("request_path", "expected_code"),
    [
        ("relative.gnucash.sqlite", "invalid_path"),
        ("~/book.gnucash.sqlite", "invalid_path"),
        ("$HOME/book.gnucash.sqlite", "invalid_path"),
        ("/tmp/${BOOK}.gnucash.sqlite", "invalid_path"),
        ("sqlite:////tmp/book.gnucash.sqlite", "unsupported_source"),
        ("postgresql://db.example/ledger", "unsupported_source"),
        ("/tmp/./book.gnucash.sqlite", "invalid_path"),
        ("/tmp/../tmp/book.gnucash.sqlite", "invalid_path"),
        ("/tmp/book\u0000.gnucash.sqlite", "invalid_path"),
    ],
)
def test_preflight_rejects_unsafe_request_paths_with_fixed_problem_codes(
    api_context, request_path, expected_code
):
    response = _post_preflight(api_context, request_path)

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["code"] == expected_code
    assert detail["retryable"] is False
    assert "/tmp" not in detail["message"]
    assert "book.gnucash" not in detail["message"]


def test_preflight_normalizes_base_currency_into_opaque_token_and_requires_it(api_context):
    book_path = _copy_fixture(api_context["allowed_root"] / "currency.gnucash.sqlite")

    lower_case = _post_preflight(api_context, book_path, base_currency="usd")
    missing_payload = _preflight_payload(book_path)
    missing_payload.pop("base_currency")
    missing = api_context["client"].post(
        "/books/preflight",
        headers=api_context["admin_headers"],
        json=missing_payload,
    )

    assert lower_case.status_code == 200
    token_payload = decode_preflight_token(
        lower_case.json()["preflight_token"], api_context["settings"]
    )
    assert token_payload is not None
    assert token_payload["request"]["base_currency"] == "USD"
    assert missing.status_code == 422


def test_preflight_validation_errors_do_not_echo_private_path_inputs(api_context):
    oversized_private_path = "/" + ("private-ledger-" * 90) + "only-copy.gnucash.sqlite"

    response = api_context["client"].post(
        "/books/preflight",
        headers=api_context["admin_headers"],
        json=_preflight_payload(Path(oversized_private_path)),
    )

    assert response.status_code == 422
    assert "input" not in response.text
    assert oversized_private_path not in response.text
    assert "only-copy.gnucash.sqlite" not in response.text
    assert "uri_or_path" in response.text


def test_preflight_rejects_symlinks_escape_and_similar_prefix_roots(api_context, tmp_path):
    allowed = api_context["allowed_root"]
    outside = tmp_path / "allowed-root-neighbor"
    outside.mkdir()
    outside_book = _copy_fixture(outside / "outside.gnucash.sqlite")

    final_symlink = allowed / "final-link.gnucash.sqlite"
    final_symlink.symlink_to(outside_book)
    symlink_dir = allowed / "linked-dir"
    symlink_dir.symlink_to(outside, target_is_directory=True)

    similar_prefix = _post_preflight(api_context, outside_book)
    final_link = _post_preflight(api_context, final_symlink)
    component_link = _post_preflight(api_context, symlink_dir / "outside.gnucash.sqlite")

    assert similar_prefix.status_code == 422
    assert similar_prefix.json()["detail"]["code"] == "outside_allowed_roots"
    assert final_link.status_code == 422
    assert final_link.json()["detail"]["code"] == "symlink_forbidden"
    assert component_link.status_code == 422
    assert component_link.json()["detail"]["code"] == "symlink_forbidden"
    combined = similar_prefix.text + final_link.text + component_link.text
    assert str(outside) not in combined
    assert outside_book.name not in combined


def test_preflight_rejects_parent_symlink_swap_after_canonicalization(
    api_context, tmp_path, monkeypatch
):
    from app.services import book_preflight

    allowed = api_context["allowed_root"]
    raced_dir = allowed / "raced-dir"
    raced_dir.mkdir()
    book_path = _copy_fixture(raced_dir / "raced.gnucash.sqlite")
    outside = tmp_path / "outside-race-target"
    outside.mkdir()
    _copy_fixture(outside / book_path.name)
    retained_dir = allowed / "retained-raced-dir"
    real_open = book_preflight._open_regular_file_no_follow

    def swapped_parent_open(canonical_path: Path, *args, **kwargs):
        assert Path(canonical_path) == book_path.resolve(strict=True)
        raced_dir.rename(retained_dir)
        raced_dir.symlink_to(outside, target_is_directory=True)
        return real_open(canonical_path, *args, **kwargs)

    monkeypatch.setattr(book_preflight, "_open_regular_file_no_follow", swapped_parent_open)

    response = _post_preflight(api_context, book_path)

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "symlink_forbidden"
    assert str(outside) not in response.text
    assert outside.name not in response.text
    assert book_path.name not in response.text


def test_full_probe_parent_swap_before_sqlite_uses_no_outside_source_schema_or_piecash(
    api_context, tmp_path, monkeypatch
):
    from app.services import book_preflight

    allowed = api_context["allowed_root"]
    raced_dir = allowed / "schema-raced-dir"
    raced_dir.mkdir()
    book_path = _copy_fixture(raced_dir / "schema-raced.gnucash.sqlite")
    outside = tmp_path / "schema-outside-target"
    outside.mkdir()
    outside_book = _copy_fixture(outside / book_path.name)
    retained_dir = allowed / "schema-retained-dir"
    outside_opens = {"source": 0, "schema": 0, "piecash": 0}

    source_open_name = (
        "_open_regular_file_no_follow"
        if hasattr(book_preflight, "_open_regular_file_no_follow")
        else "_read_regular_file_magic_no_follow"
    )
    real_source_open = getattr(book_preflight, source_open_name)
    real_schema_probe = book_preflight._verify_sqlite_gnucash_schema
    real_connect = book_preflight.sqlite3.connect
    real_open_book = book_preflight.piecash.open_book

    def counted_source_open(canonical_path: Path, *args, **kwargs):
        if _path_resolves_to(canonical_path, outside_book):
            outside_opens["source"] += 1
        return real_source_open(canonical_path, *args, **kwargs)

    def counted_connect(database, *args, **kwargs):
        if _path_resolves_to(_sqlite_database_path(database), outside_book):
            outside_opens["schema"] += 1
        return real_connect(database, *args, **kwargs)

    def counted_open_book(path, *args, **kwargs):
        if _path_resolves_to(path, outside_book):
            outside_opens["piecash"] += 1
        return real_open_book(path, *args, **kwargs)

    def swapped_schema_probe(source_path: str):
        raced_dir.rename(retained_dir)
        raced_dir.symlink_to(outside, target_is_directory=True)
        return real_schema_probe(source_path)

    monkeypatch.setattr(book_preflight, source_open_name, counted_source_open)
    monkeypatch.setattr(book_preflight.sqlite3, "connect", counted_connect)
    monkeypatch.setattr(book_preflight.piecash, "open_book", counted_open_book)
    monkeypatch.setattr(book_preflight, "_verify_sqlite_gnucash_schema", swapped_schema_probe)

    response = _post_preflight(api_context, book_path)

    assert response.status_code == 422
    assert response.json()["detail"]["code"] in {"source_changed", "symlink_forbidden"}
    assert outside_opens == {"source": 0, "schema": 0, "piecash": 0}
    assert str(outside) not in response.text
    assert outside.name not in response.text
    assert book_path.name not in response.text


def test_full_probe_parent_swap_before_piecash_uses_no_outside_source_schema_or_piecash(
    api_context, tmp_path, monkeypatch
):
    from app.services import book_preflight

    allowed = api_context["allowed_root"]
    raced_dir = allowed / "piecash-raced-dir"
    raced_dir.mkdir()
    book_path = _copy_fixture(raced_dir / "piecash-raced.gnucash.sqlite")
    outside = tmp_path / "piecash-outside-target"
    outside.mkdir()
    outside_book = _copy_fixture(outside / book_path.name)
    retained_dir = allowed / "piecash-retained-dir"
    outside_opens = {"source": 0, "schema": 0, "piecash": 0}

    source_open_name = (
        "_open_regular_file_no_follow"
        if hasattr(book_preflight, "_open_regular_file_no_follow")
        else "_read_regular_file_magic_no_follow"
    )
    real_source_open = getattr(book_preflight, source_open_name)
    real_connect = book_preflight.sqlite3.connect
    real_health_open = book_preflight._open_piecash_readonly_once
    real_open_book = book_preflight.piecash.open_book

    def counted_source_open(canonical_path: Path, *args, **kwargs):
        if _path_resolves_to(canonical_path, outside_book):
            outside_opens["source"] += 1
        return real_source_open(canonical_path, *args, **kwargs)

    def counted_connect(database, *args, **kwargs):
        if _path_resolves_to(_sqlite_database_path(database), outside_book):
            outside_opens["schema"] += 1
        return real_connect(database, *args, **kwargs)

    def counted_open_book(path, *args, **kwargs):
        if _path_resolves_to(path, outside_book):
            outside_opens["piecash"] += 1
        return real_open_book(path, *args, **kwargs)

    def swapped_piecash_open(source_path: str) -> None:
        raced_dir.rename(retained_dir)
        raced_dir.symlink_to(outside, target_is_directory=True)
        return real_health_open(source_path)

    monkeypatch.setattr(book_preflight, source_open_name, counted_source_open)
    monkeypatch.setattr(book_preflight.sqlite3, "connect", counted_connect)
    monkeypatch.setattr(book_preflight.piecash, "open_book", counted_open_book)
    monkeypatch.setattr(book_preflight, "_open_piecash_readonly_once", swapped_piecash_open)

    response = _post_preflight(api_context, book_path)

    assert response.status_code == 422
    assert response.json()["detail"]["code"] in {"source_changed", "symlink_forbidden"}
    assert outside_opens == {"source": 0, "schema": 0, "piecash": 0}
    assert str(outside) not in response.text
    assert outside.name not in response.text
    assert book_path.name not in response.text


def test_full_probe_leaf_replacement_before_piecash_does_not_open_replacement_inode(
    api_context, tmp_path, monkeypatch
):
    from app.services import book_preflight

    book_path = _copy_fixture(api_context["allowed_root"] / "leaf-raced.gnucash.sqlite")
    replacement = _copy_fixture(tmp_path / "replacement.gnucash.sqlite")
    retained_original = book_path.with_name("leaf-raced-retained.gnucash.sqlite")
    original_stat = book_path.stat()
    replacement_open_count = 0

    real_health_open = book_preflight._open_piecash_readonly_once
    real_open_book = book_preflight.piecash.open_book

    def counted_open_book(path, *args, **kwargs):
        nonlocal replacement_open_count
        try:
            opened_stat = Path(str(path)).stat()
        except OSError:
            opened_stat = None
        if opened_stat is not None and _same_inode(opened_stat, replacement.stat()):
            replacement_open_count += 1
        return real_open_book(path, *args, **kwargs)

    def swapped_piecash_open(source_path: str) -> None:
        book_path.rename(retained_original)
        shutil.copy2(replacement, book_path)
        assert not _same_inode(original_stat, book_path.stat())
        return real_health_open(source_path)

    monkeypatch.setattr(book_preflight.piecash, "open_book", counted_open_book)
    monkeypatch.setattr(book_preflight, "_open_piecash_readonly_once", swapped_piecash_open)

    response = _post_preflight(api_context, book_path)

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "source_changed"
    assert replacement_open_count == 0
    assert str(book_path) not in response.text
    assert book_path.name not in response.text


def test_open_piecash_readonly_once_disposes_engine_after_close(monkeypatch):
    from app.services import book_preflight

    events: list[str] = []

    class FakeBind:
        def dispose(self) -> None:
            events.append("dispose")

    class FakeSession:
        bind = FakeBind()

    class FakeBook:
        session = FakeSession()

        def close(self) -> None:
            events.append("close")

    def fake_open_book(path, *args, **kwargs):
        assert path == "/proc/self/fd/123"
        assert kwargs == {"readonly": True}
        return FakeBook()

    monkeypatch.setattr(book_preflight.piecash, "open_book", fake_open_book)

    book_preflight._open_piecash_readonly_once("/proc/self/fd/123")

    assert events == ["close", "dispose"]


def test_full_probe_closes_pinned_source_fd_on_success_and_error(api_context, monkeypatch):
    from app.services import book_preflight

    success_path = _copy_fixture(api_context["allowed_root"] / "fd-success.gnucash.sqlite")
    assert _fd_targets_containing(success_path.name) == []
    success = _post_preflight(api_context, success_path)
    assert success.status_code == 200
    assert _fd_targets_containing(success_path.name) == []

    error_path = _copy_fixture(api_context["allowed_root"] / "fd-error.gnucash.sqlite")

    def failing_schema_probe(source_path: str):
        raise book_preflight._problem("invalid_gnucash_schema")

    monkeypatch.setattr(book_preflight, "_verify_sqlite_gnucash_schema", failing_schema_probe)

    assert _fd_targets_containing(error_path.name) == []
    failure = _post_preflight(api_context, error_path)
    assert failure.status_code == 422
    assert failure.json()["detail"]["code"] == "invalid_gnucash_schema"
    assert _fd_targets_containing(error_path.name) == []


def test_preflight_rejects_outside_allowed_root_before_component_probes(
    api_context, tmp_path, monkeypatch
):
    from app.services import book_preflight

    outside = _copy_fixture(tmp_path / "outside-unprobed.gnucash.sqlite")

    def forbidden_component_probe(path: Path) -> None:  # pragma: no cover - regression guard
        raise AssertionError(f"outside-root path must not be component-probed: {path}")

    monkeypatch.setattr(book_preflight, "_reject_symlink_components", forbidden_component_probe)

    response = _post_preflight(api_context, outside)

    assert response.status_code == 422
    assert response.json()["detail"]["code"] == "outside_allowed_roots"
    assert str(outside) not in response.text
    assert outside.name not in response.text


def test_preflight_fails_closed_when_allowed_root_config_is_not_directory(
    api_context, tmp_path
):
    root_file = tmp_path / "configured-root-is-file"
    root_file.write_text("not a directory", encoding="utf-8")
    api_context["settings"].gnucash_book_allowed_roots = [str(root_file)]

    response = _post_preflight(api_context, root_file / "candidate.gnucash.sqlite")

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["code"] == "invalid_allowed_root_config"
    assert detail["retryable"] is False
    assert str(root_file) not in response.text
    assert root_file.name not in response.text


def test_preflight_ignores_unmounted_extra_allowed_roots(api_context):
    book_path = _copy_fixture(api_context["allowed_root"] / "available-root.gnucash.sqlite")
    api_context["settings"].gnucash_book_allowed_roots = [
        str(api_context["allowed_root"]),
        str(api_context["allowed_root"] / "future-unmounted-root"),
    ]

    response = _post_preflight(api_context, book_path)

    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_preflight_rejects_permission_denied_when_reproducible(api_context):
    if os.name != "posix" or getattr(os, "geteuid", lambda: 1)() == 0:
        pytest.skip("POSIX non-root chmod-based permission denial required")
    book_path = _copy_fixture(api_context["allowed_root"] / "permission-denied.gnucash.sqlite")
    original_mode = book_path.stat().st_mode
    book_path.chmod(0)
    try:
        response = _post_preflight(api_context, book_path)
    finally:
        book_path.chmod(original_mode)

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["code"] == "permission_denied"
    assert detail["retryable"] is True
    assert str(book_path) not in response.text
    assert book_path.name not in response.text


def test_preflight_detects_source_change_between_schema_probe_and_piecash_open(
    api_context, monkeypatch
):
    from app.services import book_preflight

    book_path = _copy_fixture(api_context["allowed_root"] / "changed-during-probe.gnucash.sqlite")
    real_verify = book_preflight._verify_sqlite_gnucash_schema

    def changing_schema_probe(canonical_path: str):
        result = real_verify(canonical_path)
        with open(canonical_path, "ab") as handle:
            handle.write(b"\n")
        return result

    monkeypatch.setattr(book_preflight, "_verify_sqlite_gnucash_schema", changing_schema_probe)

    response = _post_preflight(api_context, book_path)

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["code"] == "source_changed"
    assert detail["retryable"] is True
    assert str(book_path) not in response.text
    assert book_path.name not in response.text


@pytest.mark.parametrize(
    ("factory", "expected_code", "retryable"),
    [
        (lambda path: None, "missing_file", True),
        (lambda path: path.mkdir(), "not_regular_file", False),
        (lambda path: path.write_text("<gnc-v2></gnc-v2>", encoding="utf-8"), "unsupported_format", False),
        (lambda path: path.write_bytes(gzip.compress(b"<gnc-v2></gnc-v2>")), "unsupported_format", False),
        (lambda path: path.write_bytes(b"plain private bytes"), "unsupported_format", False),
    ],
)
def test_preflight_rejects_missing_directory_and_unsupported_content(
    api_context, factory, expected_code, retryable
):
    path = api_context["allowed_root"] / f"candidate-{expected_code}.gnucash.sqlite"
    factory(path)

    response = _post_preflight(api_context, path)

    assert response.status_code == 422
    detail = response.json()["detail"]
    assert detail["code"] == expected_code
    assert detail["retryable"] is retryable
    assert isinstance(detail["message"], str) and detail["message"]
    assert str(path) not in response.text
    assert path.name not in response.text


def test_preflight_accepts_gnucash_content_with_unusual_extension_and_rejects_bad_sqlite(api_context):
    unusual = _copy_fixture(api_context["allowed_root"] / "ledger.privatecopy")
    bad_sqlite = api_context["allowed_root"] / "fake.gnucash.sqlite"
    import sqlite3

    with sqlite3.connect(bad_sqlite) as conn:
        conn.execute("create table unrelated (id integer primary key)")

    success = _post_preflight(api_context, unusual)
    failure = _post_preflight(api_context, bad_sqlite)

    assert success.status_code == 200
    assert success.json()["format"] == "gnucash_sqlite"
    assert failure.status_code == 422
    assert failure.json()["detail"]["code"] == "invalid_gnucash_schema"
    assert str(bad_sqlite) not in failure.text
    assert bad_sqlite.name not in failure.text


def test_preflight_one_failed_candidate_does_not_affect_next_valid_candidate(api_context):
    invalid = api_context["allowed_root"] / "invalid.gnucash.sqlite"
    invalid.write_bytes(b"not sqlite")
    valid = _copy_fixture(api_context["allowed_root"] / "valid.gnucash.sqlite")

    failed = _post_preflight(api_context, invalid)
    succeeded = _post_preflight(api_context, valid)

    assert failed.status_code == 422
    assert failed.json()["detail"]["code"] == "unsupported_format"
    assert succeeded.status_code == 200
    assert succeeded.json()["status"] == "ready"
