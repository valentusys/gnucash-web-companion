"""Healthcheck and diagnostics endpoint tests."""

import logging

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

import app.database as database_module
import app.diagnostics as diagnostics_module
import app.main as main_module
from app.config import Settings
from app.diagnostics import (
    auth_configuration_posture,
    build_health_payload,
    cors_deployment_posture,
    log_startup_diagnostics,
)
from app.main import app

client = TestClient(app)


def _settings(tmp_path, book_path=None) -> Settings:
    return Settings(
        app_env="test",
        app_database_url=f"sqlite:///{tmp_path / 'app.db'}",
        gnucash_default_book_path=str(book_path or tmp_path / "missing.gnucash.sqlite"),
        jwt_secret="test-health-secret",
        app_admin_password="test-password",
    )


def _in_memory_engine():
    return create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def test_health_returns_richer_non_sensitive_payload(monkeypatch, tmp_path):
    book_path = tmp_path / "sample-book.gnucash.sqlite"
    book_path.write_bytes(b"synthetic test fixture placeholder")
    settings = _settings(tmp_path, book_path)

    monkeypatch.setattr(main_module, "get_settings", lambda: settings)
    monkeypatch.setattr(database_module, "get_settings", lambda: settings)

    response = client.get("/health")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["service"] == "api"
    assert payload["checks"]["app_database"]["reachable"] is True
    assert payload["checks"]["app_database"]["backend"] == "sqlite"
    assert payload["checks"]["app_database"]["database_name"] == "app.db"
    assert payload["warnings"] == []
    assert payload["first_run"]["summary"] == "Read-only first-run prerequisites look configured."
    assert payload["first_run"]["action_required"] == []
    assert payload["first_run"]["checks"]["write_mode"] == {
        "status": "ok",
        "message": "GnuCash writes are disabled; read-only deployment default is active.",
    }
    assert payload["checks"]["cors"] == {
        "wildcard_enabled": True,
        "app_env": "test",
        "development_like_env": True,
        "risk_level": "ok",
        "message": "CORS_ORIGINS uses the development wildcard default. This is acceptable for local development, but narrow it to exact LAN/VPN origins before shared deployment.",
    }
    assert payload["checks"]["auth_configuration"] == {
        "jwt_secret_configured": True,
        "admin_credentials_configured": True,
        "admin_password_hash_configured": False,
        "plaintext_admin_password_configured": True,
        "message": "Login bootstrap configuration is present.",
        "issues": [],
        "safe_next_actions": ["Sign in with the configured local admin account."],
    }
    assert payload["checks"]["default_book"] == {
        "configured": True,
        "exists": True,
        "readable": True,
        "filename": "sample-book.gnucash.sqlite",
        "parent_exists": True,
        "message": "Default GnuCash book file is present.",
    }
    assert payload["checks"]["writes_enabled"] is False

    response_text = response.text
    assert str(tmp_path) not in response_text
    assert "test-health-secret" not in response_text
    assert "test-password" not in response_text


def test_health_explains_missing_default_book_without_full_path(tmp_path):
    settings = _settings(tmp_path)

    payload = build_health_payload(settings, _in_memory_engine())

    assert payload["status"] == "degraded"
    default_book = payload["checks"]["default_book"]
    assert default_book["configured"] is True
    assert default_book["exists"] is False
    assert default_book["readable"] is False
    assert default_book["filename"] == "missing.gnucash.sqlite"
    assert "missing or not mounted" in default_book["message"]
    assert str(tmp_path) not in str(payload)


def test_health_explains_unreadable_default_book_without_full_path(monkeypatch, tmp_path):
    book_path = tmp_path / "unreadable-book.gnucash.sqlite"
    book_path.write_bytes(b"synthetic test fixture placeholder")
    settings = _settings(tmp_path, book_path)
    monkeypatch.setattr(diagnostics_module.os, "access", lambda path, mode: False)

    payload = build_health_payload(settings, _in_memory_engine())

    assert payload["status"] == "degraded"
    default_book = payload["checks"]["default_book"]
    assert default_book["configured"] is True
    assert default_book["exists"] is True
    assert default_book["readable"] is False
    assert default_book["filename"] == "unreadable-book.gnucash.sqlite"
    assert "not readable" in default_book["message"]
    assert "permissions" in default_book["message"]
    assert str(tmp_path) not in str(payload)


def test_auth_configuration_posture_explains_first_run_login_blockers_without_secrets(tmp_path):
    settings = Settings(
        app_env="test",
        app_database_url=f"sqlite:///{tmp_path / 'app.db'}",
        gnucash_default_book_path=str(tmp_path / "sample.gnucash.sqlite"),
        jwt_secret="change-me-use-a-long-random-secret",
        app_admin_password="",
        app_admin_password_hash="",
    )

    posture = auth_configuration_posture(settings)
    payload = build_health_payload(settings, _in_memory_engine())

    assert posture["jwt_secret_configured"] is False
    assert posture["admin_credentials_configured"] is False
    assert "JWT_SECRET is missing" in posture["issues"][0]
    assert "No admin bootstrap credentials" in posture["issues"][1]
    assert "Set JWT_SECRET" in posture["safe_next_actions"][0]
    assert "APP_ADMIN_PASSWORD_HASH or APP_ADMIN_PASSWORD" in posture["safe_next_actions"][1]
    assert payload["status"] == "degraded"
    assert payload["checks"]["auth_configuration"] == posture
    assert "change-me-use-a-long-random-secret" not in str(payload)
    assert str(tmp_path) not in str(payload)


def test_health_first_run_summary_distinguishes_actionable_states_without_sensitive_values(tmp_path):
    private_root = tmp_path / "private" / "nested"
    private_root.mkdir(parents=True)
    settings = Settings(
        app_env="production",
        app_database_url=f"sqlite:///{tmp_path / 'app.db'}",
        gnucash_default_book_path=str(private_root / "owner-book.gnucash.sqlite"),
        jwt_secret="change-me",
        app_admin_password="",
        app_admin_password_hash="",
        cors_origins=["*"],
    )

    payload = build_health_payload(settings, _in_memory_engine())
    first_run = payload["first_run"]

    assert first_run["summary"] == "First-run configuration needs operator action."
    assert first_run["action_required"] == ["jwt_secret", "admin_bootstrap", "default_book", "cors"]
    assert first_run["checks"]["jwt_secret"]["message"] == "JWT_SECRET is missing or still a placeholder. Set a long random value and restart."
    assert "APP_ADMIN_PASSWORD_HASH or APP_ADMIN_PASSWORD is missing" in first_run["checks"]["admin_bootstrap"]["message"]
    assert "missing or not mounted" in first_run["checks"]["default_book"]["message"]
    assert "Narrow CORS_ORIGINS" in first_run["checks"]["cors"]["message"]
    assert first_run["checks"]["write_mode"]["message"] == "GnuCash writes are disabled; read-only deployment default is active."

    payload_text = str(payload)
    assert "change-me" not in payload_text
    assert str(tmp_path) not in payload_text
    assert "owner-book.gnucash.sqlite" in payload_text


def test_cors_posture_warns_for_wildcard_outside_development_like_env(tmp_path):
    settings = Settings(
        app_env="production",
        app_database_url=f"sqlite:///{tmp_path / 'app.db'}",
        gnucash_default_book_path=str(tmp_path / "missing.gnucash.sqlite"),
        jwt_secret="secret-that-must-not-appear",
        app_admin_password="password-that-must-not-appear",
        cors_origins=["*"],
    )

    payload = build_health_payload(settings, _in_memory_engine())

    cors = payload["checks"]["cors"]
    assert cors["wildcard_enabled"] is True
    assert cors["app_env"] == "production"
    assert cors["development_like_env"] is False
    assert cors["risk_level"] == "warning"
    assert "Narrow CORS_ORIGINS to exact localhost, LAN, or VPN browser origins" in cors["message"]
    assert "public internet" in cors["message"]
    assert payload["warnings"] == [cors["message"]]

    payload_text = str(payload)
    assert "secret-that-must-not-appear" not in payload_text
    assert "password-that-must-not-appear" not in payload_text
    assert str(tmp_path) not in payload_text


def test_cors_posture_accepts_narrowed_origins_outside_development(tmp_path):
    settings = Settings(
        app_env="production",
        app_database_url=f"sqlite:///{tmp_path / 'app.db'}",
        gnucash_default_book_path=str(tmp_path / "missing.gnucash.sqlite"),
        jwt_secret="secret-that-must-not-appear",
        app_admin_password="password-that-must-not-appear",
        cors_origins=["https://gnucash.home.arpa", "https://gnucash.vpn.example"],
    )

    cors = cors_deployment_posture(settings)

    assert cors == {
        "wildcard_enabled": False,
        "app_env": "production",
        "development_like_env": False,
        "risk_level": "ok",
        "message": "CORS_ORIGINS is narrowed to configured origins.",
    }


def test_startup_diagnostics_log_is_structured_and_safe(caplog, tmp_path):
    secret = "super-secret-health-token"
    settings = Settings(
        app_env="test",
        app_database_url=f"sqlite:///{tmp_path / 'app.db'}",
        gnucash_default_book_path=str(tmp_path / "missing.gnucash.sqlite"),
        jwt_secret=secret,
        app_admin_password="admin-password-secret",
    )

    with caplog.at_level(logging.INFO, logger="app.diagnostics"):
        log_startup_diagnostics(settings, _in_memory_engine())

    log_text = caplog.text
    assert "startup_diagnostics" in log_text
    assert '"event": "startup_diagnostics"' in log_text
    assert '"status": "degraded"' in log_text
    assert "missing.gnucash.sqlite" in log_text
    assert str(tmp_path) not in log_text
    assert secret not in log_text
    assert "admin-password-secret" not in log_text


def test_startup_logs_warning_for_risky_cors_without_secrets(caplog, tmp_path):
    secret = "super-secret-cors-token"
    settings = Settings(
        app_env="production",
        app_database_url=f"sqlite:///{tmp_path / 'app.db'}",
        gnucash_default_book_path=str(tmp_path / "missing.gnucash.sqlite"),
        jwt_secret=secret,
        app_admin_password="admin-password-secret",
        cors_origins=["*"],
    )

    with caplog.at_level(logging.INFO, logger="app.diagnostics"):
        log_startup_diagnostics(settings, _in_memory_engine())

    log_text = caplog.text
    assert "cors_deployment_warning" in log_text
    assert '\"event\": \"cors_deployment_warning\"' in log_text
    assert '\"wildcard_enabled\": true' in log_text
    assert "Narrow CORS_ORIGINS" in log_text
    assert str(tmp_path) not in log_text
    assert secret not in log_text
    assert "admin-password-secret" not in log_text


def test_startup_logs_first_run_configuration_warning_without_secret_values(caplog, tmp_path):
    placeholder_secret = "change-me"
    settings = Settings(
        app_env="test",
        app_database_url=f"sqlite:///{tmp_path / 'app.db'}",
        gnucash_default_book_path=str(tmp_path / "missing.gnucash.sqlite"),
        jwt_secret=placeholder_secret,
        app_admin_password="",
        app_admin_password_hash="",
    )

    with caplog.at_level(logging.INFO, logger="app.diagnostics"):
        log_startup_diagnostics(settings, _in_memory_engine())

    log_text = caplog.text
    assert "first_run_configuration_warning" in log_text
    assert '\"event\": \"first_run_configuration_warning\"' in log_text
    assert "JWT_SECRET is missing" in log_text
    assert "No admin bootstrap credentials" in log_text
    assert "APP_ADMIN_PASSWORD_HASH or APP_ADMIN_PASSWORD" in log_text
    assert placeholder_secret not in log_text
    assert str(tmp_path) not in log_text
