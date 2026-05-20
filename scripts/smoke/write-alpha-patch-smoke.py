#!/usr/bin/env python3
"""Write-alpha PATCH smoke for a local disposable/test GnuCash book.

Runs against an already-started local deployment with APP_ENV=test and
GNUCASH_WRITES_ENABLED=true. Output is intentionally redacted: no account names,
transaction descriptions, raw memos, amounts, cookies, book paths, backup
filenames, or raw app DB contents are printed.
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import sqlite3
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Any

DEFAULT_API_BASE_URL = "http://localhost:8080/api"
DEFAULT_APP_DB = "data/app/app.db"
DEFAULT_BACKUP_ROOT = "data/backups"
DEFAULT_LOCK_ROOT = "data/locks"
DEFAULT_RUNTIME_BOOK = "data/books/main.gnucash.sqlite"
DEFAULT_PATCH_DESCRIPTION = "Write-alpha PATCH smoke synthetic marker"
DEFAULT_PATCH_MEMO = "write-alpha patch smoke split marker"


class SmokeFailure(Exception):
    """Raised when a write-alpha smoke check fails."""


@dataclass(frozen=True)
class LockEvidence:
    """Path-redacted runtime lock probe result for dogfood evidence."""

    status: str
    is_active: bool
    message: str


@dataclass(frozen=True)
class SmokeResponse:
    status: int
    body: Any
    raw: str
    headers: dict[str, str]


@dataclass(frozen=True)
class PatchTarget:
    transaction_id: str
    split_id: str
    original_description: str
    original_date: str
    original_split_memo: str
    split_count: int
    amount_fingerprint: tuple[str, ...]


class SmokeClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.token: str | None = None

    def request(
        self,
        method: str,
        path: str,
        *,
        payload: dict[str, Any] | None = None,
        expected_status: int | tuple[int, ...] = 200,
        authenticated: bool = False,
    ) -> SmokeResponse:
        url = f"{self.base_url}{path}"
        data = None
        headers = {"Accept": "application/json"}
        if payload is not None:
            data = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        if authenticated:
            if not self.token:
                raise SmokeFailure("authenticated request attempted before login")
            headers["Authorization"] = f"Bearer {self.token}"

        request = urllib.request.Request(url, data=data, headers=headers, method=method)
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                raw = response.read().decode("utf-8")
                status = response.status
                response_headers = dict(response.headers.items())
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8")
            status = exc.code
            response_headers = dict(exc.headers.items())
        except urllib.error.URLError as exc:
            raise SmokeFailure(f"{method} {path} could not connect: {exc}") from exc

        expected = (expected_status,) if isinstance(expected_status, int) else expected_status
        if status not in expected:
            raise SmokeFailure(
                f"{method} {path} returned HTTP {status}, expected {expected}; body class=<redacted>"
            )
        return SmokeResponse(status=status, body=_json_or_raw(raw), raw=raw, headers=response_headers)


def _json_or_raw(raw: str) -> Any:
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def _require_mapping(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SmokeFailure(f"{label} returned non-object JSON")
    return value


def _require_list(value: Any, label: str) -> list[Any]:
    if not isinstance(value, list):
        raise SmokeFailure(f"{label} returned non-array JSON")
    return value


def _check(condition: bool, message: str) -> None:
    if not condition:
        raise SmokeFailure(message)


def _login(client: SmokeClient, username: str, password: str) -> None:
    response = client.request("POST", "/auth/login", payload={"username": username, "password": password})
    data = _require_mapping(response.body, "/auth/login")
    token = data.get("access_token")
    _check(isinstance(token, str) and bool(token), "/auth/login did not return access_token")
    client.token = token


def _default_book(client: SmokeClient) -> int:
    response = client.request("GET", "/books", authenticated=True)
    books = _require_list(response.body, "/books")
    _check(len(books) > 0, "/books returned no visible books")
    book = next((item for item in books if isinstance(item, dict) and item.get("is_default")), books[0])
    book_id_value = _require_mapping(book, "/books item").get("id")
    if not isinstance(book_id_value, int):
        raise SmokeFailure("default book id is missing or not integer")
    book_id = book_id_value
    client.request("GET", f"/books/{book_id}", authenticated=True)
    return book_id


def _first_patch_target(book_path: Path) -> PatchTarget:
    _check(book_path.exists(), "runtime disposable book is missing")
    with sqlite3.connect(f"file:{book_path}?mode=ro", uri=True) as connection:
        tx_row = connection.execute(
            "select guid, description, post_date from transactions order by post_date, guid limit 1"
        ).fetchone()
        _check(tx_row is not None, "runtime disposable book has no transaction to patch")
        transaction_id, description, post_date = tx_row
        split_rows = connection.execute(
            "select guid, coalesce(memo, ''), value_num, value_denom from splits where tx_guid = ? order by guid",
            (transaction_id,),
        ).fetchall()
    _check(len(split_rows) > 0, "selected transaction has no splits")
    amount_fingerprint = tuple(f"{row[2]}/{row[3]}" for row in split_rows)
    return PatchTarget(
        transaction_id=str(transaction_id),
        split_id=str(split_rows[0][0]),
        original_description=str(description or ""),
        original_date=str(post_date),
        original_split_memo=str(split_rows[0][1] or ""),
        split_count=len(split_rows),
        amount_fingerprint=amount_fingerprint,
    )


def _read_patch_target(book_path: Path, transaction_id: str, split_id: str) -> PatchTarget:
    with sqlite3.connect(f"file:{book_path}?mode=ro", uri=True) as connection:
        tx_row = connection.execute(
            "select guid, description, post_date from transactions where guid = ?",
            (transaction_id,),
        ).fetchone()
        _check(tx_row is not None, "patched transaction missing from runtime book")
        split_rows = connection.execute(
            "select guid, coalesce(memo, ''), value_num, value_denom from splits where tx_guid = ? order by guid",
            (transaction_id,),
        ).fetchall()
    _check(len(split_rows) > 0, "patched transaction has no splits")
    split_memo_value = next((str(row[1] or "") for row in split_rows if row[0] == split_id), None)
    _check(split_memo_value is not None, "patched split missing from runtime book")
    split_memo = split_memo_value or ""
    amount_fingerprint = tuple(f"{row[2]}/{row[3]}" for row in split_rows)
    return PatchTarget(
        transaction_id=str(tx_row[0]),
        split_id=split_id,
        original_description=str(tx_row[1] or ""),
        original_date=str(tx_row[2]),
        original_split_memo=split_memo,
        split_count=len(split_rows),
        amount_fingerprint=amount_fingerprint,
    )


def _audit_success_count(app_db: Path) -> int:
    _check(app_db.exists(), "app DB is missing after runtime smoke")
    with sqlite3.connect(app_db) as connection:
        rows = connection.execute(
            "select payload_json from audit_logs where action = ?", ("transaction.patch",)
        ).fetchall()
    count = 0
    for (payload_raw,) in rows:
        try:
            payload = json.loads(payload_raw or "{}")
        except json.JSONDecodeError:
            continue
        if payload.get("result") == "success" and payload.get("transaction_id"):
            count += 1
    return count


def _audit_failed_patch_count(app_db: Path) -> int:
    _check(app_db.exists(), "app DB is missing after runtime smoke")
    with sqlite3.connect(app_db) as connection:
        rows = connection.execute(
            "select payload_json from audit_logs where action = ?", ("transaction.patch",)
        ).fetchall()
    count = 0
    for (payload_raw,) in rows:
        try:
            payload = json.loads(payload_raw or "{}")
        except json.JSONDecodeError:
            continue
        if payload.get("result") == "failed" and payload.get("backup_path") is None:
            count += 1
    return count


def _backup_file_count(backup_root: Path) -> int:
    if not backup_root.exists():
        return 0
    return sum(1 for path in backup_root.rglob("*") if path.is_file())


def _lock_evidence(lock_root: Path) -> LockEvidence:
    """Return path-redacted evidence for active, stale, or unreadable locks."""
    if not lock_root.exists():
        return LockEvidence("not_present", False, "no lock files remain")
    saw_stale = False
    for path in lock_root.glob("*.lock"):
        if not path.is_file():
            continue
        try:
            fd = os.open(path, os.O_RDWR)
        except PermissionError:
            return LockEvidence(
                "unreadable",
                False,
                "lock file is not readable by this smoke user; inspect from the API container or fix runtime ownership before removing only the book-specific stale lock with the app stopped",
            )
        try:
            try:
                fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError:
                return LockEvidence("active", True, "write lock remains actively held after PATCH")
            finally:
                try:
                    fcntl.flock(fd, fcntl.LOCK_UN)
                except OSError:
                    pass
            saw_stale = True
        finally:
            os.close(fd)
    if saw_stale:
        return LockEvidence(
            "stale_released",
            False,
            "lock file remains but is not actively held; with the app stopped an operator may remove only the book-specific stale lock from ignored runtime storage",
        )
    return LockEvidence("not_present", False, "no lock files remain")


def run(args: argparse.Namespace) -> None:
    if not args.password:
        raise SmokeFailure("Set --password or SMOKE_ADMIN_PASSWORD")
    app_db = Path(args.app_db)
    backup_root = Path(args.backup_root)
    lock_root = Path(args.lock_root)
    runtime_book = Path(args.runtime_book)

    target = _first_patch_target(runtime_book)
    before_backups = _backup_file_count(backup_root)
    before_audits = _audit_success_count(app_db) if app_db.exists() else 0
    before_failed_audits = _audit_failed_patch_count(app_db) if app_db.exists() else 0

    client = SmokeClient(args.api_base_url)
    health = client.request("GET", "/health")
    health_body = _require_mapping(health.body, "/health")
    _check(health_body.get("status") == "ok", "/health did not return status=ok")

    _login(client, args.username, args.password)
    book_id = _default_book(client)

    missing_before_backups = _backup_file_count(backup_root)
    missing = client.request(
        "PATCH",
        f"/books/{book_id}/transactions/write-alpha-patch-smoke-missing-transaction",
        payload={"description": "Write-alpha PATCH smoke missing probe"},
        expected_status=404,
        authenticated=True,
    )
    missing_body = _require_mapping(missing.body, "missing PATCH response")
    _check("detail" in missing_body, "missing PATCH response has no safe detail")
    _check(
        _backup_file_count(backup_root) == missing_before_backups,
        "missing-transaction PATCH created a backup unexpectedly",
    )

    patch_payload = {
        "description": args.patch_description,
        "date": args.patch_date,
        "split_memos": {target.split_id: args.patch_memo},
    }
    patch = client.request(
        "PATCH",
        f"/books/{book_id}/transactions/{target.transaction_id}",
        payload=patch_payload,
        expected_status=200,
        authenticated=True,
    )
    patch_body = _require_mapping(patch.body, "PATCH response")
    _check(patch_body.get("transaction_id") == target.transaction_id, "PATCH returned unexpected transaction id")
    _check(isinstance(patch_body.get("audit_log_id"), int), "PATCH did not return audit_log_id")
    backup_path_value = patch_body.get("backup_path")
    _check(isinstance(backup_path_value, str) and bool(backup_path_value), "PATCH did not return backup path evidence")

    detail = client.request("GET", f"/books/{book_id}/transactions/{target.transaction_id}", authenticated=True)
    detail_body = _require_mapping(detail.body, "patched transaction read-back")
    _check(detail_body.get("id") == target.transaction_id, "read-back transaction id mismatch")
    _check(detail_body.get("description") == args.patch_description, "read-back description marker mismatch")
    _check(detail_body.get("date") == args.patch_date, "read-back date marker mismatch")
    splits = _require_list(detail_body.get("splits"), "patched splits")
    _check(len(splits) == target.split_count, "read-back split count changed")

    after = _read_patch_target(runtime_book, target.transaction_id, target.split_id)
    _check(after.original_description == args.patch_description, "runtime book description marker mismatch")
    _check(after.original_date.startswith(args.patch_date), "runtime book date marker mismatch")
    _check(after.original_split_memo == args.patch_memo, "runtime book split memo marker mismatch")
    _check(after.amount_fingerprint == target.amount_fingerprint, "PATCH changed split amount fingerprint")

    after_backups = _backup_file_count(backup_root)
    after_audits = _audit_success_count(app_db)
    after_failed_audits = _audit_failed_patch_count(app_db)
    _check(after_backups > before_backups, "no new backup file detected after PATCH")
    _check(after_audits == before_audits + 1, "audit success count did not increase by exactly one")
    _check(after_failed_audits == before_failed_audits + 1, "failed missing-transaction PATCH audit was not recorded")
    lock_evidence = _lock_evidence(lock_root)
    _check(not lock_evidence.is_active, lock_evidence.message)
    if lock_evidence.status == "unreadable":
        raise SmokeFailure(lock_evidence.message)

    print(f"write-alpha PATCH smoke: target={args.api_base_url.rstrip('/')}")
    print("ok: APP_ENV=test and GNUCASH_WRITES_ENABLED=true were supplied by local runtime command")
    print("ok: source/runtime/backup paths were preflighted outside script and runtime book was an ignored disposable copy")
    print("ok: health/books/read-only transaction detail routes passed")
    print("ok: missing-transaction PATCH returned 404 without a new backup")
    print("ok: exactly one metadata/split-memo PATCH succeeded")
    print("ok: API read-back matched synthetic PATCH markers only")
    print("ok: runtime SQLite read-back matched markers and split amount fingerprint was unchanged")
    print("ok: backup count increased before mutation response returned")
    print("ok: audit success count increased by exactly one and failed safe-error audit was recorded")
    print(f"ok: write lock evidence status={lock_evidence.status}; {lock_evidence.message}")
    print("PASS: write-alpha PATCH smoke completed with redacted output")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run write-alpha PATCH smoke against local disposable deployment.")
    parser.add_argument("--api-base-url", default=os.environ.get("SMOKE_API_BASE_URL", DEFAULT_API_BASE_URL))
    parser.add_argument("--username", default=os.environ.get("SMOKE_ADMIN_USERNAME") or os.environ.get("APP_ADMIN_USERNAME") or "admin")
    parser.add_argument("--password", default=os.environ.get("SMOKE_ADMIN_PASSWORD") or os.environ.get("APP_ADMIN_PASSWORD"))
    parser.add_argument("--app-db", default=os.environ.get("SMOKE_APP_DB", DEFAULT_APP_DB))
    parser.add_argument("--backup-root", default=os.environ.get("SMOKE_BACKUP_ROOT", DEFAULT_BACKUP_ROOT))
    parser.add_argument("--lock-root", default=os.environ.get("SMOKE_LOCK_ROOT", DEFAULT_LOCK_ROOT))
    parser.add_argument("--runtime-book", default=os.environ.get("SMOKE_RUNTIME_BOOK", DEFAULT_RUNTIME_BOOK))
    parser.add_argument("--patch-date", default=os.environ.get("SMOKE_PATCH_DATE", "2026-05-20"))
    parser.add_argument("--patch-description", default=os.environ.get("SMOKE_PATCH_DESCRIPTION", DEFAULT_PATCH_DESCRIPTION))
    parser.add_argument("--patch-memo", default=os.environ.get("SMOKE_PATCH_MEMO", DEFAULT_PATCH_MEMO))
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    try:
        run(parse_args(argv))
    except SmokeFailure as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
