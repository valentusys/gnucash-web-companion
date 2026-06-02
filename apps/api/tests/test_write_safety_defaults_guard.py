"""Tests for committed write-safety default guard."""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts" / "check_write_safety_defaults.py"

spec = importlib.util.spec_from_file_location("check_write_safety_defaults", SCRIPT)
assert spec is not None
write_safety_guard = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["check_write_safety_defaults"] = write_safety_guard
spec.loader.exec_module(write_safety_guard)


def test_write_safety_defaults_guard_passes_on_committed_config() -> None:
    proc = subprocess.run(
        [sys.executable, str(SCRIPT)],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=ROOT,
    )

    assert proc.returncode == 0
    assert "write-safety defaults ok" in proc.stdout
    assert "GNUCASH_WRITES_ENABLED=false" in proc.stdout
    assert "APP_ENV=test gate text present" in proc.stdout
    assert "explicit write enablement present" in proc.stdout
    assert "reset/default-disabled probe wording present" in proc.stdout
    assert proc.stderr == ""


def test_owner_writebeta_operating_guide_preserves_future_copied_book_authorization_format() -> None:
    guide = (ROOT / "docs/write-alpha/owner-writebeta-operating-guide.md").read_text(encoding="utf-8")

    assert "## Future copied/restorable authorization format" in guide
    assert "same execution context" in guide
    assert "route family and operation counts" in guide
    assert "backup/read-back/audit/lock/restore/reset" in guide
    assert "No original/private/real-working/only-copy book" in guide
    assert "If authorization is absent, run non-mutating guards/docs/tests only" in guide


def test_write_safety_defaults_guard_rejects_unsafe_fixture(tmp_path: Path) -> None:
    env_example = tmp_path / ".env.example"
    compose = tmp_path / "docker-compose.yml"
    status_doc = tmp_path / "status.md"
    env_example.write_text("GNUCASH_WRITES_ENABLED=true\n", encoding="utf-8")
    compose.write_text(
        "services:\n  api:\n    environment:\n      - GNUCASH_WRITES_ENABLED=${GNUCASH_WRITES_ENABLED:-true}\n",
        encoding="utf-8",
    )
    status_doc.write_text("missing gate text\n", encoding="utf-8")

    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--env-example",
            str(env_example),
            "--compose",
            str(compose),
            "--gate-doc",
            str(status_doc),
        ],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=ROOT,
    )

    assert proc.returncode == 2
    assert proc.stdout == ""
    assert "unsafe write-safety defaults" in proc.stderr
    assert str(tmp_path) not in proc.stderr


def test_write_safety_defaults_guard_rejects_missing_reset_probe_wording(tmp_path: Path) -> None:
    env_example = tmp_path / ".env.example"
    compose = tmp_path / "docker-compose.yml"
    status_doc = tmp_path / "status.md"
    env_example.write_text("GNUCASH_WRITES_ENABLED=false\n", encoding="utf-8")
    compose.write_text(
        "services:\n  api:\n    environment:\n      - GNUCASH_WRITES_ENABLED=${GNUCASH_WRITES_ENABLED:-false}\n",
        encoding="utf-8",
    )
    status_doc.write_text(
        "Enabled write-alpha remains APP_ENV=test gated and requires explicit write enablement only.\n",
        encoding="utf-8",
    )

    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--env-example",
            str(env_example),
            "--compose",
            str(compose),
            "--gate-doc",
            str(status_doc),
        ],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=ROOT,
    )

    assert proc.returncode == 2
    assert proc.stdout == ""
    assert "reset/default-disabled probe wording" in proc.stderr
    assert str(tmp_path) not in proc.stderr


def test_write_safety_defaults_guard_rejects_missing_issue_36_audit_wording(tmp_path: Path) -> None:
    env_example = tmp_path / ".env.example"
    compose = tmp_path / "docker-compose.yml"
    status_doc = tmp_path / "status.md"
    checklist_doc = tmp_path / "checklist.md"
    env_example.write_text("GNUCASH_WRITES_ENABLED=false\n", encoding="utf-8")
    compose.write_text(
        "services:\n  api:\n    environment:\n      - GNUCASH_WRITES_ENABLED=${GNUCASH_WRITES_ENABLED:-false}\n",
        encoding="utf-8",
    )
    status_doc.write_text(
        "Enabled write-alpha remains APP_ENV=test gated, requires explicit write enablement, "
        "and reset/default-disabled disabled-probe evidence.\n",
        encoding="utf-8",
    )
    checklist_doc.write_text(
        "# Checklist\n"
        "APP_ENV=test and GNUCASH_WRITES_ENABLED=false are required.\n"
        "No release and no public write beta.\n",
        encoding="utf-8",
    )

    proc = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--env-example",
            str(env_example),
            "--compose",
            str(compose),
            "--gate-doc",
            str(status_doc),
            "--checklist-doc",
            str(checklist_doc),
        ],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=ROOT,
    )

    assert proc.returncode == 2
    assert proc.stdout == ""
    assert "#36 audit checklist" in proc.stderr
    assert str(tmp_path) not in proc.stderr


def test_write_safety_defaults_guard_rejects_broad_write_compatibility_claim(tmp_path: Path, monkeypatch) -> None:
    doc = tmp_path / "write-compatibility.md"
    doc.write_text(
        "supported-version write compatibility remains pending; "
        "synthetic/disposable or copied/restorable evidence only; "
        "not a real-book claim; broad GnuCash compatibility; public write beta; production; security-audited; "
        "broad GnuCash write compatibility is supported.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(write_safety_guard, "WRITE_COMPATIBILITY_DOCS", (doc,))

    failures = write_safety_guard._check_write_compatibility_docs((doc,))

    assert any("broad GnuCash write compatibility is supported" in failure for failure in failures)
    assert str(tmp_path) not in "; ".join(failures)


def test_write_safety_defaults_guard_rejects_missing_write_compatibility_caveat(
    tmp_path: Path, monkeypatch
) -> None:
    doc = tmp_path / "write-compatibility.md"
    doc.write_text(
        "supported-version write compatibility remains pending; "
        "not a real-book claim; no broad compatibility; public write beta; production; security-audited.\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(write_safety_guard, "WRITE_COMPATIBILITY_DOCS", (doc,))

    failures = write_safety_guard._check_write_compatibility_docs((doc,))

    assert any("synthetic/disposable or copied/restorable evidence only" in failure for failure in failures)
    assert str(tmp_path) not in "; ".join(failures)


def test_write_safety_defaults_guard_rejects_missing_issue_36_remaining_gate_marker(
    tmp_path: Path,
) -> None:
    doc = tmp_path / "issue-36.md"
    doc.write_text(
        "keep #36 open. GNUCASH_WRITES_ENABLED=false. APP_ENV=test. NO_RELEASE. "
        "CREATE 0 / PATCH 0 / DELETE 0. no public write beta.\n",
        encoding="utf-8",
    )

    failures = write_safety_guard._check_issue_36_remaining_gates(doc)

    assert any("future copied/restorable mutation evidence packet" in failure for failure in failures)
    assert any("same-context owner + PM authorization" in failure for failure in failures)
    assert str(tmp_path) not in "; ".join(failures)


def test_write_safety_defaults_guard_rejects_missing_issue_36_dashboard_marker(
    tmp_path: Path,
) -> None:
    doc = tmp_path / "dashboard.md"
    doc.write_text(
        "keep #36 open. state-machine evidence. copied-book evidence. restore evidence. "
        "GNUCASH_WRITES_ENABLED=false. APP_ENV=test. NO_RELEASE. CREATE 0 / PATCH 0 / DELETE 0.\n",
        encoding="utf-8",
    )

    failures = write_safety_guard._check_issue_36_dashboard(doc)

    assert any("default-disabled probes" in failure for failure in failures)
    assert any("compatibility gaps" in failure for failure in failures)
    assert any("same-context owner + PM authorization" in failure for failure in failures)
    assert str(tmp_path) not in "; ".join(failures)


def test_write_safety_defaults_guard_rejects_missing_restore_boundary_marker(
    tmp_path: Path,
) -> None:
    doc = tmp_path / "restore.md"
    doc.write_text(
        "restore-to-copy. not destructive restore. independent backup. redacted evidence only. "
        "GNUCASH_WRITES_ENABLED=false. APP_ENV=test. CREATE 0 / PATCH 0 / DELETE 0.\n",
        encoding="utf-8",
    )

    failures = write_safety_guard._check_restore_boundary(doc)

    assert any("not real-book safety evidence" in failure for failure in failures)
    assert str(tmp_path) not in "; ".join(failures)


def test_write_safety_defaults_guard_rejects_missing_copied_dogfood_packet_marker(
    tmp_path: Path,
) -> None:
    doc = tmp_path / "copied-packet.md"
    doc.write_text(
        "non-mutating packet. route family and operation counts. redacted evidence only. "
        "GNUCASH_WRITES_ENABLED=false. APP_ENV=test. CREATE 0 / PATCH 0 / DELETE 0.\n",
        encoding="utf-8",
    )

    failures = write_safety_guard._check_copied_dogfood_packet(doc)

    assert any("same-context owner + PM authorization" in failure for failure in failures)
    assert any("backup/read-back/audit/lock/restore/reset" in failure for failure in failures)
    assert any("no original/private/real-working/only-copy" in failure for failure in failures)
    assert str(tmp_path) not in "; ".join(failures)
