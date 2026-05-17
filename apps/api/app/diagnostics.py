"""Safe startup and health diagnostics for self-hosted deployments."""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, cast

from sqlalchemy import text
from sqlalchemy.engine import Engine, URL, make_url

from app.config import Settings

logger = logging.getLogger(__name__)


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
    readable = exists

    return {
        "configured": True,
        "exists": exists,
        "readable": readable,
        "filename": path.name,
        "parent_exists": parent_exists,
        "message": (
            "Default GnuCash book file is present."
            if exists
            else "Default GnuCash book file is missing or not mounted. Check GNUCASH_DEFAULT_BOOK_PATH and the books volume."
        ),
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
    app_database = {
        **_safe_app_database_config(settings.app_database_url),
        **check_app_database(engine),
    }

    degraded = not default_book["exists"] or not app_database["reachable"]

    return {
        "status": "degraded" if degraded else "ok",
        "service": "api",
        "checks": {
            "app_database": app_database,
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
    logger.info(
        "startup_diagnostics %s",
        json.dumps(startup_diagnostics(settings, engine), sort_keys=True),
    )
