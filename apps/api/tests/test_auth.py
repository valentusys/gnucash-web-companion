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
    decode_access_token,
    hash_password,
    require_configured_jwt_secret,
    seed_admin_user,
    verify_password,
)
from app.schemas.users import (
    DisplayNameValidationError,
    PasswordPolicyError,
    normalize_display_name,
    normalize_username,
    validate_password_policy,
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
    def test_successful_login(self, client, session_factory):
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
        assert data["user"]["is_admin"] is True
        assert isinstance(data["user"]["id"], int)
        assert set(data["user"]) == {"id", "username", "display_name", "is_admin"}
        assert "auth_version" not in response.text
        assert "password_hash" not in response.text
        assert "testpassword123" not in response.text
        with session_factory() as session:
            password_hash = session.query(User).filter(User.username == "admin").one().password_hash
        assert password_hash not in response.text
        payload = decode_access_token(data["access_token"], TEST_SETTINGS.jwt_secret)
        assert payload is not None
        assert payload["av"] == 1

    def test_login_normalizes_username(self, client):
        response = client.post(
            "/auth/login",
            json={"username": " ADMIN ", "password": "testpassword123"},
        )

        assert response.status_code == 200
        assert response.json()["user"]["username"] == "admin"

    def test_successful_login_exposes_normal_user_role_flag_only(self, client):
        response = client.post(
            "/auth/login",
            json={"username": "viewer", "password": "viewerpass"},
        )

        assert response.status_code == 200
        user = response.json()["user"]
        assert user["username"] == "viewer"
        assert user["is_admin"] is False
        assert set(user) == {"id", "username", "display_name", "is_admin"}

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

    def test_failed_login_disabled_user_is_generic(self, client, session_factory):
        with session_factory() as session:
            user = session.query(User).filter(User.username == "viewer").one()
            user.is_enabled = False
            session.commit()

        response = client.post(
            "/auth/login",
            json={"username": "viewer", "password": "viewerpass"},
        )

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid username or password"


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
        assert data["is_admin"] is True
        assert isinstance(data["id"], int)
        assert set(data) == {"id", "username", "display_name", "is_admin"}

    def test_me_returns_normal_user_admin_flag_false(self, client):
        login_resp = client.post(
            "/auth/login",
            json={"username": "viewer", "password": "viewerpass"},
        )
        token = login_resp.json()["access_token"]

        me_resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

        assert me_resp.status_code == 200
        data = me_resp.json()
        assert data["username"] == "viewer"
        assert data["is_admin"] is False
        assert set(data) == {"id", "username", "display_name", "is_admin"}

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

    def test_me_rejects_missing_auth_version_token(self, client):
        token = create_access_token(
            data={"sub": "1"},
            secret=TEST_SETTINGS.jwt_secret,
            expire_minutes=30,
        )

        response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid or expired token"

    def test_me_rejects_non_integer_auth_version_token(self, client):
        token = create_access_token(
            data={"sub": "1", "av": "1"},
            secret=TEST_SETTINGS.jwt_secret,
            expire_minutes=30,
        )

        response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid or expired token"

    def test_me_rejects_mismatched_auth_version_token(self, client):
        token = create_access_token(
            data={"sub": "1", "av": 2},
            secret=TEST_SETTINGS.jwt_secret,
            expire_minutes=30,
        )

        response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid or expired token"

    def test_me_rejects_disabled_user_on_next_request(self, client, session_factory):
        login_resp = client.post(
            "/auth/login",
            json={"username": "viewer", "password": "viewerpass"},
        )
        token = login_resp.json()["access_token"]
        with session_factory() as session:
            user = session.query(User).filter(User.username == "viewer").one()
            user.is_enabled = False
            session.commit()

        me_resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

        assert me_resp.status_code == 401
        assert me_resp.json()["detail"] == "Invalid or expired token"

    def test_me_rejects_auth_version_change_on_next_request(self, client, session_factory):
        login_resp = client.post(
            "/auth/login",
            json={"username": "viewer", "password": "viewerpass"},
        )
        token = login_resp.json()["access_token"]
        with session_factory() as session:
            user = session.query(User).filter(User.username == "viewer").one()
            user.auth_version += 1
            session.commit()

        me_resp = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

        assert me_resp.status_code == 401
        assert me_resp.json()["detail"] == "Invalid or expired token"


class TestUserCredentialHelpers:
    def test_display_name_normalization_and_bounds(self):
        assert normalize_display_name("  Ａlice  ") == "Alice"
        with pytest.raises(DisplayNameValidationError):
            normalize_display_name("")
        with pytest.raises(DisplayNameValidationError):
            normalize_display_name("A" * 101)
        with pytest.raises(DisplayNameValidationError):
            normalize_display_name("Alice\x00Admin")

    def test_password_policy_accepts_valid_secret(self):
        validate_password_policy("ValidPass123!", normalize_username("valid-user"))

    @pytest.mark.parametrize(
        "password,username",
        [
            ("Short1!", "valid-user"),
            ("A" * 129, "valid-user"),
            ("Aa1!" + "é" * 35, "valid-user"),
            ("abcdefghijkl", "valid-user"),
            ("Password1234", "valid-user"),
            (" ABCDEFGHIJKL ", "abcdefghijkl"),
        ],
    )
    def test_password_policy_rejects_boundaries_classes_weak_and_username(
        self, password, username
    ):
        with pytest.raises(PasswordPolicyError):
            validate_password_policy(password, normalize_username(username))

    def test_hash_password_uses_bcrypt_cost_12_and_verifies_without_leaking_plaintext(self):
        password = "ValidPass123!"
        hashed = hash_password(password)

        assert hashed != password
        assert password not in hashed
        assert hashed.split("$")[2] == "12"
        assert verify_password(password, hashed)


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
                    assert user.username_normalized == "admin"
                    assert user.is_admin is True
                    assert user.is_enabled is True
                    assert user.auth_version == 1
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
