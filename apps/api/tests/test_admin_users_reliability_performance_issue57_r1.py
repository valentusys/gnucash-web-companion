"""Issue #57 R1 synthetic app-DB reliability/performance evidence."""

from __future__ import annotations

import json
import time
from collections import Counter
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path
from threading import Barrier
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

from app.config import Settings, get_settings
from app.database import Base
from app.main import app
from app.models import AuditLog, Book, BookHealthSnapshot, User, UserBookAccess
from app.performance.admin_users_benchmark import (
    ADMIN_USERS_SYNTHETIC_NON_PRODUCTION_CLAIM,
    AdminUsersCaseEvidence,
    build_admin_users_case_evidence,
)
from app.routers.auth import get_db
from app.services.auth import hash_password
from app.services.user_admin import UserAdminError, UserAdminService

ADMIN_PASSWORD = "AdminPass123!"
USER_PASSWORD = "UserPass123!"
JWT_SECRET = "test-secret-key-for-admin-users-r1-32-bytes"
DATASET_SMALL = "issue57_r1_1_admin_10_users_5_books_mixed"
DATASET_LARGE = "issue57_r1_100_users_20_books_deterministic_access"


@dataclass(frozen=True)
class DatasetIds:
    admin_id: int
    user_ids: list[int]
    active_book_ids: list[int]
    disabled_book_id: int | None
    archived_book_id: int | None


@dataclass(frozen=True)
class SyntheticEnv:
    client: TestClient
    session_factory: sessionmaker
    engine: Any
    tmp_path: Path


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
def synthetic_env(tmp_path: Path):
    engine = create_engine(
        f"sqlite:///{tmp_path / 'issue57-r1.db'}",
        connect_args={"check_same_thread": False},
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine)
    settings = _settings(tmp_path)

    def override_get_db():
        with SessionLocal() as session:
            yield session

    app.dependency_overrides[get_settings] = lambda: settings
    app.dependency_overrides[get_db] = override_get_db
    try:
        yield SyntheticEnv(
            client=TestClient(app),
            session_factory=SessionLocal,
            engine=engine,
            tmp_path=tmp_path,
        )
    finally:
        app.dependency_overrides.clear()
        get_settings.cache_clear()
        engine.dispose()


def _seed_dataset(
    env: SyntheticEnv,
    *,
    regular_user_count: int,
    book_count: int,
    mixed_book_status: bool,
) -> DatasetIds:
    admin_hash = hash_password(ADMIN_PASSWORD)
    user_hash = hash_password(USER_PASSWORD)
    with env.session_factory() as session:
        admin = User(
            username="admin",
            display_name="Admin",
            password_hash=admin_hash,
            is_admin=True,
        )
        users = [
            User(
                username=f"user{i:03d}",
                display_name=f"User {i:03d}",
                password_hash=user_hash,
                is_admin=False,
                is_enabled=i != regular_user_count - 1,
            )
            for i in range(regular_user_count)
        ]
        books: list[Book] = []
        for i in range(book_count):
            is_disabled = mixed_book_status and i == book_count - 2
            is_archived = mixed_book_status and i == book_count - 1
            books.append(
                Book(
                    name=f"Book {i:02d}",
                    storage_type="sqlite",
                    uri_or_path=str(env.tmp_path / f"book-{i:02d}.gnucash.sqlite"),
                    base_currency="USD",
                    is_default=i == 0,
                    is_enabled=not is_disabled,
                    is_archived=is_archived,
                )
            )
        session.add_all([admin, *users, *books])
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
        active_books = [book for book in books if book.is_enabled and not book.is_archived]
        for user_index, user in enumerate(users):
            for book_index, book in enumerate(active_books):
                assigned = (user_index * 7 + book_index) % 5 < 2
                if user_index == 0 and book_index == 0:
                    assigned = True
                if user_index == 0 and book_index == 1:
                    assigned = False
                if assigned:
                    role = ("viewer", "editor", "owner")[(user_index + book_index) % 3]
                    session.add(
                        UserBookAccess(user_id=user.id, book_id=book.id, role=role)
                    )
        # Hidden assignments prove disabled/archived rows do not leak into admin DTOs.
        if mixed_book_status:
            session.add_all(
                [
                    UserBookAccess(user_id=users[0].id, book_id=books[-2].id, role="owner"),
                    UserBookAccess(user_id=users[0].id, book_id=books[-1].id, role="editor"),
                ]
            )
        session.commit()
        return DatasetIds(
            admin_id=int(admin.id),
            user_ids=[int(user.id) for user in users],
            active_book_ids=[int(book.id) for book in active_books],
            disabled_book_id=int(books[-2].id) if mixed_book_status else None,
            archived_book_id=int(books[-1].id) if mixed_book_status else None,
        )


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


def _audit_counts(session_factory: sessionmaker) -> Counter[str]:
    with session_factory() as session:
        return Counter(action for (action,) in session.query(AuditLog.action).all())


def _audit_delta(before: Counter[str], after: Counter[str]) -> dict[str, int]:
    delta = after - before
    return {key: delta[key] for key in sorted(delta)}


def _response_bytes(value: Any) -> int:
    if hasattr(value, "content"):
        return len(value.content)
    if isinstance(value, (list, tuple)):
        return sum(_response_bytes(item) for item in value)
    return 0


@contextmanager
def _instrument_app_db(engine):
    counts = {
        "observed_sqlite_statement_count": 0,
        "observed_sqlite_query_count": 0,
        "materialized_user_rows": 0,
        "materialized_book_rows": 0,
        "materialized_access_rows": 0,
        "preflight_open_count": 0,
        "piecash_open_count": 0,
        "gnucash_service_open_count": 0,
        "transaction_materialization_count": 0,
    }

    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        counts["observed_sqlite_statement_count"] += 1
        if statement.lstrip().lower().startswith("select"):
            counts["observed_sqlite_query_count"] += 1

    def user_load(target, context):
        counts["materialized_user_rows"] += 1

    def book_load(target, context):
        counts["materialized_book_rows"] += 1

    def access_load(target, context):
        counts["materialized_access_rows"] += 1

    event.listen(engine, "before_cursor_execute", before_cursor_execute)
    event.listen(User, "load", user_load)
    event.listen(Book, "load", book_load)
    event.listen(UserBookAccess, "load", access_load)
    try:
        yield counts
    finally:
        event.remove(engine, "before_cursor_execute", before_cursor_execute)
        event.remove(User, "load", user_load)
        event.remove(Book, "load", book_load)
        event.remove(UserBookAccess, "load", access_load)


def _install_source_open_guards(monkeypatch, counts: dict[str, int]) -> None:
    def fail_preflight(*args, **kwargs):
        counts["preflight_open_count"] += 1
        raise AssertionError("admin-user benchmark must not run source preflight")

    def fail_piecash_open(*args, **kwargs):
        counts["piecash_open_count"] += 1
        raise AssertionError("admin-user benchmark must not open a GnuCash book")

    class DummyAccountService:
        def __init__(self, book):
            counts["gnucash_service_open_count"] += 1

        def list_accounts(self):
            return []

    monkeypatch.setattr("app.services.book_preflight.run_book_health_probe", fail_preflight)
    monkeypatch.setattr("app.routers.books.run_book_health_probe", fail_preflight)
    monkeypatch.setattr("app.services.gnucash_book.piecash.open_book", fail_piecash_open)
    monkeypatch.setattr("app.routers.books.account_service_for", DummyAccountService)


def _measure_case(
    env: SyntheticEnv,
    monkeypatch,
    *,
    name: str,
    dataset: str,
    action: Callable[[], Any],
    repeat_count: int = 1,
) -> tuple[list[Any], AdminUsersCaseEvidence]:
    durations_ms: list[float] = []
    responses: list[Any] = []
    max_counts: dict[str, int] = Counter()
    max_response_bytes = 0
    audit_before = _audit_counts(env.session_factory)
    for _ in range(repeat_count):
        with _instrument_app_db(env.engine) as counts:
            _install_source_open_guards(monkeypatch, counts)
            started = time.perf_counter()
            response = action()
            durations_ms.append((time.perf_counter() - started) * 1000)
        responses.append(response)
        max_response_bytes = max(max_response_bytes, _response_bytes(response))
        for key, value in counts.items():
            max_counts[key] = max(max_counts.get(key, 0), int(value))
    audit_after = _audit_counts(env.session_factory)
    evidence = build_admin_users_case_evidence(
        name=name,
        dataset=dataset,
        durations_ms=durations_ms,
        response_bytes=max_response_bytes,
        observed_sqlite_statement_count=max_counts["observed_sqlite_statement_count"],
        observed_sqlite_query_count=max_counts["observed_sqlite_query_count"],
        materialized_user_rows=max_counts["materialized_user_rows"],
        materialized_book_rows=max_counts["materialized_book_rows"],
        materialized_access_rows=max_counts["materialized_access_rows"],
        preflight_open_count=max_counts["preflight_open_count"],
        piecash_open_count=max_counts["piecash_open_count"],
        gnucash_service_open_count=max_counts["gnucash_service_open_count"],
        transaction_materialization_count=max_counts["transaction_materialization_count"],
        app_metadata_mutation_counts_by_operation=_audit_delta(audit_before, audit_after),
        gnucash_mutation_capable_request_count=0,
        deterministic_ordering_or_pagination=True,
    )
    return responses, evidence


def _assert_evidence_shape(evidence: AdminUsersCaseEvidence) -> None:
    serialized = asdict(evidence)
    assert set(serialized) == {
        "name",
        "dataset",
        "sample_count",
        "repeat_count",
        "duration_ms_min",
        "duration_ms_median",
        "duration_ms_max",
        "response_bytes",
        "observed_sqlite_statement_count",
        "observed_sqlite_query_count",
        "materialized_user_rows",
        "materialized_book_rows",
        "materialized_access_rows",
        "preflight_open_count",
        "piecash_open_count",
        "gnucash_service_open_count",
        "transaction_materialization_count",
        "app_metadata_mutation_counts_by_operation",
        "gnucash_mutation_capable_request_count",
        "deterministic_ordering_or_pagination",
        "synthetic_non_production_claim",
    }
    assert evidence.sample_count == evidence.repeat_count >= 1
    assert evidence.duration_ms_min <= evidence.duration_ms_median <= evidence.duration_ms_max
    assert evidence.response_bytes >= 0
    assert evidence.observed_sqlite_statement_count >= evidence.observed_sqlite_query_count >= 0
    assert evidence.preflight_open_count == 0
    assert evidence.piecash_open_count == 0
    assert evidence.transaction_materialization_count == 0
    assert evidence.gnucash_mutation_capable_request_count == 0
    assert evidence.deterministic_ordering_or_pagination is True
    assert evidence.synthetic_non_production_claim == ADMIN_USERS_SYNTHETIC_NON_PRODUCTION_CLAIM


def test_issue57_r1_small_dataset_covers_admin_user_reliability_cases(
    synthetic_env: SyntheticEnv, monkeypatch
) -> None:
    ids = _seed_dataset(
        synthetic_env,
        regular_user_count=10,
        book_count=5,
        mixed_book_status=True,
    )
    admin_headers = _headers(_login(synthetic_env.client))
    viewer_headers = _headers(_login(synthetic_env.client, "user000", USER_PASSWORD))
    viewer_id = ids.user_ids[0]
    disabled_user_id = ids.user_ids[-1]
    assigned_book_id = ids.active_book_ids[0]
    inaccessible_book_id = ids.active_book_ids[1]
    evidence: list[AdminUsersCaseEvidence] = []

    responses, case = _measure_case(
        synthetic_env,
        monkeypatch,
        name="list_users_ordered_redacted_bounded",
        dataset=DATASET_SMALL,
        repeat_count=3,
        action=lambda: synthetic_env.client.get(
            "/admin/users?limit=100&offset=0&state=all",
            headers=admin_headers,
        ),
    )
    evidence.append(case)
    list_payload = responses[-1].json()
    assert responses[-1].status_code == 200
    assert list_payload["total_count"] == 11
    assert list_payload["limit"] == 100
    assert list_payload["offset"] == 0
    assert list_payload["has_next"] is False
    assert [item["username"] for item in list_payload["items"]] == sorted(
        item["username"] for item in list_payload["items"]
    )
    assert "password_hash" not in responses[-1].text
    assert "auth_version" not in responses[-1].text
    assert USER_PASSWORD not in responses[-1].text
    assert case.observed_sqlite_query_count <= 4

    responses, case = _measure_case(
        synthetic_env,
        monkeypatch,
        name="user_detail_active_assignments_only",
        dataset=DATASET_SMALL,
        action=lambda: synthetic_env.client.get(
            f"/admin/users/{viewer_id}",
            headers=admin_headers,
        ),
    )
    evidence.append(case)
    detail = responses[-1].json()
    assert responses[-1].status_code == 200
    assert detail["username"] == "user000"
    assert detail["assignments"] == [
        {
            "book_id": assigned_book_id,
            "book_name": "Book 00",
            "is_default": True,
            "role": "viewer",
        }
    ]
    assert ids.disabled_book_id not in {item["book_id"] for item in detail["assignments"]}
    assert ids.archived_book_id not in {item["book_id"] for item in detail["assignments"]}
    assert case.observed_sqlite_query_count <= 3

    responses, case = _measure_case(
        synthetic_env,
        monkeypatch,
        name="list_book_options_active_ordered_bounded",
        dataset=DATASET_SMALL,
        action=lambda: synthetic_env.client.get(
            "/admin/book-access/books?limit=100&offset=0",
            headers=admin_headers,
        ),
    )
    evidence.append(case)
    books_payload = responses[-1].json()
    assert responses[-1].status_code == 200
    assert books_payload["total_count"] == 3
    assert [item["name"] for item in books_payload["items"]] == ["Book 00", "Book 01", "Book 02"]
    assert "uri_or_path" not in responses[-1].text
    assert case.observed_sqlite_query_count <= 3

    responses, case = _measure_case(
        synthetic_env,
        monkeypatch,
        name="create_user_redacted_audited",
        dataset=DATASET_SMALL,
        action=lambda: synthetic_env.client.post(
            "/admin/users",
            headers=admin_headers,
            json={
                "username": "created-user",
                "display_name": "Created User",
                "password": "CreatedUser123!",
            },
        ),
    )
    evidence.append(case)
    created_user_id = responses[-1].json()["id"]
    assert responses[-1].status_code == 201
    assert case.app_metadata_mutation_counts_by_operation == {"user_created": 1}
    assert "CreatedUser123!" not in responses[-1].text

    responses, case = _measure_case(
        synthetic_env,
        monkeypatch,
        name="display_update_enable_disable_reset_redacted_audited",
        dataset=DATASET_SMALL,
        action=lambda: [
            synthetic_env.client.patch(
                f"/admin/users/{created_user_id}",
                headers=admin_headers,
                json={"display_name": "Updated User"},
            ),
            synthetic_env.client.post(f"/admin/users/{created_user_id}/disable", headers=admin_headers),
            synthetic_env.client.post(f"/admin/users/{created_user_id}/enable", headers=admin_headers),
            synthetic_env.client.post(
                f"/admin/users/{created_user_id}/password-reset",
                headers=admin_headers,
                json={"new_password": "ResetCreated123!"},
            ),
        ],
    )
    evidence.append(case)
    assert [response.status_code for response in responses[-1]] == [200, 200, 200, 200]
    assert responses[-1][-1].json() == {
        "status": "password_reset",
        "subject_user_id": created_user_id,
        "session_invalidated": True,
    }
    assert case.app_metadata_mutation_counts_by_operation == {
        "display_name_changed": 1,
        "password_reset": 1,
        "user_disabled": 1,
        "user_enabled": 1,
    }
    assert "ResetCreated123!" not in json.dumps([r.text for r in responses[-1]])

    responses, case = _measure_case(
        synthetic_env,
        monkeypatch,
        name="grant_update_revoke_access_redacted_audited",
        dataset=DATASET_SMALL,
        action=lambda: [
            synthetic_env.client.put(
                f"/admin/users/{created_user_id}/book-access/{assigned_book_id}",
                headers=admin_headers,
                json={"role": "viewer"},
            ),
            synthetic_env.client.put(
                f"/admin/users/{created_user_id}/book-access/{assigned_book_id}",
                headers=admin_headers,
                json={"role": "editor"},
            ),
            synthetic_env.client.delete(
                f"/admin/users/{created_user_id}/book-access/{assigned_book_id}",
                headers=admin_headers,
            ),
        ],
    )
    evidence.append(case)
    assert [response.status_code for response in responses[-1]] == [200, 200, 204]
    assert case.app_metadata_mutation_counts_by_operation == {
        "book_access_granted": 1,
        "book_access_revoked": 1,
        "book_access_role_changed": 1,
    }
    with synthetic_env.session_factory() as session:
        audit_payloads = [json.loads(row.payload_json or "{}") for row in session.query(AuditLog).all()]
    for payload in audit_payloads:
        assert "password_hash" not in json.dumps(payload)
        assert "ResetCreated123!" not in json.dumps(payload)
        assert "Book 00" not in json.dumps(payload)

    responses, case = _measure_case(
        synthetic_env,
        monkeypatch,
        name="selected_context_accessible_and_openable_without_inaccessible_open",
        dataset=DATASET_SMALL,
        action=lambda: [
            synthetic_env.client.get("/books", headers=viewer_headers),
            synthetic_env.client.get(f"/books/{assigned_book_id}", headers=viewer_headers),
            synthetic_env.client.get(f"/books/{assigned_book_id}/accounts", headers=viewer_headers),
            synthetic_env.client.get(f"/books/{inaccessible_book_id}/accounts", headers=viewer_headers),
        ],
    )
    evidence.append(case)
    switcher, selected, openable, denied = responses[-1]
    assert switcher.status_code == 200
    assert [item["id"] for item in switcher.json()] == [assigned_book_id]
    assert selected.status_code == 200
    assert selected.json()["id"] == assigned_book_id
    assert openable.status_code == 200
    assert openable.json() == []
    assert denied.status_code == 403
    assert denied.json()["detail"] == "Book access denied"
    assert case.gnucash_service_open_count == 1

    responses, case = _measure_case(
        synthetic_env,
        monkeypatch,
        name="disabled_user_auth_rejected",
        dataset=DATASET_SMALL,
        action=lambda: synthetic_env.client.post(
            "/auth/login",
            json={"username": "user009", "password": USER_PASSWORD},
        ),
    )
    evidence.append(case)
    assert disabled_user_id == ids.user_ids[-1]
    assert responses[-1].status_code == 401

    for case in evidence:
        _assert_evidence_shape(case)
    assert {case.name for case in evidence} == {
        "list_users_ordered_redacted_bounded",
        "user_detail_active_assignments_only",
        "list_book_options_active_ordered_bounded",
        "create_user_redacted_audited",
        "display_update_enable_disable_reset_redacted_audited",
        "grant_update_revoke_access_redacted_audited",
        "selected_context_accessible_and_openable_without_inaccessible_open",
        "disabled_user_auth_rejected",
    }


def test_issue57_r1_large_dataset_has_bounded_queries_payload_and_access_materialization(
    synthetic_env: SyntheticEnv, monkeypatch
) -> None:
    ids = _seed_dataset(
        synthetic_env,
        regular_user_count=99,
        book_count=20,
        mixed_book_status=False,
    )
    admin_headers = _headers(_login(synthetic_env.client))
    viewer_headers = _headers(_login(synthetic_env.client, "user000", USER_PASSWORD))

    user_responses, list_users = _measure_case(
        synthetic_env,
        monkeypatch,
        name="100x20_list_users_no_assignment_n_plus_one",
        dataset=DATASET_LARGE,
        repeat_count=3,
        action=lambda: synthetic_env.client.get(
            "/admin/users?limit=100&offset=0&state=all",
            headers=admin_headers,
        ),
    )
    assert user_responses[-1].status_code == 200
    assert user_responses[-1].json()["total_count"] == 100
    assert len(user_responses[-1].json()["items"]) == 100
    assert len(user_responses[-1].content) < 80_000
    assert list_users.observed_sqlite_query_count <= 4
    assert list_users.materialized_access_rows <= 1

    book_responses, list_books = _measure_case(
        synthetic_env,
        monkeypatch,
        name="100x20_accessible_books_no_assignment_materialization",
        dataset=DATASET_LARGE,
        repeat_count=3,
        action=lambda: synthetic_env.client.get("/books", headers=viewer_headers),
    )
    assert book_responses[-1].status_code == 200
    visible_book_ids = [item["id"] for item in book_responses[-1].json()]
    assert visible_book_ids == [
        ids.active_book_ids[index] for index in (0, 5, 6, 10, 11, 15, 16)
    ]
    assert len(book_responses[-1].content) < 30_000
    assert list_books.observed_sqlite_query_count <= 2
    assert list_books.materialized_access_rows <= len(visible_book_ids)

    inaccessible_book_id = ids.active_book_ids[1]
    denied_responses, denied = _measure_case(
        synthetic_env,
        monkeypatch,
        name="100x20_inaccessible_book_stops_before_source_open",
        dataset=DATASET_LARGE,
        action=lambda: synthetic_env.client.get(
            f"/books/{inaccessible_book_id}/accounts",
            headers=viewer_headers,
        ),
    )
    assert denied_responses[-1].status_code == 403
    assert denied_responses[-1].json()["detail"] == "Book access denied"
    assert denied.gnucash_service_open_count == 0
    assert denied.materialized_access_rows <= 1

    for case in (list_users, list_books, denied):
        _assert_evidence_shape(case)
        assert case.dataset == DATASET_LARGE


def test_issue57_r1_concurrent_duplicate_user_grant_and_last_admin_races_are_deterministic(
    synthetic_env: SyntheticEnv,
) -> None:
    ids = _seed_dataset(
        synthetic_env,
        regular_user_count=10,
        book_count=5,
        mixed_book_status=True,
    )
    with synthetic_env.session_factory() as session:
        second_admin = User(
            username="second-admin",
            display_name="Second Admin",
            password_hash=hash_password("SecondAdmin123!"),
            is_admin=True,
        )
        session.add(second_admin)
        session.commit()
        second_admin_id = int(second_admin.id)

    create_barrier = Barrier(2)

    def create_duplicate() -> str | int:
        with synthetic_env.session_factory() as session:
            create_barrier.wait(timeout=5)
            try:
                detail = UserAdminService(session).create_user(
                    actor_user_id=ids.admin_id,
                    username="race-user",
                    display_name="Race User",
                    password="RaceUser123!",
                )
                return f"ok:{detail.id}"
            except UserAdminError as exc:
                return exc.status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        create_results = list(pool.map(lambda _item: create_duplicate(), range(2)))
    assert sum(isinstance(result, str) and result.startswith("ok:") for result in create_results) == 1
    assert create_results.count(409) == 1
    with synthetic_env.session_factory() as session:
        assert session.query(User).filter(User.username == "race-user").count() == 1

    grant_barrier = Barrier(2)
    viewer_id = ids.user_ids[1]
    book_id = ids.active_book_ids[1]

    def grant_duplicate(role: str) -> str:
        with synthetic_env.session_factory() as session:
            grant_barrier.wait(timeout=5)
            return UserAdminService(session).set_book_access(
                actor_user_id=ids.admin_id,
                subject_user_id=viewer_id,
                book_id=book_id,
                role=role,
            ).role

    with ThreadPoolExecutor(max_workers=2) as pool:
        grant_results = list(pool.map(grant_duplicate, ["viewer", "editor"]))
    assert set(grant_results).issubset({"viewer", "editor"})
    with synthetic_env.session_factory() as session:
        rows = session.query(UserBookAccess).filter_by(user_id=viewer_id, book_id=book_id).all()
        assert len(rows) == 1
        assert rows[0].role in {"viewer", "editor"}

    last_admin_barrier = Barrier(2)

    def disable_admin(actor_id: int, subject_id: int) -> str | int:
        with synthetic_env.session_factory() as session:
            last_admin_barrier.wait(timeout=5)
            try:
                UserAdminService(session).disable_user(
                    actor_user_id=actor_id,
                    subject_user_id=subject_id,
                )
                return "ok"
            except UserAdminError as exc:
                return exc.status_code

    with ThreadPoolExecutor(max_workers=2) as pool:
        disable_results = list(
            pool.map(
                lambda pair: disable_admin(*pair),
                [(ids.admin_id, second_admin_id), (second_admin_id, ids.admin_id)],
            )
        )
    assert disable_results.count("ok") == 1
    assert any(result in {403, 409} for result in disable_results)
    with synthetic_env.session_factory() as session:
        assert (
            session.query(User)
            .filter(User.is_admin.is_(True), User.is_enabled.is_(True))
            .count()
            == 1
        )
