"""Phase 163 disposable GnuCash Desktop container probe tests."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from types import ModuleType


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "apps/api/scripts/probe_gnucash_desktop_disposable_container.py"
DESKTOP_CAPTURE_DOC = ROOT / "docs/gnucash-desktop-fixture-capture.md"


SAMPLE_OUTPUT = """
== commands ==
/usr/bin/gnucash
/usr/bin/gnucash-cli
== gnucash-version ==
Run 'g --help' to see a full list of available command line options.
Error: could not initialize graphical user interface and option add-price-quotes was not set.
Perhaps you need to set the $DISPLAY environment variable?GnuCash 4.13
Build ID: 4.13+(2022-12-17)
== gnucash-cli-version ==
GnuCash 4.13
Build ID: 4.13+(2022-12-17)
== gnucash-cli-help ==
gnucash-cli [options] [datafile] - GnuCash, accounting for personal and small business finance:
Report Generation Options:
  -R [ --report ] arg    Execute report related commands.
Price Quotes Retrieval Options:
  -Q [ --quotes ] arg    Execute price quote related commands.
== apt-policy ==
gnucash:
  Installed: (none)
  Candidate: 1:4.13-1
gnucash-common:
  Installed: (none)
  Candidate: 1:4.13-1
""".strip()


def _load_probe() -> ModuleType:
    spec = importlib.util.spec_from_file_location(
        "probe_gnucash_desktop_disposable_container", SCRIPT
    )
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_summarize_probe_output_records_container_tooling_without_claiming_fixture() -> None:
    probe = _load_probe()

    summary = probe.summarize_probe_output(SAMPLE_OUTPUT)
    serialized = json.dumps(summary, sort_keys=True)

    assert summary["commands_available"] == {"gnucash": True, "gnucash-cli": True}
    assert summary["package_candidates"] == {
        "gnucash": "1:4.13-1",
        "gnucash-common": "1:4.13-1",
    }
    assert "GnuCash 4.13" in summary["versions"]["gnucash-cli"]
    assert summary["noninteractive_sqlite_fixture_creation_supported_by_cli_help"] is False
    assert "did not find a safe noninteractive" in summary["blocker"]
    assert "/home" not in serialized
    assert "account" not in serialized.lower() or "accounting" in serialized.lower()


def test_run_container_probe_redacts_scope_and_keeps_raw_output_bounded(monkeypatch) -> None:
    probe = _load_probe()

    class Completed:
        returncode = 0
        stdout = SAMPLE_OUTPUT
        stderr = ""

    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs))
        return Completed()

    monkeypatch.setattr(probe.subprocess, "run", fake_run)

    payload = probe.run_container_probe(image="debian:12-slim", timeout_seconds=123)
    serialized = json.dumps(payload, sort_keys=True)

    assert calls[0][0][:3] == ["docker", "run", "--rm"]
    assert calls[0][1]["timeout"] == 123
    assert payload["probe_version"] == "phase-163"
    assert payload["container_scope"].startswith("temporary Docker container")
    assert payload["desktop_generated_fixture_possible_now"] is False
    assert "No GnuCash book was opened or generated" in payload["privacy"]
    assert "GnuCash 4.13" in payload["raw_output_excerpt"]
    assert "/home" not in serialized


def test_desktop_fixture_capture_doc_keeps_exact_blocker_and_evidence_requirements() -> None:
    text = DESKTOP_CAPTURE_DOC.read_text(encoding="utf-8")

    assert "## Exact blocker for #22" in text
    assert "isolated disposable GUI/manual-safe environment" in text
    assert "Desktop-generated synthetic SQLite fixture" in text
    assert "read-only validation with `GNUCASH_WRITES_ENABLED=false`" in text
    assert "No private home directory, private book, backup directory" in text
    assert "not broad GnuCash Desktop compatibility" in text
    assert "Keep #22 open" in text
