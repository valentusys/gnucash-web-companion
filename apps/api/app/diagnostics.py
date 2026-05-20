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
            "path_kind": "not_configured",
            "message": "GNUCASH_DEFAULT_BOOK_PATH is not configured.",
            "safe_next_actions": [
                "Set GNUCASH_DEFAULT_BOOK_PATH to the container-visible default book path.",
                "Mount the books volume from the host; do not upload or browse books through the web UI.",
            ],
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
        path_kind = "unreadable_file"
        safe_next_actions = [
            "Check host/container file permissions and mount ownership for the books volume.",
            "Keep using a synthetic or disposable copy until the read-only path is verified.",
        ]
    elif exists:
        message = "Default GnuCash book file is present."
        path_kind = "local_file"
        safe_next_actions = [
            "Continue with the normal read-only login flow.",
            "Use GnuCash Desktop for edits; web writes remain disabled by default.",
        ]
    else:
        message = "Default GnuCash book file is missing or not mounted. Check GNUCASH_DEFAULT_BOOK_PATH and the books volume."
        path_kind = "missing_file"
        safe_next_actions = [
            "Verify the configured default book is mounted into the API container.",
            "Check GNUCASH_DEFAULT_BOOK_PATH and the books volume without exposing host paths in the UI.",
        ]

    return {
        "configured": True,
        "exists": exists,
        "readable": readable,
        "filename": path.name,
        "parent_exists": parent_exists,
        "path_kind": path_kind,
        "message": message,
        "safe_next_actions": safe_next_actions,
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

    first_run_checks = {
        "jwt_secret": {
            "status": "ok" if auth_config["jwt_secret_configured"] else "action_required",
            "message": (
                "JWT_SECRET is configured."
                if auth_config["jwt_secret_configured"]
                else "JWT_SECRET is missing or still a placeholder. Set a long random value and restart."
            ),
            "safe_next_actions": (
                ["No action needed for JWT_SECRET."]
                if auth_config["jwt_secret_configured"]
                else ["Set JWT_SECRET to a long random value in the local .env/deployment environment and restart."]
            ),
        },
        "admin_bootstrap": {
            "status": "ok" if auth_config["admin_credentials_configured"] else "action_required",
            "message": (
                "Admin bootstrap credentials are configured."
                if auth_config["admin_credentials_configured"]
                else "APP_ADMIN_PASSWORD_HASH or APP_ADMIN_PASSWORD is missing; first-run admin login cannot be seeded."
            ),
            "safe_next_actions": (
                ["Sign in with the configured local admin account."]
                if auth_config["admin_credentials_configured"]
                else ["Set APP_ADMIN_PASSWORD_HASH or APP_ADMIN_PASSWORD for first-run admin bootstrap and restart."]
            ),
        },
        "default_book": {
            "status": "ok" if default_book["exists"] and default_book["readable"] else "action_required",
            "message": default_book["message"],
            "safe_next_actions": default_book["safe_next_actions"],
        },
        "cors": {
            "status": "action_required" if cors["risk_level"] == "warning" else "ok",
            "message": cors["message"],
            "safe_next_actions": (
                ["Narrow CORS_ORIGINS to exact localhost, LAN, or VPN browser origins before shared deployment."]
                if cors["risk_level"] == "warning"
                else ["No CORS action needed for this environment posture."]
            ),
        },
        "write_mode": {
            "status": "warning" if settings.gnucash_writes_enabled else "ok",
            "message": (
                "Experimental writes are explicitly enabled for this runtime. Use only APP_ENV=test with disposable copies."
                if settings.gnucash_writes_enabled
                else "GnuCash writes are disabled; read-only deployment default is active."
            ),
            "safe_next_actions": (
                ["Return GNUCASH_WRITES_ENABLED to false unless this is an explicit APP_ENV=test disposable write-alpha run."]
                if settings.gnucash_writes_enabled
                else ["Keep GNUCASH_WRITES_ENABLED=false for the default read-only first run."]
            ),
        },
    }
    first_run_action_required = [key for key, check in first_run_checks.items() if check["status"] == "action_required"]

    return {
        "status": "degraded" if degraded else "ok",
        "service": "api",
        "warnings": warnings,
        "first_run": {
            "summary": (
                "First-run configuration needs operator action."
                if first_run_action_required
                else "Read-only first-run prerequisites look configured."
            ),
            "action_required": first_run_action_required,
            "checks": first_run_checks,
        },
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
