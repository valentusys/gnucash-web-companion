from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "scripts" / "write_alpha_compatibility_check.py"
FIXTURE_SCRIPT = REPO_ROOT / "apps" / "api" / "scripts" / "create_compatibility_fixture_v1.py"

spec = importlib.util.spec_from_file_location("write_alpha_compatibility_check", SCRIPT_PATH)
assert spec and spec.loader
compat = importlib.util.module_from_spec(spec)
sys.modules["write_alpha_compatibility_check"] = compat
spec.loader.exec_module(compat)

fixture_spec = importlib.util.spec_from_file_location("create_compatibility_fixture_v1", FIXTURE_SCRIPT)
assert fixture_spec and fixture_spec.loader
fixture = importlib.util.module_from_spec(fixture_spec)
fixture_spec.loader.exec_module(fixture)


def test_synthetic_fixture_blocks_when_gnucash_cli_is_unavailable(tmp_path, monkeypatch, capsys):
    target = tmp_path / "phase-256-synthetic-copy.gnucash.sqlite"
    output = tmp_path / "evidence" / "phase-256.json"
    fixture.create_fixture(target)
    monkeypatch.setattr(compat.shutil, "which", lambda command: None)

    result = compat.main([str(target), "--output", str(output)])

    assert result == 3
    captured = capsys.readouterr()
    assert "BLOCKED" in captured.out
    assert str(tmp_path) not in captured.out
    data = json.loads(output.read_text(encoding="utf-8"))
    assert data["result"] == "blocked"
    assert data["piecash_read"]["status"] == "pass"
    assert data["piecash_read"]["account_count"] >= 1
    assert data["piecash_read"]["transaction_count"] >= 1
    assert data["desktop_tooling"]["status"] == "blocked"
    assert data["desktop_tooling"]["available"] is False
    assert data["target_path"] == "<redacted>"
    assert data["broad_compatibility_claimed"] is False
    serialized = json.dumps(data, sort_keys=True)
    assert str(tmp_path) not in serialized
    assert "Checking" not in serialized
    assert "Fixture salary" not in serialized
    assert "1000" not in serialized


def test_synthetic_fixture_passes_when_gnucash_cli_report_succeeds(tmp_path, monkeypatch):
    target = tmp_path / "phase-256-synthetic-copy.gnucash.sqlite"
    fixture.create_fixture(target)

    monkeypatch.setattr(compat.shutil, "which", lambda command: f"/usr/bin/{command}")

    class Completed:
        returncode = 0
        stdout = "GnuCash 5.10\n"
        stderr = ""

    calls = []

    def fake_run(command, **kwargs):
        calls.append(tuple(command))
        return Completed()

    monkeypatch.setattr(compat.subprocess, "run", fake_run)

    evidence = compat.run_check(target)

    assert evidence.result == "pass"
    assert evidence.piecash_read.status == "pass"
    assert evidence.desktop_tooling.status == "pass"
    assert evidence.desktop_tooling.command.endswith("<redacted-book>")
    assert any(call[:2] == ("gnucash-cli", "--report") for call in calls)


def test_missing_target_fails_without_raw_path(tmp_path, capsys):
    missing = tmp_path / "missing-private-book.gnucash.sqlite"
    output = tmp_path / "evidence.json"

    result = compat.main([str(missing), "--output", str(output)])

    assert result == 2
    captured = capsys.readouterr()
    assert "paths=redacted" in captured.err
    assert str(missing) not in captured.err
    assert not output.exists()
