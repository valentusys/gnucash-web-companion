"""#36-W2-A synthetic CREATE/PATCH/DELETE route-family drill.

All mutations in this file use an in-memory app DB and a fake write service.
No GnuCash book is opened or mutated.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import Settings, get_settings
from app.database import Base
from app.main import app
from app.models import AuditLog, Book, User, UserBookAccess
from app.routers.auth import get_db
from app.schemas.gnucash import TransactionDetailDTO, TransactionSplitDTO
from app.schemas.gnucash_writes import TransactionValidationResultDTO, TransactionWriteResultDTO
from app.services.auth import hash_password

TEST_SETTINGS = Settings(
    app_env="test",
    app_database_url="sqlite:///:memory:",
    jwt_secret="test-secret-key-for-unit-tests-32-bytes-minimum",
    app_admin_username="admin",
    app_admin_password="testpassword123",
    gnucash_writes_enabled=True,
)

REPO_ROOT = Path(__file__).resolve().parents[3]

READ_ONLY_SETTINGS = Settings(
    app_env="test",
    app_database_url="sqlite:///:memory:",
    jwt_secret="test-secret-key-for-unit-tests-32-bytes-minimum",
    app_admin_username="admin",
    app_admin_password="testpassword123",
    gnucash_writes_enabled=False,
)


@dataclass
class FakeWriteService:
    calls: list[tuple[str, object]]

    def validate_transaction_create(self, request):
        self.calls.append(("validate", request))
        return TransactionValidationResultDTO(valid=True, errors=[], warnings=[], summary={"synthetic": True})

    def create_transaction(self, *, request, user_id: int, book_id: int):
        self.calls.append(("create", request))
        return TransactionWriteResultDTO(transaction_id="synthetic-created-tx", backup_path="backup-create-ref")

    def patch_transaction_metadata(self, *, transaction_id: str, request, user_id: int, book_id: int):
        self.calls.append(("patch", request))
        return TransactionWriteResultDTO(transaction_id=transaction_id, backup_path="backup-patch-ref")

    def delete_transaction(self, *, transaction_id: str, user_id: int, book_id: int):
        self.calls.append(("delete", transaction_id))
        return TransactionWriteResultDTO(transaction_id=transaction_id, backup_path="backup-delete-ref")


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
def fake_write_calls(monkeypatch):
    calls: list[tuple[str, object]] = []

    def fake_write_service_for(book):
        target = Path(str(book.uri_or_path)).resolve()
        assert target.is_file()
        assert "disposable" in target.name
        with pytest.raises(ValueError):
            target.relative_to(REPO_ROOT)
        return FakeWriteService(calls)

    class FakeReadService:
        def get_transaction(self, transaction_id: str) -> TransactionDetailDTO:
            create_requests = [payload for name, payload in calls if name == "create"]
            assert create_requests, "read-back verification must follow a synthetic CREATE call"
            request = create_requests[-1]
            return TransactionDetailDTO(
                id=transaction_id,
                date=request.date,
                description=request.description,
                currency=request.splits[0].currency,
                splits=[
                    TransactionSplitDTO(
                        account_id=split.account_id,
                        account_name=split.account_id,
                        memo=split.memo,
                        reconcile_state="",
                        amount=split.amount,
                        currency=split.currency,
                    )
                    for split in request.splits
                ],
            )

    monkeypatch.setattr("app.routers.transactions._write_service_for", fake_write_service_for)
    monkeypatch.setattr("app.routers.transactions.transaction_service_for", lambda book: FakeReadService())
    return calls


@pytest.fixture
def client(session_factory, fake_write_calls):
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
def synthetic_book(session_factory, tmp_path: Path):
    target = tmp_path / "owner-writebeta-disposable-route-family.gnucash.sqlite"
    target.write_bytes(b"SQLite format 3\x00 synthetic route-family placeholder")
    with session_factory() as session:
        book = Book(
            name="Synthetic owner-writebeta route-family fixture",
            storage_type="sqlite",
            uri_or_path=str(target),
            is_default=True,
        )
        session.add(book)
        session.flush()
        admin = session.query(User).filter(User.username == "admin").one()
        session.add(UserBookAccess(user_id=admin.id, book_id=book.id, role="owner"))
        session.commit()
        return book.id


@pytest.fixture
def external_unproven_book(session_factory, tmp_path: Path):
    target = tmp_path / "owner-ledger.gnucash.sqlite"
    target.write_bytes(b"SQLite format 3\x00 unproven route-family placeholder")
    with session_factory() as session:
        book = Book(
            name="Unproven external route-family target",
            storage_type="sqlite",
            uri_or_path=str(target),
            is_default=False,
        )
        session.add(book)
        session.flush()
        admin = session.query(User).filter(User.username == "admin").one()
        session.add(UserBookAccess(user_id=admin.id, book_id=book.id, role="owner"))
        session.commit()
        return book.id


def _synthetic_create_payload():
    return {
        "date": "2026-06-03",
        "description": "Synthetic route-family fixture",
        "splits": [
            {"account_id": "synthetic-bank", "amount": "-10.00", "currency": "SEK", "memo": ""},
            {"account_id": "synthetic-expense", "amount": "10.00", "currency": "SEK", "memo": ""},
        ],
    }


def _preview_confirm_headers(client: TestClient, auth_headers: dict[str, str], book_id: int, operation: str, *, target_owned: bool = False):
    preflight = client.post(f"/books/{book_id}/owner-writebeta/preflight", headers=auth_headers)
    assert preflight.status_code == 200
    preview = client.post(
        f"/books/{book_id}/owner-writebeta/preview",
        headers=auth_headers,
        json={
            "operation": operation,
            "payload_shape": {"synthetic_route_family": "shape-only"},
            "target_is_write_alpha_owned": target_owned,
            "metadata_only_patch": True,
        },
    )
    assert preview.status_code == 200
    preview_hash = preview.json()["preview_hash"]
    confirm = client.post(
        f"/books/{book_id}/owner-writebeta/confirm",
        headers=auth_headers,
        json={
            "preview_hash": preview_hash,
            "backup_ref": f"bkp-{operation.lower()}-ref",
            "restore_readiness_ref": f"rr-{operation.lower()}-ref",
        },
    )
    assert confirm.status_code == 200
    return {
        **auth_headers,
        "X-Owner-Writebeta-Preview-Hash": preview_hash,
        "X-Owner-Writebeta-Confirmation-Token": confirm.json()["confirmation_token"],
    }


def _verify_and_reset(client: TestClient, auth_headers: dict[str, str], book_id: int, suffix: str):
    verify = client.post(
        f"/books/{book_id}/owner-writebeta/verify-reset",
        headers=auth_headers,
        json={
            "audit_ref": f"audit-{suffix}-ref",
            "restore_ref": f"restore-{suffix}-ref",
            "lock_released": True,
            "defaults_reset": True,
        },
    )
    assert verify.status_code == 200
    assert verify.json()["state"] == "reset_required"
    reset = client.post(f"/books/{book_id}/owner-writebeta/reset-disabled", headers=auth_headers)
    assert reset.status_code == 200
    assert reset.json()["state"] == "disabled"
    assert reset.json()["writes_blocked"] is True
    assert reset.json()["summary"]["preview_hash"] is None
    assert reset.json()["summary"]["confirmation_token_ref"] is None


def test_synthetic_create_patch_delete_route_family_requires_fresh_confirmed_gate_and_default_reset(
    client,
    auth_headers,
    synthetic_book,
    fake_write_calls,
):
    create_headers = _preview_confirm_headers(client, auth_headers, synthetic_book, "CREATE")
    create = client.post(
        f"/books/{synthetic_book}/transactions",
        headers=create_headers,
        json=_synthetic_create_payload(),
    )
    assert create.status_code == 201
    assert create.json()["transaction_id"] == "synthetic-created-tx"
    _verify_and_reset(client, auth_headers, synthetic_book, "create")

    patch_headers = _preview_confirm_headers(client, auth_headers, synthetic_book, "PATCH", target_owned=True)
    patch = client.patch(
        f"/books/{synthetic_book}/transactions/synthetic-created-tx",
        headers=patch_headers,
        json={"description": "metadata-only", "split_memos": {"synthetic-split": "memo-only"}},
    )
    assert patch.status_code == 200
    patched_request = [payload for name, payload in fake_write_calls if name == "patch"][-1]
    assert patched_request.description == "metadata-only"
    assert patched_request.split_memos == {"synthetic-split": "memo-only"}
    for immutable_field in ("amount", "account_id", "splits", "currency", "date"):
        assert not hasattr(patched_request, immutable_field)
    _verify_and_reset(client, auth_headers, synthetic_book, "patch")

    delete_headers = _preview_confirm_headers(client, auth_headers, synthetic_book, "DELETE", target_owned=True)
    non_owned_delete = client.delete(
        f"/books/{synthetic_book}/transactions/not-created-by-write-alpha",
        headers=delete_headers,
    )
    assert non_owned_delete.status_code == 403
    assert "Write-alpha DELETE is allowed only" in non_owned_delete.json()["detail"]
    delete = client.delete(
        f"/books/{synthetic_book}/transactions/synthetic-created-tx",
        headers=delete_headers,
    )
    assert delete.status_code == 200
    _verify_and_reset(client, auth_headers, synthetic_book, "delete")

    app.dependency_overrides[get_settings] = lambda: READ_ONLY_SETTINGS
    disabled_create = client.post(
        f"/books/{synthetic_book}/transactions",
        headers=auth_headers,
        json=_synthetic_create_payload(),
    )
    assert disabled_create.status_code == 403
    assert "read-only" in disabled_create.json()["detail"]
    assert [name for name, _ in fake_write_calls] == ["create", "patch", "delete"]


def test_synthetic_route_family_create_requires_disposable_target_preflight_before_write_service(
    client,
    auth_headers,
    external_unproven_book,
    fake_write_calls,
    session_factory,
):
    create_headers = _preview_confirm_headers(client, auth_headers, external_unproven_book, "CREATE")

    response = client.post(
        f"/books/{external_unproven_book}/transactions",
        headers=create_headers,
        json=_synthetic_create_payload(),
    )

    assert response.status_code == 403
    detail = response.json()["detail"]
    assert "Disposable target preflight failed closed" in detail
    assert "filename must mark it as copied/disposable/synthetic test data" in detail
    assert "owner-ledger" not in detail
    assert fake_write_calls == []
    with session_factory() as session:
        assert session.query(AuditLog).filter_by(action="transaction.create").count() == 0
    from app.routers.owner_writebeta import _SESSIONS

    assert _SESSIONS[external_unproven_book].state.value == "confirmation"


def test_synthetic_route_family_create_requires_target_outside_repo_before_write_service(
    client,
    auth_headers,
    fake_write_calls,
    session_factory,
    tmp_path: Path,
    monkeypatch,
):
    target = tmp_path / "inside-repo-disposable-route-family.gnucash.sqlite"
    target.write_bytes(b"SQLite format 3\x00 inside simulated repo placeholder")
    with session_factory() as session:
        book = Book(
            name="Repo-contained disposable-looking route-family target",
            storage_type="sqlite",
            uri_or_path=str(target),
            is_default=False,
        )
        session.add(book)
        session.flush()
        admin = session.query(User).filter(User.username == "admin").one()
        session.add(UserBookAccess(user_id=admin.id, book_id=book.id, role="owner"))
        session.commit()
        book_id = book.id

    create_headers = _preview_confirm_headers(client, auth_headers, book_id, "CREATE")
    import app.routers.transactions as transactions_router

    monkeypatch.setattr(transactions_router, "REPO_ROOT", tmp_path.parent)

    response = client.post(
        f"/books/{book_id}/transactions",
        headers=create_headers,
        json=_synthetic_create_payload(),
    )

    assert response.status_code == 403
    detail = response.json()["detail"]
    assert "Disposable target preflight failed closed" in detail
    assert "outside the git working tree" in detail
    assert str(target) not in detail
    assert fake_write_calls == []
    with session_factory() as session:
        assert session.query(AuditLog).filter_by(action="transaction.create").count() == 0
    from app.routers.owner_writebeta import _SESSIONS

    assert _SESSIONS[book_id].state.value == "confirmation"


@pytest.mark.parametrize(
    ("field_name", "immutable_payload"),
    [
        ("amount", {"amount": "999.99"}),
        ("account_id", {"account_id": "synthetic-other-account"}),
        (
            "splits",
            {
                "splits": [
                    {
                        "account_id": "synthetic-bank",
                        "amount": "-999.99",
                        "currency": "SEK",
                        "memo": "immutable split replacement",
                    },
                    {
                        "account_id": "synthetic-expense",
                        "amount": "999.99",
                        "currency": "SEK",
                        "memo": "immutable split replacement",
                    },
                ]
            },
        ),
        ("currency", {"currency": "USD"}),
        ("date", {"date": "2026-12-31"}),
    ],
)
def test_synthetic_patch_route_rejects_immutable_fields_without_calling_patch(
    client,
    auth_headers,
    synthetic_book,
    fake_write_calls,
    field_name,
    immutable_payload,
):
    create_headers = _preview_confirm_headers(client, auth_headers, synthetic_book, "CREATE")
    create = client.post(
        f"/books/{synthetic_book}/transactions",
        headers=create_headers,
        json=_synthetic_create_payload(),
    )
    assert create.status_code == 201
    _verify_and_reset(client, auth_headers, synthetic_book, "create-for-rejected-patch")

    patch_headers = _preview_confirm_headers(client, auth_headers, synthetic_book, "PATCH", target_owned=True)
    baseline_calls = list(fake_write_calls)
    response = client.patch(
        f"/books/{synthetic_book}/transactions/synthetic-created-tx",
        headers=patch_headers,
        json={
            "description": "metadata-only regression patch",
            "split_memos": {"synthetic-split": "memo-only regression patch"},
            **immutable_payload,
        },
    )

    assert response.status_code == 422
    assert field_name in str(response.json()["detail"])
    assert fake_write_calls == baseline_calls


def test_synthetic_route_family_stale_owner_writebeta_headers_do_not_fall_through_to_write(
    client,
    auth_headers,
    synthetic_book,
    fake_write_calls,
):
    response = client.post(
        f"/books/{synthetic_book}/transactions",
        headers={
            **auth_headers,
            "X-Owner-Writebeta-Preview-Hash": "owb-prev-stale",
            "X-Owner-Writebeta-Confirmation-Token": "stale-token",
        },
        json=_synthetic_create_payload(),
    )

    assert response.status_code == 403
    assert "active armed owner-writebeta session" in response.json()["detail"]
    assert fake_write_calls == []


def test_synthetic_route_family_fails_closed_for_unowned_patch_delete_previews(client, auth_headers, synthetic_book):
    client.post(f"/books/{synthetic_book}/owner-writebeta/preflight", headers=auth_headers)
    patch_preview = client.post(
        f"/books/{synthetic_book}/owner-writebeta/preview",
        headers=auth_headers,
        json={"operation": "PATCH", "payload_shape": {}, "target_is_write_alpha_owned": False},
    )
    assert patch_preview.status_code == 403

    delete_preview = client.post(
        f"/books/{synthetic_book}/owner-writebeta/preview",
        headers=auth_headers,
        json={"operation": "DELETE", "payload_shape": {}, "target_is_write_alpha_owned": False},
    )
    assert delete_preview.status_code == 403


def test_synthetic_route_family_disabled_defaults_return_403_before_write_service(
    client,
    auth_headers,
    synthetic_book,
    fake_write_calls,
):
    app.dependency_overrides[get_settings] = lambda: READ_ONLY_SETTINGS

    responses = [
        client.post(f"/books/{synthetic_book}/transactions", headers=auth_headers, json=_synthetic_create_payload()),
        client.patch(f"/books/{synthetic_book}/transactions/synthetic-created-tx", headers=auth_headers, json={"description": "blocked"}),
        client.delete(f"/books/{synthetic_book}/transactions/synthetic-created-tx", headers=auth_headers),
    ]

    assert [response.status_code for response in responses] == [403, 403, 403]
    assert all("read-only" in response.json()["detail"] for response in responses)
    assert fake_write_calls == []
