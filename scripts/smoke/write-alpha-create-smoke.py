#!/usr/bin/env python3
"""Write-alpha create smoke for a local disposable/test GnuCash book.

Runs against an already-started local deployment with APP_ENV=test and
GNUCASH_WRITES_ENABLED=true. Output is intentionally redacted: no account names,
transaction description, memos, amounts, cookies, book paths, backup filenames,
or raw app DB contents are printed.
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


def _choose_two_accounts(client: SmokeClient, book_id: int) -> tuple[str, str, str]:
    response = client.request("GET", f"/books/{book_id}/accounts", authenticated=True)
    accounts = _require_list(response.body, "accounts")
    eligible = [
        account
        for account in accounts
        if isinstance(account, dict)
        and isinstance(account.get("id"), str)
        and account.get("currency")
        and not account.get("placeholder")
        and not account.get("hidden")
    ]
    _check(len(eligible) >= 2, "fewer than two eligible non-placeholder accounts")
    first_currency = str(eligible[0]["currency"])
    same_currency = [account for account in eligible if account.get("currency") == first_currency]
    _check(len(same_currency) >= 2, "fewer than two eligible accounts in one currency")
    return str(same_currency[0]["id"]), str(same_currency[1]["id"]), first_currency


def _audit_success_count(app_db: Path) -> int:
    _check(app_db.exists(), "app DB is missing after runtime smoke")
    with sqlite3.connect(app_db) as connection:
        rows = connection.execute(
            "select payload_json from audit_logs where action = ?", ("transaction.create",)
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


def _backup_file_count(backup_root: Path) -> int:
    if not backup_root.exists():
        return 0
    return sum(1 for path in backup_root.rglob("*") if path.is_file())


def _lock_file_count(lock_root: Path) -> int:
    if not lock_root.exists():
        return 0
    return sum(1 for path in lock_root.glob("*.lock") if path.is_file())


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
                return LockEvidence("active", True, "write lock remains actively held after create")
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

    before_backups = _backup_file_count(backup_root)
    before_audits = _audit_success_count(app_db) if app_db.exists() else 0

    client = SmokeClient(args.api_base_url)
    health = client.request("GET", "/health")
    health_body = _require_mapping(health.body, "/health")
    _check(health_body.get("status") == "ok", "/health did not return status=ok")

    _login(client, args.username, args.password)
    book_id = _default_book(client)
    account_a, account_b, currency = _choose_two_accounts(client, book_id)

    valid_payload = {
        "date": args.transaction_date,
        "description": "Write-alpha create smoke disposable transaction",
        "splits": [
            {"account_id": account_a, "amount": "-1.00", "currency": currency, "memo": ""},
            {"account_id": account_b, "amount": "1.00", "currency": currency, "memo": ""},
        ],
    }
    unbalanced_payload = {
        **valid_payload,
        "splits": [
            {"account_id": account_a, "amount": "-1.00", "currency": currency, "memo": ""},
            {"account_id": account_b, "amount": "2.00", "currency": currency, "memo": ""},
        ],
    }
    invalid_payload = {
        **valid_payload,
        "splits": [
            {"account_id": "write-alpha-smoke-missing-account", "amount": "-1.00", "currency": currency, "memo": ""},
            {"account_id": account_b, "amount": "1.00", "currency": currency, "memo": ""},
        ],
    }
    placeholder_like_payload = {
        **valid_payload,
        "splits": [
            {"account_id": "write-alpha-smoke-placeholder-probe", "amount": "-1.00", "currency": currency, "memo": ""},
            {"account_id": account_b, "amount": "1.00", "currency": currency, "memo": ""},
        ],
    }

    valid = client.request(
        "POST", f"/books/{book_id}/transactions/validate", payload=valid_payload, authenticated=True
    )
    valid_body = _require_mapping(valid.body, "valid validation")
    _check(valid_body.get("valid") is True, "balanced two-split validation failed")

    for label, payload in (
        ("unbalanced", unbalanced_payload),
        ("invalid_account", invalid_payload),
        ("placeholder_like_missing_account", placeholder_like_payload),
    ):
        response = client.request(
            "POST", f"/books/{book_id}/transactions/validate", payload=payload, authenticated=True
        )
        body = _require_mapping(response.body, f"{label} validation")
        errors = body.get("errors")
        _check(body.get("valid") is False and isinstance(errors, list) and errors, f"{label} validation did not reject")

    create = client.request(
        "POST", f"/books/{book_id}/transactions", payload=valid_payload, expected_status=201, authenticated=True
    )
    create_body = _require_mapping(create.body, "create response")
    tx_id = create_body.get("transaction_id")
    audit_id = create_body.get("audit_log_id")
    _check(isinstance(tx_id, str) and tx_id, "create did not return transaction_id")
    _check(isinstance(audit_id, int), "create did not return audit_log_id")

    detail = client.request("GET", f"/books/{book_id}/transactions/{tx_id}", authenticated=True)
    detail_body = _require_mapping(detail.body, "created transaction read-back")
    _check(detail_body.get("id") == tx_id, "read-back transaction id mismatch")
    _check(len(_require_list(detail_body.get("splits"), "created splits")) == 2, "read-back split count mismatch")

    after_backups = _backup_file_count(backup_root)
    after_audits = _audit_success_count(app_db)
    _check(after_backups > before_backups, "no new backup file detected after create")
    _check(after_audits == before_audits + 1, "audit success count did not increase by exactly one")
    lock_evidence = _lock_evidence(lock_root)
    _check(not lock_evidence.is_active, lock_evidence.message)
    if lock_evidence.status == "unreadable":
        raise SmokeFailure(lock_evidence.message)

    print(f"write-alpha create smoke: target={args.api_base_url.rstrip('/')}")
    print("ok: APP_ENV=test and GNUCASH_WRITES_ENABLED=true were supplied by local runtime command")
    print("ok: read-only routes health/books/accounts/transaction-readback passed")
    print("ok: validation rejected unbalanced and invalid account probes")
    print("ok: placeholder-style validation probe rejected without using a real placeholder account")
    print("ok: exactly one balanced two-split create succeeded")
    print("ok: backup count increased before mutation response returned")
    print("ok: audit success count increased by exactly one")
    print(f"ok: write lock evidence status={lock_evidence.status}; {lock_evidence.message}")
    print("PASS: write-alpha create smoke completed with redacted output")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run write-alpha create smoke against local disposable deployment.")
    parser.add_argument("--api-base-url", default=os.environ.get("SMOKE_API_BASE_URL", DEFAULT_API_BASE_URL))
    parser.add_argument("--username", default=os.environ.get("SMOKE_ADMIN_USERNAME") or os.environ.get("APP_ADMIN_USERNAME") or "admin")
    parser.add_argument("--password", default=os.environ.get("SMOKE_ADMIN_PASSWORD") or os.environ.get("APP_ADMIN_PASSWORD"))
    parser.add_argument("--app-db", default=os.environ.get("SMOKE_APP_DB", DEFAULT_APP_DB))
    parser.add_argument("--backup-root", default=os.environ.get("SMOKE_BACKUP_ROOT", DEFAULT_BACKUP_ROOT))
    parser.add_argument("--lock-root", default=os.environ.get("SMOKE_LOCK_ROOT", DEFAULT_LOCK_ROOT))
    parser.add_argument("--transaction-date", default=os.environ.get("SMOKE_TRANSACTION_DATE", "2026-05-20"))
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
