import importlib.util
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[3] / "scripts" / "owner_write_session_preflight.py"
spec = importlib.util.spec_from_file_location("owner_write_session_preflight", SCRIPT)
assert spec is not None
owner_preflight = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = owner_preflight
assert spec.loader is not None
spec.loader.exec_module(owner_preflight)


def test_owner_write_session_preflight_passes_with_external_copy(tmp_path, monkeypatch):
    target = tmp_path / "copied-test-book.gnucash.sqlite"
    target.write_bytes(b"synthetic copied book placeholder")
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("GNUCASH_WRITES_ENABLED", "false")

    result = owner_preflight.run_preflight(str(target), str(backup_dir))
    manifest = owner_preflight.build_manifest(result, 447)

    assert result.status == "PASS"
    assert result.mutation_performed is False
    assert result.target_ref == "target:redacted.gnucash.sqlite"
    assert str(target) not in str(manifest)
    assert manifest["backup_readiness_status"] == "ready"
    assert manifest["restore_check_status"] == "helper-available"


def test_owner_write_session_preflight_blocks_inside_repo(tmp_path, monkeypatch):
    target = Path(__file__).resolve()
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("GNUCASH_WRITES_ENABLED", "false")

    result = owner_preflight.run_preflight(str(target), str(backup_dir))

    assert result.status == "BLOCKED"
    assert "target must be outside git checkout" in result.blockers
    assert result.mutation_performed is False


def test_owner_write_session_preflight_blocks_enabled_runtime(tmp_path, monkeypatch):
    target = tmp_path / "copy.gnucash.sqlite"
    target.write_bytes(b"synthetic")
    backup_dir = tmp_path / "backups"
    backup_dir.mkdir()
    monkeypatch.setenv("APP_ENV", "test")
    monkeypatch.setenv("GNUCASH_WRITES_ENABLED", "true")

    result = owner_preflight.run_preflight(str(target), str(backup_dir))

    assert result.status == "BLOCKED"
    assert "runtime writes are enabled during non-mutating preflight" in result.blockers
    assert result.runtime_writes_enabled is True
