"""Phase 92 safe GnuCash compatibility metadata collector tests."""

from __future__ import annotations

import importlib.util
import json
import sqlite3
from pathlib import Path
from types import ModuleType


ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "apps/api/scripts/collect_gnucash_compatibility_metadata.py"
PROBE_SCRIPT = ROOT / "apps/api/scripts/probe_gnucash_desktop_tooling.py"


def _load_collector() -> ModuleType:
    spec = importlib.util.spec_from_file_location("collect_gnucash_compatibility_metadata", SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_probe() -> ModuleType:
    spec = importlib.util.spec_from_file_location("probe_gnucash_desktop_tooling", PROBE_SCRIPT)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _create_minimal_book(path: Path) -> None:
    with sqlite3.connect(path) as conn:
        conn.execute("create table versions (table_name text primary key, table_version integer not null)")
        conn.executemany(
            "insert into versions (table_name, table_version) values (?, ?)",
            [("Gnucash", 3_000_000), ("Gnucash-Resave", 19_920)],
        )
        conn.execute("create table accounts (guid text primary key, name text)")
        conn.execute("create table transactions (guid text primary key, description text)")
        conn.execute("create table splits (guid text primary key, memo text, value_num integer, value_denom integer)")
        conn.execute("create table commodities (guid text primary key, fullname text)")
        conn.execute("create table books (guid text primary key, root_account_guid text)")
        conn.executemany(
            "insert into accounts (guid, name) values (?, ?)",
            [("a", "Private Checking"), ("b", "Private Income")],
        )
        conn.execute(
            "insert into transactions (guid, description) values (?, ?)",
            ("t", "Private salary"),
        )
        conn.execute(
            "insert into splits (guid, memo, value_num, value_denom) values (?, ?, ?, ?)",
            ("s", "Private memo 123", 12345, 100),
        )
        conn.execute(
            "insert into commodities (guid, fullname) values (?, ?)",
            ("c", "Private commodity name"),
        )
        conn.execute(
            "insert into books (guid, root_account_guid) values (?, ?)",
            ("book", "a"),
        )


def test_collector_reports_safe_schema_metadata_without_private_values(tmp_path: Path) -> None:
    collector = _load_collector()
    book_path = tmp_path / "desktop-synthetic-fixture.gnucash.sqlite"
    _create_minimal_book(book_path)

    metadata = collector.collect_metadata(
        book_path,
        gnucash_version="GnuCash 5.10",
        fixture_origin="desktop-generated-synthetic",
    )

    assert metadata["format"] == "GnuCash SQLite"
    assert metadata["gnucash_desktop_version"] == "GnuCash 5.10"
    assert metadata["book_path"] == "<redacted>"
    assert metadata["versions"] == {"Gnucash": 3_000_000, "Gnucash-Resave": 19_920}
    assert metadata["fixture_origin"] == "desktop-generated-synthetic"
    assert metadata["desktop_generated_synthetic_fixture"] is True
    assert metadata["candidate_acceptance"]["accepted"] is True
    assert metadata["candidate_acceptance"]["checked"] is True
    assert metadata["table_counts"] == {
        "accounts": 2,
        "transactions": 1,
        "splits": 1,
        "commodities": 1,
        "books": 1,
    }
    assert metadata["runtime_context"]["python_version"]
    assert metadata["runtime_context"]["sqlite_version"] == sqlite3.sqlite_version
    assert metadata["runtime_context"]["piecash_version"]
    assert metadata["runtime_context"]["collector_version"] == "phase-203"
    assert "split memos" in metadata["redaction_contract"]["excluded_row_fields"]
    assert "split amounts" in metadata["redaction_contract"]["excluded_row_fields"]
    serialized = json.dumps(metadata, sort_keys=True)
    assert str(book_path) not in serialized
    assert "Private Checking" not in serialized
    assert "Private salary" not in serialized
    assert "Private memo" not in serialized
    assert "12345" not in serialized
    assert "Private commodity" not in serialized


def test_collector_cli_writes_safe_json(tmp_path: Path, capsys) -> None:
    collector = _load_collector()
    book_path = tmp_path / "desktop-synthetic-fixture.gnucash.sqlite"
    output_path = tmp_path / "metadata.json"
    _create_minimal_book(book_path)

    collector.main([
        str(book_path),
        "--gnucash-version",
        "GnuCash 5.10",
        "--fixture-origin",
        "desktop-generated-synthetic",
        "--output",
        str(output_path),
    ])

    captured = capsys.readouterr()
    assert "Compatibility metadata written" in captured.out
    data = json.loads(output_path.read_text(encoding="utf-8"))
    assert data["book_path"] == "<redacted>"
    assert data["gnucash_desktop_version"] == "GnuCash 5.10"
    assert data["desktop_generated_synthetic_fixture"] is True
    assert data["candidate_acceptance"]["accepted"] is True
    assert data["versions"]["Gnucash"] == 3_000_000
    assert str(book_path) not in output_path.read_text(encoding="utf-8")


def test_desktop_fixture_candidate_rejections_are_deterministic_and_path_safe(tmp_path: Path, capsys) -> None:
    collector = _load_collector()
    bad_book_path = tmp_path / "private-production-book.gnucash.sqlite"
    _create_minimal_book(bad_book_path)

    try:
        collector.main([
            str(bad_book_path),
            "--fixture-origin",
            "desktop-generated-synthetic",
            "--gnucash-version",
            "GnuCash 5.10",
        ])
    except SystemExit as exc:
        assert exc.code == 2
    else:  # pragma: no cover - defensive clarity for failed rejection
        raise AssertionError("unsafe Desktop fixture candidate was accepted")

    captured = capsys.readouterr()
    assert "Compatibility metadata rejected" in captured.err
    assert "forbidden non-disposable marker" in captured.err
    assert str(bad_book_path) not in captured.err
    assert "private-production-book" not in captured.err


def test_desktop_fixture_candidate_refuses_forbidden_runtime_classes(tmp_path: Path, monkeypatch) -> None:
    collector = _load_collector()
    repo_root = tmp_path / "repo"
    monkeypatch.setattr(collector, "_repo_root", lambda: repo_root)
    forbidden_book = repo_root / "data" / "backups" / "desktop-synthetic-fixture.gnucash.sqlite"
    forbidden_book.parent.mkdir(parents=True)
    _create_minimal_book(forbidden_book)

    try:
        collector.collect_metadata(
            forbidden_book,
            fixture_origin="desktop-generated-synthetic",
            gnucash_version="GnuCash 5.10",
        )
    except collector.SafeCandidateError as exc:
        serialized = json.dumps(exc.reasons, sort_keys=True)
        assert "forbidden repo runtime/secrets class" in serialized
        assert str(forbidden_book) not in serialized
    else:  # pragma: no cover - defensive clarity for failed rejection
        raise AssertionError("forbidden runtime class was accepted")


def test_desktop_tooling_probe_records_only_safe_availability_metadata(monkeypatch) -> None:
    probe = _load_probe()

    monkeypatch.setattr(probe.shutil, "which", lambda command: f"/private/bin/{command}")

    class Completed:
        returncode = 0
        stdout = "GnuCash 5.10\n"
        stderr = ""

    monkeypatch.setattr(probe.subprocess, "run", lambda *args, **kwargs: Completed())

    metadata = probe.probe_tooling()
    serialized = json.dumps(metadata, sort_keys=True)

    assert metadata["probe"] == "gnucash-desktop-tooling"
    assert metadata["probe_version"] == "phase-154"
    assert metadata["desktop_tooling_available"] is True
    assert metadata["commands"]["gnucash"]["version_output"] == "GnuCash 5.10"
    assert metadata["commands"]["gnucash"]["executable_path_recorded"] == "<redacted>"
    assert "/private/bin" not in serialized
    assert "book" in metadata["privacy"].lower()


def test_desktop_tooling_probe_handles_unavailable_tools_without_private_paths(monkeypatch) -> None:
    probe = _load_probe()
    monkeypatch.setattr(probe.shutil, "which", lambda command: None)

    metadata = probe.probe_tooling()
    serialized = json.dumps(metadata, sort_keys=True)

    assert metadata["desktop_tooling_available"] is False
    assert metadata["desktop_generated_fixture_possible_now"] is False
    assert metadata["commands"]["gnucash"]["available"] is False
    assert metadata["commands"]["gnucash-cli"]["available"] is False
    assert metadata["commands"]["gnucash"]["missing_reason"] == "gnucash not found on PATH"
    assert "not found" in serialized
    assert "/home" not in serialized


def test_desktop_tooling_probe_can_add_non_mutating_install_hints(monkeypatch) -> None:
    probe = _load_probe()
    monkeypatch.setattr(
        probe.shutil,
        "which",
        lambda command: "/usr/bin/apt-cache" if command == "apt-cache" else None,
    )

    class Completed:
        returncode = 0
        stdout = "gnucash:\n  Installed: (none)\n  Candidate: 1:5.14-1build1\n"
        stderr = ""

    monkeypatch.setattr(probe.subprocess, "run", lambda *args, **kwargs: Completed())

    metadata = probe.probe_tooling(include_install_hints=True)
    serialized = json.dumps(metadata, sort_keys=True)

    assert metadata["install_hints"]["checked"] is True
    assert metadata["install_hints"]["packages"]["gnucash"]["candidate"] == "1:5.14-1build1"
    assert "apt-cache policy gnucash" in serialized
    assert "No GnuCash book was opened" in metadata["privacy"]
    assert "/home" not in serialized
