"""Non-mutating write-alpha readiness inspection helpers.

This module is intentionally read-only. It does not import or construct the
write-capable GnuCash service and performs no backup, lock, audit, or book
mutation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from sqlalchemy import text
from sqlalchemy.engine import Engine, URL, make_url

from app.config import Settings
from app.services.gnucash_book import GnuCashBookService
from app.services.gnucash_exceptions import (
    BookNotConfiguredError,
    BookNotFoundError,
    GnuCashReadError,
)


@dataclass(frozen=True)
class ReadinessCheck:
    """One operator-safe readiness check result."""

    status: str
    ok: bool
    message: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class WriteAlphaReadiness:
    """Redacted write-alpha readiness report."""

    status: str
    ready: bool
    checks: dict[str, ReadinessCheck]
    mutation_performed: bool = False
    limitations: tuple[str, ...] = (
        "Readiness is an operator preflight only; it does not make write-alpha safe for real/private or only-copy books.",
        "Output is redacted: raw configured paths, account names, memos, amounts, and request payloads are not exposed.",
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "ready": self.ready,
            "mutation_performed": self.mutation_performed,
            "checks": {
                name: {
                    "status": check.status,
                    "ok": check.ok,
                    "message": check.message,
                    "details": check.details,
                }
                for name, check in self.checks.items()
            },
            "limitations": list(self.limitations),
        }

    def safe_summary(self) -> str:
        parts = [
            f"status={self.status}",
            f"ready={str(self.ready).lower()}",
            f"mutation_performed={str(self.mutation_performed).lower()}",
        ]
        for name, check in self.checks.items():
            parts.append(f"{name}={check.status}")
        parts.append("paths=redacted")
        return " ".join(parts)


def _ok(message: str, **details: Any) -> ReadinessCheck:
    return ReadinessCheck(status="ok", ok=True, message=message, details=details)


def _blocked(message: str, **details: Any) -> ReadinessCheck:
    return ReadinessCheck(status="blocked", ok=False, message=message, details=details)


def _warning(message: str, **details: Any) -> ReadinessCheck:
    return ReadinessCheck(status="warning", ok=False, message=message, details=details)


def _database_name(settings: Settings) -> str:
    try:
        parsed = make_url(settings.app_database_url)
    except Exception:
        return "<redacted>"
    if isinstance(parsed, str):
        return "<redacted>"
    url: URL = parsed
    if url.get_backend_name() == "sqlite" and url.database not in (None, ":memory:"):
        return Path(url.database).name or "<redacted>"
    return url.get_backend_name()


def _check_app_db(engine: Engine, settings: Settings) -> ReadinessCheck:
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception:
        return _blocked(
            "App metadata DB is not reachable; write-alpha readiness is blocked.",
            database_name=_database_name(settings),
        )
    return _ok(
        "App metadata DB is reachable.",
        database_name=_database_name(settings),
    )


def _book_path_kind(settings: Settings) -> str:
    raw = str(settings.gnucash_default_book_path or "").strip()
    if not raw:
        return "not_configured"
    if "://" in raw:
        return "uri_or_remote"
    path = Path(raw)
    if not path.exists():
        return "missing_file"
    if not path.is_file():
        return "not_file"
    return "local_file"


def _check_backup_dir(settings: Settings) -> ReadinessCheck:
    raw = str(settings.gnucash_default_book_path or "").strip()
    if not raw:
        return _blocked("Default book is not configured, so no derived backup directory can be selected.")
    if "://" in raw:
        return _warning(
            "Default book is not a local file; the local backup directory derivation cannot be confirmed by readiness.",
            backup_policy="not_confirmed_for_uri",
        )
    path = Path(raw)
    parent = path.parent
    if not parent.exists():
        return _blocked(
            "Default book parent directory is missing, so the derived local backup directory is not ready.",
            backup_policy="derived_from_default_book_parent",
        )
    return _ok(
        "Derived local backup directory policy is configured from the default book parent.",
        backup_policy="derived_from_default_book_parent",
    )


def _check_default_book(settings: Settings) -> ReadinessCheck:
    service = GnuCashBookService(
        {"uri_or_path": settings.gnucash_default_book_path, "base_currency": "XXX"}
    )
    try:
        service.check_connection()
    except BookNotConfiguredError:
        return _blocked("Default book is not configured.", path_kind="not_configured")
    except BookNotFoundError:
        return _blocked("Default book is missing or not mounted.", path_kind="missing_file")
    except GnuCashReadError:
        return _blocked("Default book could not be opened read-only by piecash.", path_kind=_book_path_kind(settings))
    except Exception:
        return _blocked("Default book read-only open check failed safely.", path_kind=_book_path_kind(settings))
    return _ok("Default book opened successfully in read-only mode.", path_kind=_book_path_kind(settings))


def inspect_write_alpha_readiness(settings: Settings, engine: Engine) -> WriteAlphaReadiness:
    """Return a redacted non-mutating write-alpha readiness report."""

    app_env = settings.app_env.strip().lower()
    checks = {
        "writes_enabled_flag": (
            _ok("GNUCASH_WRITES_ENABLED is explicitly true for a local write-alpha run.", expected="true")
            if settings.gnucash_writes_enabled
            else _blocked("GNUCASH_WRITES_ENABLED is false; read-only default is active.", expected="true")
        ),
        "app_env_test_gate": (
            _ok("APP_ENV=test gate is satisfied.", expected="test")
            if app_env == "test"
            else _blocked("APP_ENV is not test; write-alpha routes must remain blocked.", expected="test")
        ),
        "backup_dir_configured": _check_backup_dir(settings),
        "app_db_reachable": _check_app_db(engine, settings),
        "default_book_readable": _check_default_book(settings),
        "no_mutation_performed": _ok("Readiness inspection performed no mutation.", mutation="none"),
    }
    ready = all(check.ok for check in checks.values())
    return WriteAlphaReadiness(status="ready" if ready else "blocked", ready=ready, checks=checks)
