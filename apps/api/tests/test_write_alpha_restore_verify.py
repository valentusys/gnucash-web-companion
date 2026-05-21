import hashlib
import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "scripts" / "write_alpha_restore_verify.py"
FIXTURE = REPO_ROOT / "apps" / "api" / "tests" / "fixtures" / "test-book.gnucash.sqlite"

spec = importlib.util.spec_from_file_location("write_alpha_restore_verify", SCRIPT_PATH)
assert spec and spec.loader
restore_verify = importlib.util.module_from_spec(spec)
sys.modules["write_alpha_restore_verify"] = restore_verify
spec.loader.exec_module(restore_verify)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _base_args(target: Path, backup: Path, output: Path) -> list[str]:
    return [
        "--target",
        str(target),
        "--backup",
        str(backup),
        "--output",
        str(output),
        "--confirm-copied-disposable",
        "--confirm-original-untouched",
        "--confirm-restore-over-copy",
        "--confirm-backup-pre-mutation",
    ]


def _copy_fixture_pair(tmp_path: Path) -> tuple[Path, Path]:
    backup = tmp_path / "phase-257-pre-mutation-backup.gnucash.sqlite"
    target = tmp_path / "phase-257-working-copy.gnucash.sqlite"
    backup.write_bytes(FIXTURE.read_bytes())
    target.write_bytes(b"mutated placeholder bytes before restore")
    return target, backup


def test_restore_verification_restores_fixture_and_writes_redacted_evidence(tmp_path, monkeypatch):
    monkeypatch.setattr(restore_verify, "_default_disabled_status", lambda: "verified-default-disabled")
    target, backup = _copy_fixture_pair(tmp_path)
    expected = _sha256(backup)
    output = tmp_path / "evidence" / "restore.json"

    result = restore_verify.main(
        [
            *_base_args(target, backup, output),
            "--expected-restored-sha256",
            expected,
            "--api-read-command",
            "true",
        ]
    )

    assert result == 0
    assert _sha256(target) == expected
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["phase_number"] == 257
    assert data["result"] == "pass"
    assert data["restore_proof_status"] == "verified"
    assert data["checksum_status"] == "verified-backup-matches-restored"
    assert data["expected_checksum_status"] == "verified-expected-checksum"
    assert data["read_back"]["status"] == "pass"
    assert data["api_read"]["status"] == "pass"
    assert data["disabled_reset_status"] == "verified-default-disabled"
    evidence_text = output.read_text(encoding="utf-8")
    assert str(tmp_path) not in evidence_text
    assert "test-book" not in evidence_text


def test_restore_verification_blocks_without_api_read_command(tmp_path, monkeypatch):
    monkeypatch.setattr(restore_verify, "_default_disabled_status", lambda: "verified-default-disabled")
    target, backup = _copy_fixture_pair(tmp_path)
    output = tmp_path / "restore.json"

    result = restore_verify.main(_base_args(target, backup, output))

    assert result == 3
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["result"] == "blocked"
    assert data["api_read"]["status"] == "blocked"
    assert data["restore_proof_status"] == "verified"


def test_restore_verification_rejects_inside_repo_target(tmp_path, monkeypatch):
    monkeypatch.setattr(restore_verify, "_default_disabled_status", lambda: "verified-default-disabled")
    inside = REPO_ROOT / "phase-257-inside-repo-test.gnucash.sqlite"
    backup = tmp_path / "phase-257-backup.gnucash.sqlite"
    inside.write_bytes(b"unsafe target")
    backup.write_bytes(FIXTURE.read_bytes())
    try:
        result = restore_verify.main(_base_args(inside, backup, tmp_path / "restore.json"))
    finally:
        inside.unlink(missing_ok=True)

    assert result == 2
    assert not (tmp_path / "restore.json").exists()


def test_restore_verification_fails_on_expected_checksum_mismatch(tmp_path, monkeypatch):
    monkeypatch.setattr(restore_verify, "_default_disabled_status", lambda: "verified-default-disabled")
    target, backup = _copy_fixture_pair(tmp_path)
    output = tmp_path / "restore.json"

    result = restore_verify.main(
        [
            *_base_args(target, backup, output),
            "--expected-restored-sha256",
            "0" * 64,
            "--api-read-command",
            "true",
        ]
    )

    assert result == 2
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["result"] == "fail"
    assert data["expected_checksum_status"] == "failed-expected-checksum-mismatch"


def test_restore_verification_requires_explicit_confirmations(tmp_path):
    target, backup = _copy_fixture_pair(tmp_path)

    result = restore_verify.main(
        [
            "--target",
            str(target),
            "--backup",
            str(backup),
            "--output",
            str(tmp_path / "restore.json"),
        ]
    )

    assert result == 2
