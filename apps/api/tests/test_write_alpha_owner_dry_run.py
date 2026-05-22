import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "scripts" / "write_alpha_owner_dry_run.py"

spec = importlib.util.spec_from_file_location("write_alpha_owner_dry_run", SCRIPT_PATH)
assert spec and spec.loader
owner_dry_run = importlib.util.module_from_spec(spec)
sys.modules["write_alpha_owner_dry_run"] = owner_dry_run
spec.loader.exec_module(owner_dry_run)


def _target(tmp_path: Path) -> Path:
    target = tmp_path / "phase-263-synthetic-copy.gnucash.sqlite"
    target.write_bytes(b"synthetic copied fixture bytes")
    return target


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


def test_owner_dry_run_entrypoint_writes_no_mutation_evidence(tmp_path, monkeypatch):
    monkeypatch.setenv("GNUCASH_WRITES_ENABLED", "true")
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setattr(owner_dry_run.dogfood, "_default_disabled_status", lambda: "verified-default-disabled")

    evidence_file = tmp_path / "evidence" / "phase-263.json"
    result = owner_dry_run.main(
        _base_args(_target(tmp_path), tmp_path / "backups", evidence_file)
    )

    assert result == 0
    data = json.loads(evidence_file.read_text(encoding="utf-8"))
    assert data["phase_number"] == 263
    assert data["classification"] == "synthetic"
    assert data["mode"] == "dry-run"
    assert data["mutation_requested"] is False
    assert data["mutation_performed"] is False
    assert data["create_command_status"] == "not-run"
    assert data["patch_status"] == "not-supported-by-default"
    assert data["delete_status"] == "not-supported-by-default"
    assert str(tmp_path) not in evidence_file.read_text(encoding="utf-8")
    assert list((tmp_path / "backups").iterdir())


def test_owner_dry_run_has_no_create_one_cli_mode():
    parser = owner_dry_run.parse_args
    try:
        parser(["--create-one"])
    except SystemExit as exc:
        assert exc.code != 0
    else:  # pragma: no cover - defensive
        raise AssertionError("--create-one must not be accepted by owner dry-run entrypoint")


def test_owner_dry_run_blocks_if_underlying_evidence_claims_mutation(tmp_path, monkeypatch):
    class FakeEvidence:
        mode = "dry-run"
        mutation_requested = False
        mutation_performed = True
        create_command_status = "not-run"

    monkeypatch.setattr(owner_dry_run.dogfood, "run", lambda args: FakeEvidence())

    result = owner_dry_run.main(
        _base_args(_target(tmp_path), tmp_path / "backups", tmp_path / "evidence.json")
    )

    assert result == 2
    assert not (tmp_path / "evidence.json").exists()
