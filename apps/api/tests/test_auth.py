"""Tests for authentication endpoints and JWT handling."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.config import Settings, get_settings
from app.database import Base
from app.main import app
from app.models import User
from app.routers.auth import get_db
from app.services.auth import (
    AuthConfigurationError,
    create_access_token,
    hash_password,
    require_configured_jwt_secret,
    seed_admin_user,
)

TEST_SETTINGS = Settings(
    app_env="test",
    app_database_url="sqlite:///:memory:",
    jwt_secret="test-secret-key-for-unit-tests-32-bytes-minimum",
    jwt_token_expire_minutes=30,
    app_admin_username="admin",
    app_admin_password="testpassword123",
)


@pytest.fixture
def engine():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def session_factory(engine):
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

    app.dependency_overrides.clear()
    get_settings.cache_clear()


class TestAuthConfiguration:
    def test_rejects_missing_or_placeholder_jwt_secret(self):
        for secret in ["", "change-me", "change-me-use-a-long-random-secret"]:
            with pytest.raises(AuthConfigurationError):
                require_configured_jwt_secret(secret)

    def test_accepts_configured_jwt_secret(self):
        assert (
            require_configured_jwt_secret("test-secret-key-for-unit-tests-32-bytes-minimum")
            == "test-secret-key-for-unit-tests-32-bytes-minimum"
        )


class TestLoginEndpoint:
    def test_successful_login(self, client):
        response = client.post(
            "/auth/login",
            json={"username": "admin", "password": "testpassword123"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["user"]["username"] == "admin"
        assert data["user"]["display_name"] == "Admin"
        assert isinstance(data["user"]["id"], int)

    def test_failed_login_wrong_password(self, client):
        response = client.post(
            "/auth/login",
            json={"username": "admin", "password": "wrongpassword"},
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid username or password"

    def test_failed_login_unknown_user(self, client):
        response = client.post(
            "/auth/login",
            json={"username": "nobody", "password": "testpassword123"},
        )

        assert response.status_code == 401


class TestMeEndpoint:
    def test_me_returns_current_user(self, client):
        login_resp = client.post(
            "/auth/login",
            json={"username": "admin", "password": "testpassword123"},
        )
        token = login_resp.json()["access_token"]

        me_resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

        assert me_resp.status_code == 200
        data = me_resp.json()
        assert data["username"] == "admin"
        assert data["display_name"] == "Admin"
        assert isinstance(data["id"], int)

    def test_me_without_token_returns_401(self, client):
        response = client.get("/auth/me")

        assert response.status_code == 401

    def test_me_with_invalid_token_returns_401(self, client):
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid-token"},
        )

        assert response.status_code == 401

    def test_me_with_expired_token_returns_401(self, client):
        expired_token = create_access_token(
            data={"sub": "1"},
            secret=TEST_SETTINGS.jwt_secret,
            expire_minutes=-1,
        )

        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"},
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid or expired token"


class TestLogoutEndpoint:
    def test_logout_returns_success(self, client):
        response = client.post("/auth/logout")

        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestAdminSeed:
    def test_seed_admin_from_hash_when_user_table_empty(self, session_factory):
        password_hash = hash_password("hashed-secret")
        settings = Settings(
            app_env="test",
            app_database_url="sqlite:///:memory:",
            jwt_secret="test-secret-key-for-unit-tests-32-bytes-minimum",
            app_admin_username="admin",
            app_admin_password_hash=password_hash,
        )
        app.dependency_overrides[get_settings] = lambda: settings
        try:
            with pytest.MonkeyPatch.context() as monkeypatch:
                monkeypatch.setattr("app.services.auth.get_settings", lambda: settings)
                with session_factory() as session:
                    user = seed_admin_user(session)
                    assert user is not None
                    assert user.username == "admin"
                    assert user.is_admin is True
                    assert user.password_hash == password_hash
        finally:
            app.dependency_overrides.clear()

    def test_seed_admin_skips_when_user_exists(self, session_factory):
        with session_factory() as session:
            session.add(
                User(
                    username="existing",
                    display_name="Existing",
                    password_hash=hash_password("secret"),
                )
            )
            session.commit()

            assert seed_admin_user(session) is None
            assert session.query(User).count() == 1
