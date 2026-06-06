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
    assert "APP_ENV=development default present" in proc.stdout
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


def test_write_safety_defaults_guard_rejects_commented_env_defaults_spoof(tmp_path: Path) -> None:
    env_example = tmp_path / ".env.example"
    compose = tmp_path / "docker-compose.yml"
    status_doc = tmp_path / "status.md"
    env_example.write_text(
        "# APP_ENV=development\n"
        "# GNUCASH_WRITES_ENABLED=false\n",
        encoding="utf-8",
    )
    compose.write_text(
        "services:\n"
        "  api:\n"
        "    environment:\n"
        "      - APP_ENV=${APP_ENV:-development}\n"
        "      - GNUCASH_WRITES_ENABLED=${GNUCASH_WRITES_ENABLED:-false}\n"
        "  web:\n"
        "    environment:\n"
        "      - GNUCASH_WRITES_ENABLED=${GNUCASH_WRITES_ENABLED:-false}\n",
        encoding="utf-8",
    )
    status_doc.write_text(
        "Enabled write-alpha remains APP_ENV=test gated, requires explicit write enablement, "
        "and reset/default-disabled disabled-probe evidence.\n",
        encoding="utf-8",
    )

    failures = write_safety_guard._check(env_example, compose, status_doc, checklist_doc=None)

    assert any("uncommented assignment" in failure for failure in failures)
    assert str(tmp_path) not in "; ".join(failures)


def test_write_safety_defaults_guard_rejects_duplicate_env_alternate_defaults(tmp_path: Path) -> None:
    env_example = tmp_path / ".env.example"
    compose = tmp_path / "docker-compose.yml"
    status_doc = tmp_path / "status.md"
    env_example.write_text(
        "APP_ENV=development\n"
        "export APP_ENV=test\n"
        "GNUCASH_WRITES_ENABLED=false\n"
        "export GNUCASH_WRITES_ENABLED=true\n",
        encoding="utf-8",
    )
    compose.write_text(
        "services:\n"
        "  api:\n"
        "    environment:\n"
        "      - APP_ENV=${APP_ENV:-development}\n"
        "      - GNUCASH_WRITES_ENABLED=${GNUCASH_WRITES_ENABLED:-false}\n"
        "  web:\n"
        "    environment:\n"
        "      - GNUCASH_WRITES_ENABLED=${GNUCASH_WRITES_ENABLED:-false}\n",
        encoding="utf-8",
    )
    status_doc.write_text(
        "Enabled write-alpha remains APP_ENV=test gated, requires explicit write enablement, "
        "and reset/default-disabled disabled-probe evidence.\n",
        encoding="utf-8",
    )

    failures = write_safety_guard._check(env_example, compose, status_doc, checklist_doc=None)

    assert any("alternate GNUCASH_WRITES_ENABLED" in failure for failure in failures)
    assert any("alternate APP_ENV" in failure for failure in failures)
    assert str(tmp_path) not in "; ".join(failures)


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


def test_write_safety_defaults_guard_rejects_compose_api_write_default_hidden_by_web_default(
    tmp_path: Path,
) -> None:
    env_example = tmp_path / ".env.example"
    compose = tmp_path / "docker-compose.yml"
    status_doc = tmp_path / "status.md"
    env_example.write_text("APP_ENV=development\nGNUCASH_WRITES_ENABLED=false\n", encoding="utf-8")
    compose.write_text(
        "services:\n"
        "  api:\n"
        "    environment:\n"
        "      - APP_ENV=${APP_ENV:-development}\n"
        "  web:\n"
        "    environment:\n"
        "      - GNUCASH_WRITES_ENABLED=${GNUCASH_WRITES_ENABLED:-false}\n",
        encoding="utf-8",
    )
    status_doc.write_text(
        "Enabled write-alpha remains APP_ENV=test gated, requires explicit write enablement, "
        "and reset/default-disabled disabled-probe evidence.\n",
        encoding="utf-8",
    )

    failures = write_safety_guard._check(env_example, compose, status_doc, checklist_doc=None)

    assert any("api service" in failure and "GNUCASH_WRITES_ENABLED" in failure for failure in failures)
    assert str(tmp_path) not in "; ".join(failures)


def test_write_safety_defaults_guard_rejects_compose_api_app_env_default_hidden_by_other_defaults(
    tmp_path: Path,
) -> None:
    env_example = tmp_path / ".env.example"
    compose = tmp_path / "docker-compose.yml"
    status_doc = tmp_path / "status.md"
    env_example.write_text("APP_ENV=development\nGNUCASH_WRITES_ENABLED=false\n", encoding="utf-8")
    compose.write_text(
        "services:\n"
        "  api:\n"
        "    environment:\n"
        "      - GNUCASH_WRITES_ENABLED=${GNUCASH_WRITES_ENABLED:-false}\n"
        "  worker:\n"
        "    environment:\n"
        "      - APP_ENV=${APP_ENV:-development}\n",
        encoding="utf-8",
    )
    status_doc.write_text(
        "Enabled write-alpha remains APP_ENV=test gated, requires explicit write enablement, "
        "and reset/default-disabled disabled-probe evidence.\n",
        encoding="utf-8",
    )

    failures = write_safety_guard._check(env_example, compose, status_doc, checklist_doc=None)

    assert any("api service" in failure and "APP_ENV" in failure for failure in failures)
    assert str(tmp_path) not in "; ".join(failures)


def test_compose_service_environment_lines_supports_mapping_form() -> None:
    compose_text = (
        "services:\n"
        "  api:\n"
        "    environment:\n"
        "      APP_ENV: ${APP_ENV:-development}\n"
        "      GNUCASH_WRITES_ENABLED: ${GNUCASH_WRITES_ENABLED:-false}\n"
        "  web:\n"
        "    environment:\n"
        "      GNUCASH_WRITES_ENABLED: ${GNUCASH_WRITES_ENABLED:-true}\n"
    )

    environment = write_safety_guard._compose_service_environment_lines(compose_text, "api")

    assert "APP_ENV=${APP_ENV:-development}" in environment
    assert "GNUCASH_WRITES_ENABLED=${GNUCASH_WRITES_ENABLED:-false}" in environment
    assert "GNUCASH_WRITES_ENABLED=${GNUCASH_WRITES_ENABLED:-true}" not in environment


def test_write_safety_defaults_guard_rejects_compose_api_mapping_write_default_hidden_by_web_default(
    tmp_path: Path,
) -> None:
    env_example = tmp_path / ".env.example"
    compose = tmp_path / "docker-compose.yml"
    status_doc = tmp_path / "status.md"
    env_example.write_text("APP_ENV=development\nGNUCASH_WRITES_ENABLED=false\n", encoding="utf-8")
    compose.write_text(
        "services:\n"
        "  api:\n"
        "    environment:\n"
        "      APP_ENV: ${APP_ENV:-development}\n"
        "      GNUCASH_WRITES_ENABLED: ${GNUCASH_WRITES_ENABLED:-true}\n"
        "  web:\n"
        "    environment:\n"
        "      - GNUCASH_WRITES_ENABLED=${GNUCASH_WRITES_ENABLED:-false}\n",
        encoding="utf-8",
    )
    status_doc.write_text(
        "Enabled write-alpha remains APP_ENV=test gated, requires explicit write enablement, "
        "and reset/default-disabled disabled-probe evidence.\n",
        encoding="utf-8",
    )

    failures = write_safety_guard._check(env_example, compose, status_doc, checklist_doc=None)

    assert any("api service" in failure and "GNUCASH_WRITES_ENABLED" in failure for failure in failures)
    assert str(tmp_path) not in "; ".join(failures)


def test_write_safety_defaults_guard_rejects_duplicate_api_write_env_override(
    tmp_path: Path,
) -> None:
    env_example = tmp_path / ".env.example"
    compose = tmp_path / "docker-compose.yml"
    status_doc = tmp_path / "status.md"
    env_example.write_text("APP_ENV=development\nGNUCASH_WRITES_ENABLED=false\n", encoding="utf-8")
    compose.write_text(
        "services:\n"
        "  api:\n"
        "    environment:\n"
        "      - APP_ENV=${APP_ENV:-development}\n"
        "      - GNUCASH_WRITES_ENABLED=${GNUCASH_WRITES_ENABLED:-false}\n"
        "      - GNUCASH_WRITES_ENABLED=true\n"
        "  web:\n"
        "    environment:\n"
        "      - GNUCASH_WRITES_ENABLED=${GNUCASH_WRITES_ENABLED:-false}\n",
        encoding="utf-8",
    )
    status_doc.write_text(
        "Enabled write-alpha remains APP_ENV=test gated, requires explicit write enablement, "
        "and reset/default-disabled disabled-probe evidence.\n",
        encoding="utf-8",
    )

    failures = write_safety_guard._check(env_example, compose, status_doc, checklist_doc=None)

    assert any("api service" in failure and "alternate GNUCASH_WRITES_ENABLED" in failure for failure in failures)
    assert str(tmp_path) not in "; ".join(failures)


def test_write_safety_defaults_guard_rejects_duplicate_api_app_env_test_override(
    tmp_path: Path,
) -> None:
    env_example = tmp_path / ".env.example"
    compose = tmp_path / "docker-compose.yml"
    status_doc = tmp_path / "status.md"
    env_example.write_text("APP_ENV=development\nGNUCASH_WRITES_ENABLED=false\n", encoding="utf-8")
    compose.write_text(
        "services:\n"
        "  api:\n"
        "    environment:\n"
        "      - APP_ENV=${APP_ENV:-development}\n"
        "      - APP_ENV=test\n"
        "      - GNUCASH_WRITES_ENABLED=${GNUCASH_WRITES_ENABLED:-false}\n"
        "  web:\n"
        "    environment:\n"
        "      - APP_ENV=${APP_ENV:-development}\n",
        encoding="utf-8",
    )
    status_doc.write_text(
        "Enabled write-alpha remains APP_ENV=test gated, requires explicit write enablement, "
        "and reset/default-disabled disabled-probe evidence.\n",
        encoding="utf-8",
    )

    failures = write_safety_guard._check(env_example, compose, status_doc, checklist_doc=None)

    assert any("api service" in failure and "alternate APP_ENV" in failure for failure in failures)
    assert str(tmp_path) not in "; ".join(failures)


def test_write_safety_defaults_guard_rejects_compose_web_mapping_write_default_hidden_by_api_default(
    tmp_path: Path,
) -> None:
    env_example = tmp_path / ".env.example"
    compose = tmp_path / "docker-compose.yml"
    status_doc = tmp_path / "status.md"
    env_example.write_text("APP_ENV=development\nGNUCASH_WRITES_ENABLED=false\n", encoding="utf-8")
    compose.write_text(
        "services:\n"
        "  api:\n"
        "    environment:\n"
        "      - APP_ENV=${APP_ENV:-development}\n"
        "      - GNUCASH_WRITES_ENABLED=${GNUCASH_WRITES_ENABLED:-false}\n"
        "  web:\n"
        "    environment:\n"
        "      GNUCASH_WRITES_ENABLED: ${GNUCASH_WRITES_ENABLED:-true}\n",
        encoding="utf-8",
    )
    status_doc.write_text(
        "Enabled write-alpha remains APP_ENV=test gated, requires explicit write enablement, "
        "and reset/default-disabled disabled-probe evidence.\n",
        encoding="utf-8",
    )

    failures = write_safety_guard._check(env_example, compose, status_doc, checklist_doc=None)

    assert any("web service" in failure and "GNUCASH_WRITES_ENABLED" in failure for failure in failures)
    assert str(tmp_path) not in "; ".join(failures)


def test_write_safety_defaults_guard_rejects_public_defaults_that_satisfy_app_env_test_gate(
    tmp_path: Path,
) -> None:
    env_example = tmp_path / ".env.example"
    compose = tmp_path / "docker-compose.yml"
    status_doc = tmp_path / "status.md"
    env_example.write_text("APP_ENV=test\nGNUCASH_WRITES_ENABLED=false\n", encoding="utf-8")
    compose.write_text(
        "services:\n  api:\n    environment:\n"
        "      - APP_ENV=${APP_ENV:-test}\n"
        "      - GNUCASH_WRITES_ENABLED=${GNUCASH_WRITES_ENABLED:-false}\n",
        encoding="utf-8",
    )
    status_doc.write_text(
        "Enabled write-alpha remains APP_ENV=test gated, requires explicit write enablement, "
        "and reset/default-disabled disabled-probe evidence.\n",
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
    assert "must not default APP_ENV=test" in proc.stderr
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

    assert any("copied-book dogfood gate accepted" in failure for failure in failures)
    assert any("W3 CREATE 2 / PATCH 1 / DELETE 1" in failure for failure in failures)
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
    assert any("no broad compatibility claim" in failure for failure in failures)
    assert any("no only-copy safety claim" in failure for failure in failures)
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


def test_write_safety_defaults_guard_rejects_api_write_default_true(tmp_path: Path) -> None:
    config = tmp_path / "config.py"
    config.write_text(
        "class Settings:\n"
        "    app_env: str = 'development'\n"
        "    gnucash_writes_enabled: bool = True\n",
        encoding="utf-8",
    )

    failures = write_safety_guard._check_api_write_defaults(config)

    assert any("gnucash_writes_enabled to False" in failure for failure in failures)
    assert any("non-False value" in failure for failure in failures)
    assert str(tmp_path) not in "; ".join(failures)


def test_write_safety_defaults_guard_rejects_api_app_env_test_default(tmp_path: Path) -> None:
    config = tmp_path / "config.py"
    config.write_text(
        "class Settings:\n"
        "    app_env: str = 'test'\n"
        "    gnucash_writes_enabled: bool = False\n",
        encoding="utf-8",
    )

    failures = write_safety_guard._check_api_app_env_defaults(config)

    assert any("app_env to development" in failure for failure in failures)
    assert any("must not default app_env to test" in failure for failure in failures)
    assert str(tmp_path) not in "; ".join(failures)


def test_write_safety_defaults_guard_rejects_new_transaction_write_route_not_in_guard_list(
    tmp_path: Path,
) -> None:
    routes = tmp_path / "transactions.py"
    route_defs = "\n".join(
        f"@router.post('/books/{{book_id}}/transactions')\n"
        f"async def {name}():\n"
        "    _ensure_writes_enabled(settings)\n"
        "    _ensure_write_alpha_test_scope(settings)\n"
        for name in write_safety_guard.WRITE_ROUTE_FUNCTIONS
    )
    routes.write_text(
        "class router:\n"
        "    @staticmethod\n"
        "    def post(path):\n"
        "        return lambda fn: fn\n\n"
        "def _ensure_write_alpha_test_scope(settings):\n"
        "    if settings.app_env.lower() != \"test\":\n"
        "        raise RuntimeError(\"controlled write-alpha routes are limited to explicit test-environment\")\n\n"
        f"{route_defs}\n"
        "@router.post('/books/{book_id}/transactions/import')\n"
        "async def import_book_transactions():\n"
        "    _ensure_writes_enabled(settings)\n"
        "    _ensure_write_alpha_test_scope(settings)\n",
        encoding="utf-8",
    )

    failures = write_safety_guard._check_write_route_test_gates(routes)

    assert any(
        "write route import_book_transactions must be registered in WRITE_ROUTE_FUNCTIONS" in failure
        for failure in failures
    )
    assert str(tmp_path) not in "; ".join(failures)


def test_write_safety_defaults_guard_rejects_write_route_missing_app_env_gate(tmp_path: Path) -> None:
    routes = tmp_path / "transactions.py"
    route_defs = "\n".join(
        f"async def {name}():\n    _ensure_writes_enabled(settings)\n"
        for name in write_safety_guard.WRITE_ROUTE_FUNCTIONS
    )
    routes.write_text(
        "def _ensure_write_alpha_test_scope(settings):\n"
        "    return None\n\n"
        f"{route_defs}\n",
        encoding="utf-8",
    )

    failures = write_safety_guard._check_write_route_test_gates(routes)

    assert any("block non-test APP_ENV" in failure for failure in failures)
    assert any("test-environment scope wording" in failure for failure in failures)
    assert any("executable settings.app_env.lower() != test rejection logic" in failure for failure in failures)
    assert any("_ensure_write_alpha_test_scope" in failure for failure in failures)
    assert str(tmp_path) not in "; ".join(failures)


def test_write_safety_defaults_guard_rejects_docstring_only_app_env_gate(tmp_path: Path) -> None:
    routes = tmp_path / "transactions.py"
    route_defs = "\n".join(
        f"async def {name}():\n"
        "    _ensure_writes_enabled(settings)\n"
        "    _ensure_write_alpha_test_scope(settings)\n"
        for name in write_safety_guard.WRITE_ROUTE_FUNCTIONS
    )
    routes.write_text(
        "def _ensure_write_alpha_test_scope(settings):\n"
        "    '''settings.app_env.lower() != \"test\" controlled write-alpha routes are limited to explicit test-environment'''\n"
        "    return None\n\n"
        f"{route_defs}\n",
        encoding="utf-8",
    )

    failures = write_safety_guard._check_write_route_test_gates(routes)

    assert any("executable settings.app_env.lower() != test rejection logic" in failure for failure in failures)
    assert str(tmp_path) not in "; ".join(failures)


def test_write_safety_defaults_guard_rejects_wrong_polarity_app_env_gate(tmp_path: Path) -> None:
    routes = tmp_path / "transactions.py"
    route_defs = "\n".join(
        f"async def {name}():\n"
        "    _ensure_writes_enabled(settings)\n"
        "    _ensure_write_alpha_test_scope(settings)\n"
        for name in write_safety_guard.WRITE_ROUTE_FUNCTIONS
    )
    routes.write_text(
        "def _ensure_write_alpha_test_scope(settings):\n"
        "    if settings.app_env.lower() == \"test\":\n"
        "        raise RuntimeError(\"controlled write-alpha routes are limited to explicit test-environment\")\n"
        "    _note = 'settings.app_env.lower() != \\\"test\\\"'\n\n"
        f"{route_defs}\n",
        encoding="utf-8",
    )

    failures = write_safety_guard._check_write_route_test_gates(routes)

    assert any("settings.app_env.lower() != test rejection logic" in failure for failure in failures)
    assert str(tmp_path) not in "; ".join(failures)


def test_write_safety_defaults_guard_rejects_route_that_checks_app_env_before_write_default(
    tmp_path: Path,
) -> None:
    routes = tmp_path / "transactions.py"
    route_defs = "\n".join(
        f"async def {name}():\n"
        "    _ensure_write_alpha_test_scope(settings)\n"
        "    _ensure_writes_enabled(settings)\n"
        for name in write_safety_guard.WRITE_ROUTE_FUNCTIONS
    )
    routes.write_text(
        "def _ensure_write_alpha_test_scope(settings):\n"
        "    if settings.app_env.lower() != \"test\":\n"
        "        raise RuntimeError(\"controlled write-alpha routes are limited to explicit test-environment\")\n\n"
        f"{route_defs}\n",
        encoding="utf-8",
    )

    failures = write_safety_guard._check_write_route_test_gates(routes)

    assert any("_ensure_writes_enabled before APP_ENV=test scope" in failure for failure in failures)
    assert str(tmp_path) not in "; ".join(failures)


def test_write_safety_defaults_guard_requires_adjacent_write_and_app_env_gates(
    tmp_path: Path,
) -> None:
    routes = tmp_path / "transactions.py"
    route_defs = "\n".join(
        f"async def {name}():\n"
        "    _ensure_writes_enabled(settings)\n"
        "    _resolve_request_context(request)\n"
        "    _ensure_write_alpha_test_scope(settings)\n"
        for name in write_safety_guard.WRITE_ROUTE_FUNCTIONS
    )
    routes.write_text(
        "def _ensure_write_alpha_test_scope(settings):\n"
        "    if settings.app_env.lower() != \"test\":\n"
        "        raise RuntimeError(\"controlled write-alpha routes are limited to explicit test-environment\")\n\n"
        f"{route_defs}\n",
        encoding="utf-8",
    )

    failures = write_safety_guard._check_write_route_test_gates(routes)

    assert any(
        "_ensure_write_alpha_test_scope immediately after _ensure_writes_enabled" in failure
        for failure in failures
    )
    assert str(tmp_path) not in "; ".join(failures)


def test_write_safety_defaults_guard_rejects_nested_non_executed_route_guards(
    tmp_path: Path,
) -> None:
    routes = tmp_path / "transactions.py"
    route_defs = "\n".join(
        f"async def {name}():\n"
        "    if False:\n"
        "        _ensure_writes_enabled(settings)\n"
        "    _ensure_write_alpha_test_scope(settings)\n"
        for name in write_safety_guard.WRITE_ROUTE_FUNCTIONS
    )
    routes.write_text(
        "def _ensure_write_alpha_test_scope(settings):\n"
        "    if settings.app_env.lower() != \"test\":\n"
        "        raise RuntimeError(\"controlled write-alpha routes are limited to explicit test-environment\")\n\n"
        f"{route_defs}\n",
        encoding="utf-8",
    )

    failures = write_safety_guard._check_write_route_test_gates(routes)

    assert any("_ensure_writes_enabled as a direct guard statement" in failure for failure in failures)
    assert str(tmp_path) not in "; ".join(failures)


def test_write_safety_defaults_guard_rejects_route_side_effects_before_app_env_gate(
    tmp_path: Path,
) -> None:
    routes = tmp_path / "transactions.py"
    route_defs = "\n".join(
        f"async def {name}():\n"
        "    _ensure_writes_enabled(settings)\n"
        "    _write_service_for(book)\n"
        "    _ensure_write_alpha_test_scope(settings)\n"
        for name in write_safety_guard.WRITE_ROUTE_FUNCTIONS
    )
    routes.write_text(
        "def _ensure_write_alpha_test_scope(settings):\n"
        "    if settings.app_env.lower() != \"test\":\n"
        "        raise RuntimeError(\"controlled write-alpha routes are limited to explicit test-environment\")\n\n"
        f"{route_defs}\n",
        encoding="utf-8",
    )

    failures = write_safety_guard._check_write_route_test_gates(routes)

    assert any("_write_service_for only after APP_ENV=test scope" in failure for failure in failures)
    assert str(tmp_path) not in "; ".join(failures)


def test_write_safety_defaults_guard_rejects_book_lookup_before_app_env_gate(
    tmp_path: Path,
) -> None:
    routes = tmp_path / "transactions.py"
    route_defs = "\n".join(
        f"async def {name}():\n"
        "    _ensure_writes_enabled(settings)\n"
        "    _resolve_viewable_book(book_id, user, session)\n"
        "    _require_book_edit_access(book, user, session)\n"
        "    _ensure_write_alpha_test_scope(settings)\n"
        for name in write_safety_guard.WRITE_ROUTE_FUNCTIONS
    )
    routes.write_text(
        "def _ensure_write_alpha_test_scope(settings):\n"
        "    if settings.app_env.lower() != \"test\":\n"
        "        raise RuntimeError(\"controlled write-alpha routes are limited to explicit test-environment\")\n\n"
        f"{route_defs}\n",
        encoding="utf-8",
    )

    failures = write_safety_guard._check_write_route_test_gates(routes)

    assert any("_resolve_viewable_book only after APP_ENV=test scope" in failure for failure in failures)
    assert any("_require_book_edit_access only after APP_ENV=test scope" in failure for failure in failures)
    assert str(tmp_path) not in "; ".join(failures)


def test_write_safety_defaults_guard_rejects_missing_after_w3_boundary_marker(
    tmp_path: Path,
) -> None:
    doc = tmp_path / "after-w3-boundary.md"
    doc.write_text(
        "#36 remains open. NO_RELEASE. no public write beta. GNUCASH_WRITES_ENABLED=false. "
        "APP_ENV=test. restore-to-copy. same-context owner + PM authorization. "
        "CREATE 0 / PATCH 0 / DELETE 0.\n",
        encoding="utf-8",
    )

    failures = write_safety_guard._check_after_w3_readiness_boundary(doc)

    assert any("reset/default-disabled probes" in failure for failure in failures)
    assert any("hard stop" in failure for failure in failures)
    assert any("supported-version write compatibility remains pending" in failure for failure in failures)
    assert any("not a broad GnuCash compatibility claim" in failure for failure in failures)
    assert any("not a real-book claim" in failure for failure in failures)
    assert any("#22 closed only for narrow Desktop-generated synthetic SQLite fixture evidence" in failure for failure in failures)
    assert str(tmp_path) not in "; ".join(failures)


def test_write_safety_defaults_guard_rejects_missing_owner_writebeta_release_boundary_marker(
    tmp_path: Path,
) -> None:
    approval = tmp_path / "approval.md"
    unreleased = tmp_path / "unreleased.md"
    approval.write_text(
        "NO_RELEASE_KEEP_MAINTENANCE. not release notes. owner/PM release-candidate approval. "
        "no public write beta. GNUCASH_WRITES_ENABLED=false. APP_ENV=test.\n",
        encoding="utf-8",
    )
    unreleased.write_text(
        "UNRELEASED_UNTIL_OWNER_APPROVAL. not release authorization. "
        "No tag, GitHub release, package, image, or release notes are authorized.\n",
        encoding="utf-8",
    )

    failures = write_safety_guard._check_owner_writebeta_release_boundaries((approval, unreleased))

    assert any("no stable, production-ready, or security-audited claim" in failure for failure in failures)
    assert any("no broad GnuCash version compatibility claim" in failure for failure in failures)
    assert any("no real/private/original/working/only-copy book safety claim" in failure for failure in failures)
    assert str(tmp_path) not in "; ".join(failures)
