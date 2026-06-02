"""Non-mutating write-alpha readiness inspection helpers.

This module is intentionally read-only. It does not import or construct the
write-capable GnuCash service and performs no backup, lock, audit, or book
mutation.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Mapping

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
    mutation_plan: dict[str, Any] = field(
        default_factory=lambda: {
            "authorized": False,
            "create_count": 0,
            "patch_count": 0,
            "delete_count": 0,
            "reason": "readiness inspection never authorizes mutations",
        }
    )
    limitations: tuple[str, ...] = (
        "Readiness is an operator preflight only; it does not make write-alpha safe for real/private or only-copy books.",
        "Output is redacted: raw configured paths, account names, memos, amounts, and request payloads are not exposed.",
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "ready": self.ready,
            "mutation_performed": self.mutation_performed,
            "mutation_plan": self.mutation_plan,
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
            "authorized_mutations=create:0,patch:0,delete:0",
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


_ALLOWED_FIXTURE_CLASSIFICATIONS = frozenset(
    {
        "copied-disposable",
        "copied-restorable",
        "synthetic-disposable",
        "synthetic-or-copied-disposable-only",
    }
)
_ALLOWED_BACKUP_LOCATIONS = frozenset({"outside-git", "approved-temp-area"})
_SENSITIVE_EVIDENCE_KEYS = frozenset(
    {
        "raw_path",
        "private_path",
        "book_path",
        "backup_path",
        "account_name",
        "transaction_description",
        "memo",
        "amount",
        "balance",
        "payload",
        "splits",
    }
)


def _bool_check(evidence: Mapping[str, Any], key: str, ok_message: str, blocked_message: str) -> ReadinessCheck:
    return _ok(ok_message, marker=key) if evidence.get(key) is True else _blocked(blocked_message, marker=key)


def _text_marker_check(
    evidence: Mapping[str, Any],
    key: str,
    required_terms: tuple[str, ...],
    ok_message: str,
    blocked_message: str,
) -> ReadinessCheck:
    note = str(evidence.get(key, "")).strip().lower()
    if note and all(term in note for term in required_terms):
        return _ok(ok_message, marker=key)
    return _blocked(blocked_message, marker=key)


def validate_backup_restore_readiness_evidence(evidence: Mapping[str, Any]) -> WriteAlphaReadiness:
    """Validate redacted backup/restore readiness evidence without mutating files.

    This is a fail-closed checklist for future controlled-write packages. It
    accepts only bounded markers and intentionally ignores/raw-redacts evidence
    values so private paths, account names, memos, amounts, and payloads never
    appear in the returned report.
    """

    classification = str(evidence.get("fixture_classification", "")).strip().lower()
    backup_location = str(evidence.get("backup_location", "")).strip().lower()
    note = str(evidence.get("recovery_hard_stop_note", "")).strip().lower()
    sensitive_keys_present = sorted(key for key in _SENSITIVE_EVIDENCE_KEYS if key in evidence)
    private_raw_included = evidence.get("private_raw_evidence_included") is True or bool(sensitive_keys_present)

    checks = {
        "fixture_classification": (
            _ok("Evidence identifies only a copied/disposable or synthetic/disposable fixture.", allowed="copied_or_synthetic_disposable")
            if classification in _ALLOWED_FIXTURE_CLASSIFICATIONS
            else _blocked("Evidence must identify a copied/disposable or synthetic/disposable fixture.", allowed="copied_or_synthetic_disposable")
        ),
        "backup_location": (
            _ok("Backup evidence is outside git or in an approved temp area.", allowed="outside_git_or_approved_temp")
            if backup_location in _ALLOWED_BACKUP_LOCATIONS
            else _blocked("Backup evidence must be outside git or in an approved temp area.", allowed="outside_git_or_approved_temp")
        ),
        "restore_hash_verified": _bool_check(
            evidence,
            "restore_hash_verified",
            "Restore checksum/hash verification marker is present.",
            "Restore checksum/hash verification marker is missing.",
        ),
        "restore_row_count_verified": _bool_check(
            evidence,
            "restore_row_count_verified",
            "Restore bounded row-count verification marker is present.",
            "Restore bounded row-count verification marker is missing.",
        ),
        "restore_schema_marker_verified": _bool_check(
            evidence,
            "restore_schema_marker_verified",
            "Restore schema marker verification is present.",
            "Restore schema marker verification is missing.",
        ),
        "private_raw_evidence_absent": (
            _blocked(
                "Evidence includes private/raw fields or explicitly reports private/raw evidence; redact before proceeding.",
                sensitive_key_count=len(sensitive_keys_present),
            )
            if private_raw_included
            else _ok("Evidence reports no private paths, raw account/memo/amount data, or payloads.", sensitive_key_count=0)
        ),
        "default_writes_disabled": _bool_check(
            evidence,
            "default_writes_disabled",
            "Default write-disabled posture marker is present.",
            "Default write-disabled posture marker is missing.",
        ),
        "recovery_hard_stop_note": (
            _ok("Recovery/hard-stop note is present.", marker="recovery_hard_stop_note")
            if ("stop" in note or "hard-stop" in note) and "recover" in note
            else _blocked("Recovery/hard-stop note must tell the operator to stop and recover before further writes.", marker="recovery_hard_stop_note")
        ),
        "abort_after_failed_restore_or_readback_or_audit": _bool_check(
            evidence,
            "abort_after_failed_restore_or_readback_or_audit",
            "Abort/hard-stop marker after failed restore, read-back, or audit is present.",
            "Abort/hard-stop marker after failed restore, read-back, or audit is missing.",
        ),
        "backup_preservation_note": _text_marker_check(
            evidence,
            "backup_preservation_note",
            ("preserve", "backup"),
            "Backup preservation note is present.",
            "Backup preservation note must tell the operator to preserve recovery backups/evidence.",
        ),
        "no_retry_same_copy_without_recovery": _bool_check(
            evidence,
            "no_retry_same_copy_without_recovery",
            "No-retry-on-same-copy-without-recovery marker is present.",
            "No-retry-on-same-copy-without-recovery marker is missing.",
        ),
        "maintainer_review_or_owner_escalation": _bool_check(
            evidence,
            "maintainer_review_or_owner_escalation",
            "Maintainer review or owner escalation marker is present.",
            "Maintainer review or owner escalation marker is missing.",
        ),
        "default_disabled_reset_probe": _bool_check(
            evidence,
            "default_disabled_reset_probe",
            "Default write-disabled reset/probe marker is present.",
            "Default write-disabled reset/probe marker is missing.",
        ),
        "no_mutation_performed": _ok("Checklist validation performed no mutation.", mutation="none"),
    }
    ready = all(check.ok for check in checks.values())
    return WriteAlphaReadiness(status="ready" if ready else "blocked", ready=ready, checks=checks)
