#!/usr/bin/env python3
"""Read-only API smoke test for a local gnucash-web-companion deployment.

This script is intentionally minimal and uses only Python's standard library.
Run it against a local Docker deployment with a disposable/synthetic or copied
GnuCash SQL book. It does not require or commit real financial data.

Default target is the Caddy proxy API path used by docker-compose:

    SMOKE_ADMIN_PASSWORD='...' scripts/smoke/read-only-api-smoke.py

Optional environment variables:

    SMOKE_API_BASE_URL       API base URL, default http://localhost:8080/api
    SMOKE_ADMIN_USERNAME     admin username, default APP_ADMIN_USERNAME or admin
    SMOKE_ADMIN_PASSWORD     admin password, default APP_ADMIN_PASSWORD

The script verifies health, login, /auth/me, default book discovery, accounts,
transactions, scheduled transaction metadata, reports summary, write-alpha audit
summary, and that controlled-write endpoints return 403 while
GNUCASH_WRITES_ENABLED=false.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


DEFAULT_API_BASE_URL = "http://localhost:8080/api"


@dataclass(frozen=True)
class SmokeResponse:
    status: int
    body: Any
    raw: str
    headers: dict[str, str]


class SmokeFailure(RuntimeError):
    """Raised when a smoke check fails."""


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
            with urllib.request.urlopen(request, timeout=15) as response:
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
                f"{method} {path} returned HTTP {status}, expected {expected}; body: {raw[:500]}"
            )

        return SmokeResponse(status=status, body=_json_or_raw(raw), raw=raw, headers=response_headers)


def _json_or_raw(raw: str) -> Any:
    if not raw:
        return None
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def _require_mapping(value: Any, path: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise SmokeFailure(f"{path} returned non-object JSON: {value!r}")
    return value


def _require_list(value: Any, path: str) -> list[Any]:
    if not isinstance(value, list):
        raise SmokeFailure(f"{path} returned non-array JSON: {value!r}")
    return value


def _check(condition: bool, message: str) -> None:
    if not condition:
        raise SmokeFailure(message)


def _login(client: SmokeClient, username: str, password: str) -> None:
    response = client.request(
        "POST",
        "/auth/login",
        payload={"username": username, "password": password},
    )
    data = _require_mapping(response.body, "/auth/login")
    token = data.get("access_token")
    _check(isinstance(token, str) and bool(token), "/auth/login did not return access_token")
    client.token = token


def _find_default_book(client: SmokeClient) -> dict[str, Any]:
    books_response = client.request("GET", "/books", authenticated=True)
    books = _require_list(books_response.body, "/books")
    _check(len(books) > 0, "/books returned no visible books")

    default_book = next((book for book in books if isinstance(book, dict) and book.get("is_default")), None)
    if default_book is None:
        default_book = books[0]

    book_id = _require_mapping(default_book, "/books item").get("id")
    _check(isinstance(book_id, int), "default book id is missing or not an integer")

    book_response = client.request("GET", f"/books/{book_id}", authenticated=True)
    book = _require_mapping(book_response.body, f"/books/{book_id}")
    _check(book.get("id") == book_id, f"/books/{book_id} returned unexpected book id")
    return book


def _assert_write_disabled(response: SmokeResponse, path: str) -> None:
    _check(response.status == 403, f"{path} returned {response.status}, expected disabled-write 403")
    body = _require_mapping(response.body, path)
    detail = str(body.get("detail", "")).lower()
    _check(
        "writes are disabled" in detail or "read-only" in detail,
        f"{path} 403 response did not explain read-only/write-disabled state: {body!r}",
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run read-only API smoke checks against a local gnucash-web-companion deployment.",
    )
    parser.add_argument(
        "--api-base-url",
        default=os.environ.get("SMOKE_API_BASE_URL", DEFAULT_API_BASE_URL),
        help=f"API base URL (default: $SMOKE_API_BASE_URL or {DEFAULT_API_BASE_URL})",
    )
    parser.add_argument(
        "--username",
        default=os.environ.get("SMOKE_ADMIN_USERNAME") or os.environ.get("APP_ADMIN_USERNAME") or "admin",
        help="Admin username (default: $SMOKE_ADMIN_USERNAME, $APP_ADMIN_USERNAME, or admin)",
    )
    parser.add_argument(
        "--password",
        default=os.environ.get("SMOKE_ADMIN_PASSWORD") or os.environ.get("APP_ADMIN_PASSWORD"),
        help="Admin password (default: $SMOKE_ADMIN_PASSWORD or $APP_ADMIN_PASSWORD; value is never printed)",
    )
    return parser.parse_args(argv)


def run(args: argparse.Namespace | None = None) -> None:
    args = args or parse_args([])
    base_url = args.api_base_url
    username = args.username
    password = args.password
    if not password:
        raise SmokeFailure(
            "Set SMOKE_ADMIN_PASSWORD or APP_ADMIN_PASSWORD for the local deployment admin user."
        )

    client = SmokeClient(base_url)
    print(f"read-only API smoke: target={base_url}")

    health = client.request("GET", "/health")
    health_body = _require_mapping(health.body, "/health")
    _check(health_body.get("status") == "ok", "/health did not return status=ok")
    print("ok: API health")

    _login(client, username, password)
    print("ok: login")

    me = client.request("GET", "/auth/me", authenticated=True)
    me_body = _require_mapping(me.body, "/auth/me")
    _check(me_body.get("username") == username, "/auth/me returned unexpected username")
    print("ok: /auth/me")

    default_book = _find_default_book(client)
    book_id = default_book["id"]
    print(f"ok: default book discovered via /books and verified at /books/{book_id}")

    accounts = client.request("GET", f"/books/{book_id}/accounts", authenticated=True)
    _require_list(accounts.body, f"/books/{book_id}/accounts")
    print("ok: accounts endpoint")

    transactions = client.request("GET", f"/books/{book_id}/transactions?limit=5&offset=0", authenticated=True)
    transactions_body = _require_mapping(transactions.body, f"/books/{book_id}/transactions")
    _check("items" in transactions_body, "transactions response is missing items")
    transaction_items = _require_list(transactions_body["items"], f"/books/{book_id}/transactions items")
    print("ok: transactions endpoint")

    if transaction_items:
        first_transaction = _require_mapping(transaction_items[0], "first transaction item")
        transaction_id = first_transaction.get("id")
        _check(isinstance(transaction_id, str) and bool(transaction_id), "first transaction item has no id")
        detail = client.request("GET", f"/books/{book_id}/transactions/{transaction_id}", authenticated=True)
        detail_body = _require_mapping(detail.body, f"/books/{book_id}/transactions/{transaction_id}")
        _check(detail_body.get("id") == transaction_id, "transaction detail returned unexpected id")
        _check(isinstance(detail_body.get("splits"), list), "transaction detail is missing splits")
        print("ok: transaction detail endpoint")
    else:
        print("skip: transaction detail endpoint (no transactions in default book)")

    export = client.request("GET", f"/books/{book_id}/transactions/export", authenticated=True)
    _check(isinstance(export.body, str), "CSV export did not return text content")
    _check(export.raw.startswith("id,date,description,amount,currency"), "CSV export header is unexpected")
    export_headers = {key.lower(): value for key, value in export.headers.items()}
    _check(export_headers.get("x-csv-export-limit") == "10000", "CSV export limit header is unexpected")
    print("ok: CSV export endpoint")

    summary = client.request("GET", f"/books/{book_id}/reports/summary", authenticated=True)
    _require_mapping(summary.body, f"/books/{book_id}/reports/summary")
    print("ok: reports summary")

    scheduled = client.request(
        "GET",
        f"/books/{book_id}/scheduled-transactions",
        authenticated=True,
    )
    scheduled_body = _require_list(scheduled.body, f"/books/{book_id}/scheduled-transactions")
    for index, item in enumerate(scheduled_body):
        scheduled_item = _require_mapping(item, f"/books/{book_id}/scheduled-transactions[{index}]")
        _check("id" in scheduled_item, "scheduled transaction item is missing id")
        unsafe_keys = {
            "template_transaction_description",
            "template_split_memo",
            "template_split_amount",
            "raw_sql",
        }
        _check(
            unsafe_keys.isdisjoint(scheduled_item.keys()),
            f"scheduled transaction item exposed unsafe template/source keys: {scheduled_item.keys()}",
        )
        _check(
            scheduled_item.get("new_transactions_created") == 0,
            "scheduled forecast violated the no-materialization invariant",
        )
        forecast = _require_mapping(
            scheduled_item.get("forecast"),
            f"/books/{book_id}/scheduled-transactions[{index}].forecast",
        )
        upcoming_7 = _require_list(
            forecast.get("upcoming_7_days"),
            f"/books/{book_id}/scheduled-transactions[{index}].forecast.upcoming_7_days",
        )
        upcoming_30 = _require_list(
            forecast.get("upcoming_30_days"),
            f"/books/{book_id}/scheduled-transactions[{index}].forecast.upcoming_30_days",
        )
        _check(len(upcoming_7) <= 7, "scheduled 7-day forecast is not bounded")
        _check(len(upcoming_30) <= 30, "scheduled 30-day forecast is not bounded")
        amount = _require_mapping(
            scheduled_item.get("amount"),
            f"/books/{book_id}/scheduled-transactions[{index}].amount",
        )
        if amount.get("status") != "resolved":
            _check(amount.get("amount") is None, "unresolved scheduled amount must not contain a fake value")
    print("ok: scheduled transactions endpoint")

    audit = client.request(
        "GET",
        f"/books/{book_id}/write-alpha-audit-summary",
        authenticated=True,
    )
    audit_body = _require_mapping(audit.body, f"/books/{book_id}/write-alpha-audit-summary")
    _check(isinstance(audit_body.get("items"), list), "audit summary response is missing items")
    _check(
        isinstance(audit_body.get("counts_by_action"), dict),
        "audit summary response is missing counts_by_action",
    )
    _check(
        isinstance(audit_body.get("counts_by_result"), dict),
        "audit summary response is missing counts_by_result",
    )
    _check(
        isinstance(audit_body.get("status_summary"), list),
        "audit summary response is missing status_summary",
    )
    _check(isinstance(audit_body.get("time_window"), dict), "audit summary response is missing time_window")
    print("ok: write-alpha audit summary endpoint")

    create_payload = {
        "date": "2026-05-18",
        "description": "Smoke disabled-write probe",
        "splits": [
            {"account_id": "smoke-account-a", "amount": "-1.00", "currency": "SEK", "memo": ""},
            {"account_id": "smoke-account-b", "amount": "1.00", "currency": "SEK", "memo": ""},
        ],
    }
    validate = client.request(
        "POST",
        f"/books/{book_id}/transactions/validate",
        payload=create_payload,
        expected_status=403,
        authenticated=True,
    )
    _assert_write_disabled(validate, f"/books/{book_id}/transactions/validate")
    print("ok: validate endpoint is write-disabled")

    create = client.request(
        "POST",
        f"/books/{book_id}/transactions",
        payload=create_payload,
        expected_status=403,
        authenticated=True,
    )
    _assert_write_disabled(create, f"/books/{book_id}/transactions")
    print("ok: create endpoint is write-disabled")

    patch = client.request(
        "PATCH",
        f"/books/{book_id}/transactions/smoke-nonexistent-transaction",
        payload={"description": "Smoke disabled-write probe"},
        expected_status=403,
        authenticated=True,
    )
    _assert_write_disabled(patch, f"/books/{book_id}/transactions/{{transaction_id}}")
    print("ok: patch endpoint is write-disabled")

    delete = client.request(
        "DELETE",
        f"/books/{book_id}/transactions/smoke-nonexistent-transaction",
        expected_status=403,
        authenticated=True,
    )
    _assert_write_disabled(delete, f"/books/{book_id}/transactions/{{transaction_id}}")
    print("ok: delete endpoint is write-disabled")

    print("PASS: read-only API smoke checks completed")


def main(argv: list[str] | None = None) -> int:
    try:
        run(parse_args(argv))
    except SmokeFailure as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
