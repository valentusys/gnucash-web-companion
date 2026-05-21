import importlib.util
import json
import os
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "scripts" / "write_alpha_copied_book_dogfood.py"

spec = importlib.util.spec_from_file_location("write_alpha_copied_book_dogfood", SCRIPT_PATH)
assert spec and spec.loader
wrapper = importlib.util.module_from_spec(spec)
sys.modules["write_alpha_copied_book_dogfood"] = wrapper
spec.loader.exec_module(wrapper)


def _target(tmp_path: Path) -> Path:
    outside = tmp_path / "phase-254-synthetic-copy.gnucash.sqlite"
    outside.write_bytes(b"synthetic copied fixture bytes")
    return outside


def _base_args(target: Path, backup_dir: Path, evidence_file: Path) -> list[str]:
    return [
        "--target",
        str(target),
        "--backup-dir",
        str(backup_dir),
        "--evidence-file",
        str(evidence_file),
        "--confirm-copied-disposable",
        "--confirm-original-untouched",
        "--confirm-outside-git",
    ]


def test_dry_run_succeeds_with_redacted_evidence(tmp_path, monkeypatch):
    monkeypatch.setenv("GNUCASH_WRITES_ENABLED", "true")
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setattr(wrapper, "_default_disabled_status", lambda: "verified-default-disabled")

    evidence_file = tmp_path / "evidence" / "phase-254.json"
    result = wrapper.main(
        ["--dry-run", *_base_args(_target(tmp_path), tmp_path / "backups", evidence_file)]
    )

    assert result == 0
    data = json.loads(evidence_file.read_text(encoding="utf-8"))
    assert data["mode"] == "dry-run"
    assert data["mutation_requested"] is False
    assert data["mutation_performed"] is False
    assert data["backup_status"] == "created-before-step"
    assert data["location_redaction_status"] == "redacted"
    assert str(tmp_path) not in evidence_file.read_text(encoding="utf-8")
    assert list((tmp_path / "backups").iterdir())


def test_create_one_requires_explicit_mutation_confirmation(tmp_path, monkeypatch):
    monkeypatch.setenv("GNUCASH_WRITES_ENABLED", "true")
    monkeypatch.setenv("APP_ENV", "test")

    result = wrapper.main(
        ["--create-one", *_base_args(_target(tmp_path), tmp_path / "backups", tmp_path / "evidence.json")]
    )

    assert result == 2


def test_create_one_runs_delegated_command_after_backup(tmp_path, monkeypatch):
    monkeypatch.setenv("GNUCASH_WRITES_ENABLED", "true")
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setattr(wrapper, "_default_disabled_status", lambda: "verified-default-disabled")
    calls = []

    def fake_run(command):
        calls.append(tuple(command))
        return "passed"

    monkeypatch.setattr(wrapper, "_run_create_command", fake_run)
    evidence_file = tmp_path / "evidence.json"

    result = wrapper.main(
        [
            "--create-one",
            *_base_args(_target(tmp_path), tmp_path / "backups", evidence_file),
            "--confirm-create-one-mutation",
            "--create-command",
            "true",
        ]
    )

    assert result == 0
    assert calls == [("true",)]
    data = json.loads(evidence_file.read_text(encoding="utf-8"))
    assert data["mode"] == "create-one"
    assert data["mutation_requested"] is True
    assert data["mutation_performed"] is True
    assert data["create_command_status"] == "passed"
    assert data["delete_status"] == "not-supported-by-default"


def test_inside_repo_target_is_rejected(tmp_path, monkeypatch):
    monkeypatch.setenv("GNUCASH_WRITES_ENABLED", "true")
    monkeypatch.setenv("APP_ENV", "test")
    inside = REPO_ROOT / "phase-254-inside-repo-test.gnucash.sqlite"
    inside.write_bytes(b"temporary unsafe target")
    try:
        result = wrapper.main(
            ["--dry-run", *_base_args(inside, tmp_path / "backups", tmp_path / "evidence.json")]
        )
    finally:
        inside.unlink(missing_ok=True)

    assert result == 2
    assert not (tmp_path / "evidence.json").exists()


def test_dry_run_blocks_without_write_alpha_env(tmp_path, monkeypatch):
    monkeypatch.delenv("GNUCASH_WRITES_ENABLED", raising=False)
    monkeypatch.setenv("APP_ENV", "test")

    result = wrapper.main(
        ["--dry-run", *_base_args(_target(tmp_path), tmp_path / "backups", tmp_path / "evidence.json")]
    )

    assert result == 2
