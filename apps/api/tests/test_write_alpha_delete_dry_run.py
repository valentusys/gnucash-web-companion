"""Regression tests for the non-mutating DELETE planning dry-run helper."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import sqlite3
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT_PATH = REPO_ROOT / "scripts" / "write_alpha_delete_dry_run.py"

spec = importlib.util.spec_from_file_location("write_alpha_delete_dry_run", SCRIPT_PATH)
assert spec is not None
helper = importlib.util.module_from_spec(spec)
assert spec.loader is not None
sys.modules["write_alpha_delete_dry_run"] = helper
spec.loader.exec_module(helper)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _synthetic_book(path: Path, transaction_id: str = "tx-write-alpha-created") -> None:
    with sqlite3.connect(path) as conn:
        conn.execute("create table transactions (guid text primary key)")
        conn.execute("create table splits (guid text primary key, tx_guid text not null)")
        conn.execute("insert into transactions (guid) values (?)", (transaction_id,))
        conn.execute("insert into splits (guid, tx_guid) values ('split-1', ?)", (transaction_id,))
        conn.execute("insert into splits (guid, tx_guid) values ('split-2', ?)", (transaction_id,))


def _app_db(path: Path, transaction_id: str = "tx-write-alpha-created") -> None:
    with sqlite3.connect(path) as conn:
        conn.execute("create table write_alpha_transaction_ownership (book_id integer, transaction_id text, created_by_write_alpha integer)")
        conn.execute("create table audit_logs (id integer primary key autoincrement, action text)")
        conn.execute(
            "insert into write_alpha_transaction_ownership (book_id, transaction_id, created_by_write_alpha) values (1, ?, 1)",
            (transaction_id,),
        )


def _base_args(tmp_path: Path, book: Path, app_db: Path, evidence: Path) -> list[str]:
    return [
        "--target",
        str(book),
        "--transaction-id",
        "tx-write-alpha-created",
        "--app-db",
        str(app_db),
        "--book-id",
        "1",
        "--backup-dir",
        str(tmp_path / "backups"),
        "--evidence-file",
        str(evidence),
        "--confirm-synthetic-disposable",
        "--confirm-no-delete-route",
    ]


def test_delete_dry_run_proves_book_and_app_db_are_not_mutated(tmp_path, monkeypatch):
    monkeypatch.delenv("GNUCASH_WRITES_ENABLED", raising=False)
    monkeypatch.setenv("APP_ENV", "development")
    book = tmp_path / "synthetic-delete-target.gnucash.sqlite"
    app_db = tmp_path / "app.db"
    evidence = tmp_path / "evidence" / "delete-dry-run.json"
    _synthetic_book(book)
    _app_db(app_db)
    before_book = _sha256(book)
    before_app = _sha256(app_db)

    result = helper.main(_base_args(tmp_path, book, app_db, evidence))

    assert result == 0
    assert _sha256(book) == before_book
    assert _sha256(app_db) == before_app
    data = json.loads(evidence.read_text(encoding="utf-8"))
    assert data["result"] == "pass"
    assert data["mode"] == "delete-dry-run"
    assert data["delete_route_called"] is False
    assert data["mutation_performed"] is False
    assert data["book_checksum_stable"] is True
    assert data["app_db_checksum_stable"] is True
    assert data["delete_audit_rows_before"] == 0
    assert data["delete_audit_rows_after"] == 0
    assert data["target_eligibility_status"] == "write-alpha-owned"
    assert data["split_count"] == 2
    assert str(tmp_path) not in evidence.read_text(encoding="utf-8")


def test_delete_dry_run_blocks_if_writes_are_enabled(tmp_path, monkeypatch):
    monkeypatch.setenv("GNUCASH_WRITES_ENABLED", "true")
    book = tmp_path / "synthetic-delete-target.gnucash.sqlite"
    app_db = tmp_path / "app.db"
    evidence = tmp_path / "evidence.json"
    _synthetic_book(book)
    _app_db(app_db)

    result = helper.main(_base_args(tmp_path, book, app_db, evidence))

    assert result == 2
    assert not evidence.exists()


def test_delete_dry_run_blocks_non_write_alpha_owned_target(tmp_path, monkeypatch):
    monkeypatch.delenv("GNUCASH_WRITES_ENABLED", raising=False)
    book = tmp_path / "synthetic-delete-target.gnucash.sqlite"
    app_db = tmp_path / "app.db"
    evidence = tmp_path / "evidence.json"
    _synthetic_book(book)
    with sqlite3.connect(app_db) as conn:
        conn.execute("create table write_alpha_transaction_ownership (book_id integer, transaction_id text, created_by_write_alpha integer)")
        conn.execute("create table audit_logs (id integer primary key autoincrement, action text)")

    result = helper.main(_base_args(tmp_path, book, app_db, evidence))

    assert result == 2
    assert not evidence.exists()
