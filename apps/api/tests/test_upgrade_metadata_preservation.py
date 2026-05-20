"""Synthetic upgrade app-metadata preservation regression tests.

These tests pin the startup/seed behavior relied on by the Phase 214 Docker
upgrade smoke: an existing app metadata DB from a previous tag must remain
readable and must not be overwritten by current startup seeding.
"""

from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import Settings
from app.database import Base
from app.models import AuditLog, Book, User, UserBookAccess
from app.services.auth import seed_admin_user, verify_password, hash_password
from app.services.seed import seed_admin_default_book_access, seed_default_book


TEST_SETTINGS = Settings(
    app_env="test",
    app_database_url="sqlite:///:memory:",
    jwt_secret="test-secret-key-for-upgrade-tests-32-bytes",
    app_admin_username="admin",
    app_admin_password="new-bootstrap-password-that-must-not-replace-existing",
    gnucash_default_book_path="/data/books/main.gnucash.sqlite",
    gnucash_writes_enabled=False,
)


def _session_factory():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)


def test_upgrade_seed_functions_are_idempotent_for_existing_user_book_access(monkeypatch):
    monkeypatch.setattr("app.services.auth.get_settings", lambda: TEST_SETTINGS)
    session_factory = _session_factory()

    with session_factory() as session:
        admin = User(
            username="admin",
            display_name="Existing Admin",
            password_hash=hash_password("previous-dummy-password"),
            is_admin=True,
        )
        default_book = Book(
            name="Existing Synthetic Main",
            storage_type="sqlite",
            uri_or_path="/data/books/main.gnucash.sqlite",
            base_currency="USD",
            is_default=True,
        )
        session.add_all([admin, default_book])
        session.commit()
        session.refresh(admin)
        session.refresh(default_book)
        session.add(UserBookAccess(user_id=admin.id, book_id=default_book.id, role="editor"))
        session.add(
            AuditLog(
                user_id=admin.id,
                book_id=default_book.id,
                action="transaction.create",
                payload_json='{"result":"success","transaction_id":"phase-214-legacy-synthetic"}',
            )
        )
        session.commit()
        original_user_id = admin.id
        original_book_id = default_book.id

    with session_factory() as session:
        returned_book = seed_default_book(session, "/data/books/replacement-should-not-win.gnucash.sqlite")
        seeded_user = seed_admin_user(session)
        seeded_access = seed_admin_default_book_access(session)

        users = session.query(User).all()
        books = session.query(Book).all()
        access_rows = session.query(UserBookAccess).all()
        audit_rows = session.query(AuditLog).all()

        assert returned_book is not None
        assert returned_book.id == original_book_id
        assert seeded_user is None
        assert seeded_access is not None
        assert seeded_access.role == "editor"
        assert len(users) == 1
        assert users[0].id == original_user_id
        assert users[0].display_name == "Existing Admin"
        assert verify_password("previous-dummy-password", users[0].password_hash)
        assert not verify_password(TEST_SETTINGS.app_admin_password, users[0].password_hash)
        assert len(books) == 1
        assert books[0].id == original_book_id
        assert books[0].uri_or_path == "/data/books/main.gnucash.sqlite"
        assert books[0].is_default is True
        assert len(access_rows) == 1
        assert access_rows[0].role == "editor"
        assert len(audit_rows) == 1
        assert audit_rows[0].action == "transaction.create"


def test_upgrade_seed_adds_missing_access_without_replacing_preserved_metadata(monkeypatch):
    monkeypatch.setattr("app.services.auth.get_settings", lambda: TEST_SETTINGS)
    session_factory = _session_factory()

    with session_factory() as session:
        admin = User(
            username="admin",
            display_name="Existing Admin",
            password_hash=hash_password("previous-dummy-password"),
            is_admin=True,
        )
        default_book = Book(
            name="Existing Synthetic Main",
            storage_type="sqlite",
            uri_or_path="/data/books/main.gnucash.sqlite",
            is_default=True,
        )
        session.add_all([admin, default_book])
        session.commit()
        session.refresh(admin)
        session.refresh(default_book)
        original_user_id = admin.id
        original_book_id = default_book.id

    with session_factory() as session:
        assert seed_default_book(session, "/data/books/other.gnucash.sqlite").id == original_book_id
        assert seed_admin_user(session) is None
        access = seed_admin_default_book_access(session)

        assert access is not None
        assert access.user_id == original_user_id
        assert access.book_id == original_book_id
        assert access.role == "owner"
        assert session.query(User).count() == 1
        assert session.query(Book).count() == 1
        assert session.query(UserBookAccess).count() == 1
