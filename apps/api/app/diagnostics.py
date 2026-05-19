"""Safe startup and health diagnostics for self-hosted deployments."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path
from typing import Any, cast

from sqlalchemy import text
from sqlalchemy.engine import Engine, URL, make_url

from app.config import Settings
from app.services.auth import INSECURE_JWT_SECRET_VALUES

logger = logging.getLogger(__name__)

DEVELOPMENT_LIKE_ENVS = {"dev", "development", "local", "test", "testing"}


def _is_development_like_env(app_env: str) -> bool:
    """Return whether APP_ENV is local/development/test-like."""
    return app_env.strip().lower() in DEVELOPMENT_LIKE_ENVS


def cors_deployment_posture(settings: Settings) -> dict[str, Any]:
    """Return a safe CORS deployment-posture diagnostic."""
    origins = [origin.strip() for origin in settings.cors_origins]
    wildcard_enabled = "*" in origins
    development_like = _is_development_like_env(settings.app_env)
    risky = wildcard_enabled and not development_like

    if risky:
        message = (
            "CORS_ORIGINS allows all origins while APP_ENV is not development-like. "
            "Narrow CORS_ORIGINS to exact localhost, LAN, or VPN browser origins before shared deployment; "
            "do not expose this pre-alpha app directly to the public internet."
        )
    elif wildcard_enabled:
        message = (
            "CORS_ORIGINS uses the development wildcard default. This is acceptable for local development, "
            "but narrow it to exact LAN/VPN origins before shared deployment."
        )
    else:
        message = "CORS_ORIGINS is narrowed to configured origins."

    return {
        "wildcard_enabled": wildcard_enabled,
        "app_env": settings.app_env,
        "development_like_env": development_like,
        "risk_level": "warning" if risky else "ok",
        "message": message,
    }


def _safe_book_path_status(path_value: str) -> dict[str, Any]:
    """Return non-sensitive default-book diagnostics without exposing full paths."""
    if not path_value:
        return {
            "configured": False,
            "exists": False,
            "readable": False,
            "filename": None,
            "parent_exists": False,
            "message": "GNUCASH_DEFAULT_BOOK_PATH is not configured.",
        }

    path = Path(path_value)
    exists = path.is_file()
    parent_exists = path.parent.exists()
    readable = exists and os.access(path, os.R_OK)

    if exists and not readable:
        message = (
            "Default GnuCash book file exists but is not readable by this runtime. "
            "Check host/container file permissions and mount ownership."
        )
    elif exists:
        message = "Default GnuCash book file is present."
    else:
        message = "Default GnuCash book file is missing or not mounted. Check GNUCASH_DEFAULT_BOOK_PATH and the books volume."

    return {
        "configured": True,
        "exists": exists,
        "readable": readable,
        "filename": path.name,
        "parent_exists": parent_exists,
        "message": message,
    }


def auth_configuration_posture(settings: Settings) -> dict[str, Any]:
    """Return safe login/JWT bootstrap diagnostics without exposing secrets."""
    jwt_secret_configured = settings.jwt_secret.strip() not in INSECURE_JWT_SECRET_VALUES
    admin_password_hash_configured = bool(settings.app_admin_password_hash.strip())
    admin_password_configured = bool(settings.app_admin_password.strip())
    admin_credentials_configured = admin_password_hash_configured or admin_password_configured

    issues: list[str] = []
    safe_next_actions: list[str] = []
    if not jwt_secret_configured:
        issues.append("JWT_SECRET is missing or still uses a placeholder value.")
        safe_next_actions.append("Set JWT_SECRET to a long random value in the local .env/deployment environment.")
    if not admin_credentials_configured:
        issues.append("No admin bootstrap credentials are configured.")
        safe_next_actions.append("Set APP_ADMIN_PASSWORD_HASH or APP_ADMIN_PASSWORD for first-run admin bootstrap.")

    if not issues:
        message = "Login bootstrap configuration is present."
        safe_next_actions.append("Sign in with the configured local admin account.")
    else:
        message = "Login is not fully configured for first run. Fix the listed environment settings and restart the service."

    return {
        "jwt_secret_configured": jwt_secret_configured,
        "admin_credentials_configured": admin_credentials_configured,
        "admin_password_hash_configured": admin_password_hash_configured,
        "plaintext_admin_password_configured": admin_password_configured,
        "message": message,
        "issues": issues,
        "safe_next_actions": safe_next_actions,
    }


def _safe_app_database_config(database_url: str) -> dict[str, Any]:
    """Summarize app DB configuration without returning credentials or file paths."""
    url = cast(URL, make_url(database_url))
    backend = url.get_backend_name()
    database_name = None
    if backend == "sqlite" and url.database:
        database_name = Path(url.database).name

    return {
        "backend": backend,
        "database_name": database_name,
        "configured": bool(database_url),
    }


def check_app_database(engine: Engine) -> dict[str, Any]:
    """Probe app metadata database reachability without exposing connection details."""
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception as exc:  # pragma: no cover - exact DB driver errors vary
        return {
            "reachable": False,
            "message": "App metadata database is not reachable.",
            "error_type": exc.__class__.__name__,
        }

    return {
        "reachable": True,
        "message": "App metadata database is reachable.",
    }


def build_health_payload(settings: Settings, engine: Engine) -> dict[str, Any]:
    """Build the public health payload using only non-sensitive diagnostics."""
    default_book = _safe_book_path_status(settings.gnucash_default_book_path)
    cors = cors_deployment_posture(settings)
    auth_config = auth_configuration_posture(settings)
    app_database = {
        **_safe_app_database_config(settings.app_database_url),
        **check_app_database(engine),
    }

    degraded = (
        not default_book["exists"]
        or not default_book["readable"]
        or not app_database["reachable"]
        or not auth_config["jwt_secret_configured"]
        or not auth_config["admin_credentials_configured"]
    )
    warnings = [cors["message"]] if cors["risk_level"] == "warning" else []
    warnings.extend(auth_config["issues"])

    return {
        "status": "degraded" if degraded else "ok",
        "service": "api",
        "warnings": warnings,
        "checks": {
            "app_database": app_database,
            "auth_configuration": auth_config,
            "cors": cors,
            "default_book": default_book,
            "writes_enabled": settings.gnucash_writes_enabled,
        },
    }


def startup_diagnostics(settings: Settings, engine: Engine) -> dict[str, Any]:
    """Return structured, safe diagnostics for startup logging."""
    health = build_health_payload(settings, engine)
    return {
        "event": "startup_diagnostics",
        "service": "api",
        "app_env": settings.app_env,
        "status": health["status"],
        "checks": health["checks"],
    }


def log_startup_diagnostics(settings: Settings, engine: Engine) -> None:
    """Log startup diagnostics as a single safe JSON object."""
    diagnostics = startup_diagnostics(settings, engine)
    logger.info(
        "startup_diagnostics %s",
        json.dumps(diagnostics, sort_keys=True),
    )
    cors = diagnostics["checks"]["cors"]
    if cors["risk_level"] == "warning":
        logger.warning(
            "cors_deployment_warning %s",
            json.dumps(
                {
                    "event": "cors_deployment_warning",
                    "service": "api",
                    "app_env": settings.app_env,
                    "wildcard_enabled": cors["wildcard_enabled"],
                    "message": cors["message"],
                },
                sort_keys=True,
            ),
        )
    auth_config = diagnostics["checks"]["auth_configuration"]
    if auth_config["issues"]:
        logger.warning(
            "first_run_configuration_warning %s",
            json.dumps(
                {
                    "event": "first_run_configuration_warning",
                    "service": "api",
                    "issues": auth_config["issues"],
                    "safe_next_actions": auth_config["safe_next_actions"],
                },
                sort_keys=True,
            ),
        )
