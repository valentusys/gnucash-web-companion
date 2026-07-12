"""Validation, errors, and cursors for the bounded transaction explorer."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import re
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal, InvalidOperation
from typing import Any, Literal

EXPLORER_CONTRACT_VERSION = 1
CURSOR_TTL = timedelta(hours=24)
MAX_CURSOR_LENGTH = 1024
MAX_EXPLORER_DATE_DAYS = 366
MAX_EXPLORER_PAGE_SIZE = 100
DEFAULT_EXPLORER_PAGE_SIZE = 50
MAX_ACCOUNT_IDS = 20
MAX_QUERY_CODEPOINTS = 120
ACCOUNT_ID_RE = re.compile(r"^[0-9a-f]{32}$")
DECIMAL_RE = re.compile(r"^(0|[1-9][0-9]{0,17})(\.[0-9]{1,8})?$")
ISO_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")

ExplorerSort = Literal["date_desc", "date_asc"]
ExplorerCursorMode = Literal["next", "previous"]
ExplorerDirection = Literal["increase", "decrease"]
ExplorerType = Literal["income", "expense"]


class TransactionExplorerError(ValueError):
    """Stable path-safe explorer error."""

    def __init__(self, code: str, message: str, *, field: str | None = None, status_code: int = 422):
        super().__init__(message)
        self.code = code
        self.message = message
        self.field = field or ""
        self.status_code = status_code

    def detail(self) -> dict[str, str]:
        return {"code": self.code, "field": self.field, "message": self.message}


@dataclass(frozen=True)
class TransactionExplorerCursor:
    mode: ExplorerCursorMode
    date: date
    guid: str


@dataclass(frozen=True)
class TransactionExplorerQuery:
    date_from: date
    date_to: date
    account_ids: tuple[str, ...]
    direction: ExplorerDirection | None
    transaction_type: ExplorerType | None
    min_amount: Decimal | None
    max_amount: Decimal | None
    raw_min_amount: str | None
    raw_max_amount: str | None
    query: str | None
    transaction_state: str | None
    sort: ExplorerSort
    page_size: int
    cursor: TransactionExplorerCursor | None
    filter_hash: str
    cursor_secret: str
    normalized_filters: dict[str, Any]


def _json_b64(payload: dict[str, Any]) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _b64_json(value: str) -> dict[str, Any]:
    padding = "=" * (-len(value) % 4)
    raw = base64.urlsafe_b64decode((value + padding).encode("ascii"))
    decoded = json.loads(raw.decode("utf-8"))
    if not isinstance(decoded, dict):
        raise ValueError("cursor payload must be an object")
    return decoded


def _sign_cursor_payload(payload_part: str, secret: str) -> str:
    return base64.urlsafe_b64encode(
        hmac.new(secret.encode("utf-8"), payload_part.encode("ascii"), hashlib.sha256).digest()
    ).decode("ascii").rstrip("=")


def parse_explorer_date(value: str | None, field: str) -> date:
    if value is None or not ISO_DATE_RE.match(value):
        raise TransactionExplorerError("invalid_date", f"{field} must be an ISO date in YYYY-MM-DD format")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise TransactionExplorerError("invalid_date", f"{field} must be an ISO date in YYYY-MM-DD format") from exc
    if parsed.isoformat() != value:
        raise TransactionExplorerError("invalid_date", f"{field} must be an ISO date in YYYY-MM-DD format")
    return parsed


def parse_explorer_date_range(date_from: str | None, date_to: str | None) -> tuple[date, date]:
    if date_from is None or date_to is None:
        raise TransactionExplorerError("date_pair_required", "date_from and date_to are required together", field="date_from")
    start = parse_explorer_date(date_from, "date_from")
    end = parse_explorer_date(date_to, "date_to")
    if start > end:
        raise TransactionExplorerError("invalid_date_range", "date_from must be on or before date_to")
    if (end - start).days > MAX_EXPLORER_DATE_DAYS - 1:
        raise TransactionExplorerError("date_range_too_wide", "date range must be at most 366 inclusive days", field="date_to")
    return start, end


def parse_explorer_account_ids(values: list[str] | None, *, legacy_account_id_present: bool) -> tuple[str, ...]:
    if legacy_account_id_present:
        raise TransactionExplorerError("invalid_account_id", "Use repeated account_ids; account_id is not supported by explorer", field="account_id")
    if not values:
        return ()
    if len(values) > MAX_ACCOUNT_IDS:
        raise TransactionExplorerError("too_many_accounts", "account_ids accepts at most 20 values", field="account_ids")
    normalized: list[str] = []
    for value in values:
        lowered = str(value).strip().lower()
        if not ACCOUNT_ID_RE.match(lowered):
            raise TransactionExplorerError("invalid_account_id", "account_ids must be 32-character lowercase hexadecimal GUIDs")
        normalized.append(lowered)
    if len(set(normalized)) != len(normalized):
        raise TransactionExplorerError("duplicate_account_id", "account_ids must be unique after normalization")
    return tuple(normalized)


def parse_explorer_decimal(value: str | None, field: str) -> tuple[Decimal | None, str | None]:
    if value is None:
        return None, None
    text = str(value)
    if not DECIMAL_RE.match(text):
        raise TransactionExplorerError(
            "invalid_amount",
            f"{field} must be a canonical non-negative decimal string with up to 18 integer and 8 fractional digits",
        )
    try:
        parsed = Decimal(text)
    except InvalidOperation as exc:
        raise TransactionExplorerError("invalid_amount", f"{field} must be a valid decimal string") from exc
    if not parsed.is_finite() or parsed < 0:
        raise TransactionExplorerError("invalid_amount", f"{field} must be a non-negative finite decimal string")
    return parsed, text


def parse_explorer_query_text(value: str | None) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text:
        raise TransactionExplorerError("invalid_query", "query must be 1 to 120 Unicode code points after trimming")
    if len(text) > MAX_QUERY_CODEPOINTS:
        raise TransactionExplorerError("invalid_query", "query must be 1 to 120 Unicode code points after trimming")
    return text


def parse_explorer_sort(value: str | None) -> ExplorerSort:
    if value in (None, "", "date_desc"):
        return "date_desc"
    if value == "date_asc":
        return "date_asc"
    raise TransactionExplorerError("invalid_sort", "sort must be date_desc or date_asc")


def parse_explorer_page_size(value: int | str | None) -> int:
    if value in (None, ""):
        return DEFAULT_EXPLORER_PAGE_SIZE
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise TransactionExplorerError("invalid_page_size", "page_size must be an integer from 1 to 100") from exc
    if parsed < 1 or parsed > MAX_EXPLORER_PAGE_SIZE:
        raise TransactionExplorerError("invalid_page_size", "page_size must be an integer from 1 to 100")
    return parsed


def parse_explorer_direction(value: str | None) -> ExplorerDirection | None:
    if value in (None, ""):
        return None
    if value in {"increase", "decrease"}:
        return value  # type: ignore[return-value]
    raise TransactionExplorerError("invalid_direction", "direction must be increase or decrease")


def parse_explorer_type(value: str | None) -> ExplorerType | None:
    if value in (None, ""):
        return None
    if value in {"income", "expense"}:
        return value  # type: ignore[return-value]
    raise TransactionExplorerError("invalid_type", "type must be income or expense")


def validate_explorer_filter_modes(
    *,
    account_ids: tuple[str, ...],
    direction: ExplorerDirection | None,
    transaction_type: ExplorerType | None,
    min_amount: Decimal | None,
    max_amount: Decimal | None,
) -> None:
    if direction is not None and not account_ids:
        raise TransactionExplorerError("account_scope_required", "direction requires at least one account_ids value", field="direction")
    if transaction_type is not None and (account_ids or direction is not None):
        raise TransactionExplorerError("incompatible_filter_mode", "type is incompatible with account_ids and direction")
    if (min_amount is not None or max_amount is not None) and not (account_ids or transaction_type is not None):
        raise TransactionExplorerError("account_scope_required", "min_amount and max_amount require account_ids or type", field="min_amount")
    if min_amount is not None and max_amount is not None and min_amount > max_amount:
        raise TransactionExplorerError("invalid_amount", "min_amount must be less than or equal to max_amount", field="min_amount")


def explorer_filter_hash(
    *,
    date_from: date,
    date_to: date,
    account_ids: tuple[str, ...],
    direction: ExplorerDirection | None,
    transaction_type: ExplorerType | None,
    raw_min_amount: str | None,
    raw_max_amount: str | None,
    query: str | None,
    transaction_state: str | None,
    sort: ExplorerSort,
    page_size: int,
    secret: str,
) -> str:
    payload = {
        "date_from": date_from.isoformat(),
        "date_to": date_to.isoformat(),
        "account_ids": list(account_ids),
        "direction": direction,
        "type": transaction_type,
        "min_amount": raw_min_amount,
        "max_amount": raw_max_amount,
        "query_casefold_sha256": hashlib.sha256((query or "").casefold().encode("utf-8")).hexdigest(),
        "transaction_state": transaction_state,
        "sort": sort,
        "page_size": page_size,
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hmac.new(secret.encode("utf-8"), raw, hashlib.sha256).hexdigest()


def encode_explorer_cursor(
    *,
    mode: ExplorerCursorMode,
    cursor_date: date,
    cursor_guid: str,
    filter_hash: str,
    sort: ExplorerSort,
    secret: str,
    now: datetime | None = None,
) -> str:
    expires = int(((now or datetime.now(timezone.utc)) + CURSOR_TTL).timestamp())
    payload = {
        "v": EXPLORER_CONTRACT_VERSION,
        "exp": expires,
        "mode": mode,
        "date": cursor_date.isoformat(),
        "guid": cursor_guid,
        "fh": filter_hash,
        "sort": sort,
    }
    payload_part = _json_b64(payload)
    signature = _sign_cursor_payload(payload_part, secret)
    token = f"{payload_part}.{signature}"
    if len(token) > MAX_CURSOR_LENGTH:  # pragma: no cover - defensive guard
        raise TransactionExplorerError("cursor_too_large", "cursor could not be created within the explorer size bound")
    return token


def decode_explorer_cursor(
    value: str | None,
    *,
    expected_filter_hash: str,
    expected_sort: ExplorerSort,
    secret: str,
    now: datetime | None = None,
) -> TransactionExplorerCursor | None:
    if value is None or value == "":
        return None
    if len(value) > MAX_CURSOR_LENGTH:
        raise TransactionExplorerError("invalid_cursor", "cursor is invalid or too large")
    try:
        payload_part, signature = value.split(".", 1)
        expected_signature = _sign_cursor_payload(payload_part, secret)
        if not hmac.compare_digest(signature, expected_signature):
            raise ValueError("bad cursor signature")
        payload = _b64_json(payload_part)
        if payload.get("v") != EXPLORER_CONTRACT_VERSION:
            raise ValueError("unsupported cursor version")
        if payload.get("fh") != expected_filter_hash or payload.get("sort") != expected_sort:
            raise TransactionExplorerError("cursor_filter_mismatch", "cursor does not match the current explorer filters")
        expires = int(payload["exp"])
        if expires < int((now or datetime.now(timezone.utc)).timestamp()):
            raise TransactionExplorerError("cursor_expired", "cursor has expired", field="cursor")
        mode = payload.get("mode")
        if mode not in {"next", "previous"}:
            raise ValueError("bad cursor mode")
        cursor_date = parse_explorer_date(str(payload.get("date")), "cursor.date")
        guid = str(payload.get("guid") or "")
        if not guid:
            raise ValueError("bad cursor guid")
        return TransactionExplorerCursor(mode=mode, date=cursor_date, guid=guid)  # type: ignore[arg-type]
    except TransactionExplorerError:
        raise
    except Exception as exc:
        raise TransactionExplorerError("invalid_cursor", "cursor is invalid") from exc


def build_transaction_explorer_query(
    *,
    date_from: str | None,
    date_to: str | None,
    account_ids: list[str] | None,
    legacy_account_id_present: bool,
    direction: str | None,
    transaction_type: str | None,
    min_amount: str | None,
    max_amount: str | None,
    query: str | None,
    transaction_state: str | None,
    sort: str | None,
    page_size: int | str | None,
    cursor: str | None,
    secret: str,
) -> TransactionExplorerQuery:
    parsed_from, parsed_to = parse_explorer_date_range(date_from, date_to)
    parsed_accounts = parse_explorer_account_ids(account_ids, legacy_account_id_present=legacy_account_id_present)
    parsed_direction = parse_explorer_direction(direction)
    parsed_type = parse_explorer_type(transaction_type)
    parsed_min, raw_min = parse_explorer_decimal(min_amount, "min_amount")
    parsed_max, raw_max = parse_explorer_decimal(max_amount, "max_amount")
    normalized_query = parse_explorer_query_text(query)
    if transaction_state in (None, ""):
        normalized_state = None
    elif transaction_state in {"unreconciled", "cleared", "reconciled", "voided"}:
        normalized_state = transaction_state
    else:
        raise TransactionExplorerError("invalid_state", "transaction_state is not supported", field="transaction_state")
    parsed_sort = parse_explorer_sort(sort)
    parsed_page_size = parse_explorer_page_size(page_size)
    validate_explorer_filter_modes(
        account_ids=parsed_accounts,
        direction=parsed_direction,
        transaction_type=parsed_type,
        min_amount=parsed_min,
        max_amount=parsed_max,
    )
    filter_hash = explorer_filter_hash(
        date_from=parsed_from,
        date_to=parsed_to,
        account_ids=parsed_accounts,
        direction=parsed_direction,
        transaction_type=parsed_type,
        raw_min_amount=raw_min,
        raw_max_amount=raw_max,
        query=normalized_query,
        transaction_state=normalized_state,
        sort=parsed_sort,
        page_size=parsed_page_size,
        secret=secret,
    )
    parsed_cursor = decode_explorer_cursor(
        cursor,
        expected_filter_hash=filter_hash,
        expected_sort=parsed_sort,
        secret=secret,
    )
    normalized_filters = {
        "date_from": parsed_from.isoformat(),
        "date_to": parsed_to.isoformat(),
        "account_ids": list(parsed_accounts),
        "direction": parsed_direction,
        "type": parsed_type,
        "min_amount": raw_min,
        "max_amount": raw_max,
        "query": normalized_query,
        "transaction_state": normalized_state,
        "sort": parsed_sort,
        "page_size": parsed_page_size,
    }
    return TransactionExplorerQuery(
        date_from=parsed_from,
        date_to=parsed_to,
        account_ids=parsed_accounts,
        direction=parsed_direction,
        transaction_type=parsed_type,
        min_amount=parsed_min,
        max_amount=parsed_max,
        raw_min_amount=raw_min,
        raw_max_amount=raw_max,
        query=normalized_query,
        transaction_state=normalized_state,
        sort=parsed_sort,
        page_size=parsed_page_size,
        cursor=parsed_cursor,
        filter_hash=filter_hash,
        cursor_secret=secret,
        normalized_filters=normalized_filters,
    )
