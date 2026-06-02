"""Regression tests for non-mutating write-alpha readiness inspection."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

from app.config import Settings
from app.write_alpha_readiness import (
    validate_backup_restore_readiness_evidence,
    inspect_write_alpha_readiness,
)

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "scripts" / "write_alpha_readiness.py"
FIXTURE_BOOK = Path(__file__).resolve().parent / "fixtures" / "test-book.gnucash.sqlite"

spec = importlib.util.spec_from_file_location("write_alpha_readiness_cli", SCRIPT_PATH)
assert spec is not None
readiness_cli = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["write_alpha_readiness_cli"] = readiness_cli
spec.loader.exec_module(readiness_cli)


def _engine():
    return create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


def _settings(tmp_path: Path, *, writes: bool, app_env: str, book_path: Path | None = None) -> Settings:
    return Settings(
        app_env=app_env,
        app_database_url=f"sqlite:///{tmp_path / 'private-app-db' / 'app.db'}",
        gnucash_default_book_path=str(book_path or FIXTURE_BOOK),
        jwt_secret="test-readiness-secret",
        app_admin_password="test-readiness-password",
        gnucash_writes_enabled=writes,
    )


def test_readiness_ready_when_explicit_write_alpha_gates_and_book_are_ok(tmp_path):
    private_root = tmp_path / "private"
    copied_fixture = private_root / "copied-test-book.gnucash.sqlite"
    private_root.mkdir()
    copied_fixture.write_bytes(FIXTURE_BOOK.read_bytes())
    settings = _settings(tmp_path, writes=True, app_env="test", book_path=copied_fixture)

    result = inspect_write_alpha_readiness(settings, _engine())
    payload = result.to_dict()
    summary = result.safe_summary()

    assert result.ready is True
    assert payload["status"] == "ready"
    assert payload["mutation_performed"] is False
    assert payload["mutation_plan"]["authorized"] is False
    assert payload["mutation_plan"]["create_count"] == 0
    assert payload["mutation_plan"]["patch_count"] == 0
    assert payload["mutation_plan"]["delete_count"] == 0
    assert payload["checks"]["writes_enabled_flag"]["status"] == "ok"
    assert payload["checks"]["app_env_test_gate"]["status"] == "ok"
    assert payload["checks"]["backup_dir_configured"]["status"] == "ok"
    assert payload["checks"]["app_db_reachable"]["status"] == "ok"
    assert payload["checks"]["default_book_readable"]["status"] == "ok"
    assert "mutation_performed=false" in summary
    assert str(tmp_path) not in str(payload)
    assert str(copied_fixture) not in str(payload)
    assert "private" not in summary
    assert "copied-test-book" not in summary


def test_readiness_works_when_writes_disabled_and_reports_blocked_without_path_leak(tmp_path):
    private_missing = tmp_path / "private" / "owner-book.gnucash.sqlite"
    settings = _settings(tmp_path, writes=False, app_env="test", book_path=private_missing)

    result = inspect_write_alpha_readiness(settings, _engine())
    payload = result.to_dict()

    assert result.ready is False
    assert payload["status"] == "blocked"
    assert payload["checks"]["writes_enabled_flag"]["status"] == "blocked"
    assert payload["checks"]["app_env_test_gate"]["status"] == "ok"
    assert payload["checks"]["default_book_readable"]["details"]["path_kind"] == "missing_file"
    assert payload["checks"]["no_mutation_performed"]["details"]["mutation"] == "none"
    assert str(tmp_path) not in str(payload)
    assert "owner-book.gnucash.sqlite" not in str(payload)


def test_readiness_blocks_non_test_app_env_even_when_writes_enabled(tmp_path):
    settings = _settings(tmp_path, writes=True, app_env="production", book_path=FIXTURE_BOOK)

    result = inspect_write_alpha_readiness(settings, _engine())
    payload = result.to_dict()

    assert result.ready is False
    assert payload["checks"]["writes_enabled_flag"]["status"] == "ok"
    assert payload["checks"]["app_env_test_gate"]["status"] == "blocked"
    assert payload["checks"]["app_env_test_gate"]["details"] == {"expected": "test"}
    assert "production" not in result.safe_summary()


def test_readiness_does_not_construct_write_service(tmp_path, monkeypatch):
    import app.services.gnucash_write as write_module

    def fail_if_constructed(*args, **kwargs):  # noqa: ANN002, ANN003
        raise AssertionError("GnuCashWriteService must not be constructed by readiness")

    monkeypatch.setattr(write_module, "GnuCashWriteService", fail_if_constructed)
    settings = _settings(tmp_path, writes=True, app_env="test", book_path=FIXTURE_BOOK)

    result = inspect_write_alpha_readiness(settings, _engine())

    assert result.to_dict()["checks"]["no_mutation_performed"]["status"] == "ok"


def test_cli_json_output_is_redacted_and_uses_nonzero_for_not_ready(tmp_path, monkeypatch):
    private_missing = tmp_path / "private" / "missing.gnucash.sqlite"
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("GNUCASH_WRITES_ENABLED", "false")
    monkeypatch.setenv("APP_DATABASE_URL", f"sqlite:///{tmp_path / 'app' / 'app.db'}")
    monkeypatch.setenv("GNUCASH_DEFAULT_BOOK_PATH", str(private_missing))
    monkeypatch.setenv("JWT_SECRET", "test-readiness-secret")
    monkeypatch.setenv("APP_ADMIN_PASSWORD", "test-readiness-password")

    result = subprocess.run(
        ["python3", str(SCRIPT_PATH), "--json"],
        cwd=REPO_ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    assert result.returncode == 2
    payload = json.loads(result.stdout)
    assert payload["status"] == "blocked"
    assert payload["mutation_performed"] is False
    assert payload["mutation_plan"] == {
        "authorized": False,
        "create_count": 0,
        "patch_count": 0,
        "delete_count": 0,
        "reason": "readiness inspection never authorizes mutations",
    }
    assert str(tmp_path) not in result.stdout
    assert "missing.gnucash.sqlite" not in result.stdout
    assert result.stderr == ""


def _complete_backup_restore_evidence() -> dict[str, object]:
    return {
        "fixture_classification": "copied-disposable",
        "backup_location": "outside-git",
        "restore_hash_verified": True,
        "restore_row_count_verified": True,
        "restore_schema_marker_verified": True,
        "private_raw_evidence_included": False,
        "default_writes_disabled": True,
        "recovery_hard_stop_note": "stop and recover from the verified backup before any further write attempt",
    }


def test_backup_restore_readiness_evidence_requires_all_fail_closed_markers():
    evidence = _complete_backup_restore_evidence()

    result = validate_backup_restore_readiness_evidence(evidence)
    payload = result.to_dict()

    assert result.ready is True
    assert payload["checks"]["fixture_classification"]["status"] == "ok"
    assert payload["checks"]["backup_location"]["status"] == "ok"
    assert payload["checks"]["restore_hash_verified"]["status"] == "ok"
    assert payload["checks"]["restore_row_count_verified"]["status"] == "ok"
    assert payload["checks"]["restore_schema_marker_verified"]["status"] == "ok"
    assert payload["checks"]["private_raw_evidence_absent"]["status"] == "ok"
    assert payload["checks"]["default_writes_disabled"]["status"] == "ok"
    assert payload["checks"]["recovery_hard_stop_note"]["status"] == "ok"
    assert payload["mutation_plan"]["authorized"] is False
    assert "authorized_mutations=create:0,patch:0,delete:0" in result.safe_summary()


def test_backup_restore_readiness_evidence_blocks_missing_restore_schema_marker():
    evidence = _complete_backup_restore_evidence()
    evidence.pop("restore_schema_marker_verified")

    result = validate_backup_restore_readiness_evidence(evidence)
    payload = result.to_dict()

    assert result.ready is False
    assert payload["status"] == "blocked"
    assert payload["checks"]["restore_schema_marker_verified"]["status"] == "blocked"
    assert "restore_schema_marker_verified=blocked" in result.safe_summary()


def test_backup_restore_readiness_evidence_blocks_private_or_raw_evidence():
    evidence = _complete_backup_restore_evidence()
    evidence["private_raw_evidence_included"] = True
    evidence["raw_path"] = str(Path.home() / "private" / "owner-book.gnucash.sqlite")
    evidence["memo"] = "owner memo should never be accepted"
    evidence["amount"] = "123.45"

    result = validate_backup_restore_readiness_evidence(evidence)
    payload_text = json.dumps(result.to_dict(), sort_keys=True)

    assert result.ready is False
    assert result.to_dict()["checks"]["private_raw_evidence_absent"]["status"] == "blocked"
    assert str(Path.home()) not in payload_text
    assert "owner-book" not in payload_text
    assert "owner memo" not in payload_text
    assert "123.45" not in payload_text
