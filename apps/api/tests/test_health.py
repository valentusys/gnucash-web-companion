"""Healthcheck and diagnostics endpoint tests."""

import logging

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

import app.database as database_module
import app.main as main_module
from app.config import Settings
from app.diagnostics import build_health_payload, log_startup_diagnostics
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
    assert default_book["filename"] == "missing.gnucash.sqlite"
    assert "missing or not mounted" in default_book["message"]
    assert str(tmp_path) not in str(payload)


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
