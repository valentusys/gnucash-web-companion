"""Bounded account option service for filters and preview selectors."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import islice
import re
from types import SimpleNamespace
from typing import Any, cast
import unicodedata

import piecash

from app.schemas.accounts import (
    AccountOptionItemDTO,
    AccountOptionsPurpose,
    AccountOptionsResponseDTO,
    AccountOptionsScanDTO,
    CommodityRefDTO,
)
from app.services.account_explorer import AccountExplorerError
from app.services.account_visibility import (
    AccountVisibilityIndex,
    account_guid,
    build_account_visibility_index,
    visible_accounts as ordered_visible_accounts,
)

ACCOUNT_OPTIONS_DEFAULT_LIMIT = 50
ACCOUNT_OPTIONS_MAX_LIMIT = 200
ACCOUNT_OPTIONS_CANDIDATE_ROW_LIMIT = 10_000
ACCOUNT_OPTIONS_QUERY_LIMIT = 2
ACCOUNT_OPTIONS_SERIALIZED_BYTES_LIMIT = 128 * 1024
ACCOUNT_OPTIONS_QUERY_CODEPOINT_LIMIT = 120
ACCOUNT_OPTIONS_POSTING_TYPES = frozenset(
    {"ASSET", "BANK", "CASH", "CREDIT", "LIABILITY", "INCOME", "EXPENSE", "EQUITY"}
)
ACCOUNT_OPTIONS_PURPOSE_ALIASES = {
    "transactions_filter": "transactions_filter",
    "transaction_filter": "transactions_filter",
    "filters": "transactions_filter",
    "transaction_create_preview": "transaction_create_preview",
    "create_preview": "transaction_create_preview",
    "preview": "transaction_create_preview",
}
CURRENCY_RE = re.compile(r"^[A-Z0-9]{1,16}$")


class AccountOptionsError(AccountExplorerError):
    """Stable path-safe account option request/read error."""


@dataclass(frozen=True)
class AccountOptionsRequest:
    purpose: AccountOptionsPurpose
    query: str | None
    currency: str | None
    limit: int
    offset: int
    cursor: str | None


@dataclass(frozen=True)
class _AccountOptionRow:
    guid: str
    name: str
    account_type: str
    parent_guid: str | None
    hidden: bool
    placeholder: bool
    commodity_guid: str | None
    commodity_namespace: str | None
    commodity_mnemonic: str | None
    commodity_fraction: int | None


@dataclass(frozen=True)
class _LoadedOptionRows:
    rows: list[_AccountOptionRow]
    query_count: int
    candidate_limited: bool


def build_account_options_request(
    *,
    purpose: str | None,
    query: str | None,
    currency: str | None,
    limit: str | int | None,
    cursor: str | None,
) -> AccountOptionsRequest:
    """Parse account-options query params into a redacted bounded request."""

    parsed_purpose = _parse_purpose(purpose)
    parsed_query = _parse_query(query)
    parsed_currency = _parse_currency(currency)
    parsed_limit = _parse_limit(limit)
    parsed_offset = _parse_cursor(cursor)
    return AccountOptionsRequest(
        purpose=parsed_purpose,
        query=parsed_query,
        currency=parsed_currency,
        limit=parsed_limit,
        offset=parsed_offset,
        cursor=str(cursor).strip() if cursor is not None and str(cursor).strip() else None,
    )


def build_account_options_response(
    book: Any,
    request: AccountOptionsRequest,
    *,
    book_id: int,
    base_currency: str,
) -> AccountOptionsResponseDTO:
    """Return bounded selectable options without balance recursion or split scans."""

    normalized_base_currency = _normalized_currency(base_currency) or "XXX"
    loaded = _load_account_option_rows(book)
    visibility = build_account_visibility_index(SimpleNamespace(accounts=loaded.rows), accounts=loaded.rows)
    matched_items: list[AccountOptionItemDTO] = []
    for row in ordered_visible_accounts(visibility):
        if _row_hidden(row):
            continue
        if not _row_selectable(row, request=request, base_currency=normalized_base_currency):
            continue
        full_name = visibility.full_name(row)
        display_name = visibility.display_name(row)
        if request.query and not _matches_query(row, request.query, full_name=full_name, display_name=display_name):
            continue
        matched_items.append(_option_item(row, visibility=visibility, full_name=full_name, display_name=display_name))

    page_items = matched_items[request.offset : request.offset + request.limit]
    has_more = request.offset + len(page_items) < len(matched_items) or loaded.candidate_limited
    next_cursor = str(request.offset + len(page_items)) if has_more and page_items else None
    partial_failure = loaded.candidate_limited
    error_code = "candidate_row_limit_exceeded" if loaded.candidate_limited else None
    response = AccountOptionsResponseDTO(
        book_id=book_id,
        purpose=request.purpose,
        normalized_filters={
            "query": request.query,
            "currency": request.currency,
            "cursor": request.cursor,
        },
        items=page_items,
        limit=request.limit,
        returned_count=len(page_items),
        next_cursor=next_cursor,
        partial_failure=partial_failure,
        error_code=error_code,
        scan=AccountOptionsScanDTO(
            candidate_accounts=len(loaded.rows),
            matched_accounts=len(matched_items),
            returned_items=len(page_items),
            query_count=loaded.query_count,
            serialized_bytes=0,
            exhausted=not has_more,
            limits=_scan_limits(),
        ),
        limitations=[
            "Account options are ID-backed labels only; balances and transaction objects are not loaded.",
            "Hidden, structural-root, and canonical template-root accounts are excluded from selectable options.",
            "Transactions filter options are limited to configured reporting-currency accounts; no FX conversion is performed.",
            "Preview-create options include only visible non-placeholder posting accounts with CURRENCY commodities.",
        ],
    )
    _enforce_serialized_byte_limit(response, offset=request.offset, original_page_size=len(page_items))
    return response


def _parse_purpose(value: str | None) -> AccountOptionsPurpose:
    raw = str(value or "transactions_filter").strip().lower()
    purpose = ACCOUNT_OPTIONS_PURPOSE_ALIASES.get(raw)
    if purpose is None:
        raise AccountOptionsError(
            "invalid_purpose",
            "purpose must be transactions_filter or transaction_create_preview",
            field="purpose",
        )
    return cast(AccountOptionsPurpose, purpose)


def _parse_query(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = unicodedata.normalize("NFC", str(value)).strip()
    if not normalized:
        return None
    if len(normalized) > ACCOUNT_OPTIONS_QUERY_CODEPOINT_LIMIT:
        raise AccountOptionsError("query_too_long", "query is too long for account options", field="query")
    return normalized.casefold()


def _parse_currency(value: str | None) -> str | None:
    if value is None:
        return None
    normalized = _normalized_currency(value)
    if normalized is None:
        return None
    if not CURRENCY_RE.fullmatch(normalized):
        raise AccountOptionsError("invalid_currency", "currency must be an uppercase commodity mnemonic", field="currency")
    return normalized


def _parse_limit(value: str | int | None) -> int:
    if value is None or value == "":
        return ACCOUNT_OPTIONS_DEFAULT_LIMIT
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise AccountOptionsError("invalid_limit", "limit must be a positive integer", field="limit") from exc
    if parsed < 1 or parsed > ACCOUNT_OPTIONS_MAX_LIMIT:
        raise AccountOptionsError(
            "invalid_limit",
            f"limit must be between 1 and {ACCOUNT_OPTIONS_MAX_LIMIT}",
            field="limit",
        )
    return parsed


def _parse_cursor(value: str | None) -> int:
    if value is None or str(value).strip() == "":
        return 0
    text = str(value).strip()
    if not text.isdecimal():
        raise AccountOptionsError("invalid_cursor", "cursor is not a valid account-options cursor", field="cursor")
    parsed = int(text)
    if parsed < 0 or parsed > ACCOUNT_OPTIONS_CANDIDATE_ROW_LIMIT:
        raise AccountOptionsError("invalid_cursor", "cursor is outside the bounded account-options window", field="cursor")
    return parsed


def _load_account_option_rows(book: Any) -> _LoadedOptionRows:
    session = getattr(book, "session", None)
    query = getattr(session, "query", None) if session is not None else None
    if callable(query):
        rows = _load_sql_account_option_rows(session)
        candidate_limited = len(rows) > ACCOUNT_OPTIONS_CANDIDATE_ROW_LIMIT
        return _LoadedOptionRows(
            rows=rows[:ACCOUNT_OPTIONS_CANDIDATE_ROW_LIMIT],
            query_count=1,
            candidate_limited=candidate_limited,
        )

    accounts = list(islice(iter(getattr(book, "accounts", []) or []), ACCOUNT_OPTIONS_CANDIDATE_ROW_LIMIT + 1))
    candidate_limited = len(accounts) > ACCOUNT_OPTIONS_CANDIDATE_ROW_LIMIT
    rows = [_row_from_account(account) for account in accounts[:ACCOUNT_OPTIONS_CANDIDATE_ROW_LIMIT]]
    return _LoadedOptionRows(rows=rows, query_count=0, candidate_limited=candidate_limited)


def _load_sql_account_option_rows(session: Any) -> list[_AccountOptionRow]:
    account_table = piecash.Account.__table__
    commodity_table = piecash.Commodity.__table__
    rows = (
        session.query(
            account_table.c.guid.label("guid"),
            account_table.c.name.label("name"),
            account_table.c.account_type.label("account_type"),
            account_table.c.parent_guid.label("parent_guid"),
            account_table.c.hidden.label("hidden"),
            account_table.c.placeholder.label("placeholder"),
            account_table.c.commodity_guid.label("commodity_guid"),
            commodity_table.c.namespace.label("commodity_namespace"),
            commodity_table.c.mnemonic.label("commodity_mnemonic"),
            commodity_table.c.fraction.label("commodity_fraction"),
        )
        .select_from(account_table.outerjoin(commodity_table, account_table.c.commodity_guid == commodity_table.c.guid))
        .order_by(account_table.c.guid.asc())
        .limit(ACCOUNT_OPTIONS_CANDIDATE_ROW_LIMIT + 1)
        .all()
    )
    return [_row_from_sql(row) for row in rows]


def _row_from_sql(row: Any) -> _AccountOptionRow:
    return _AccountOptionRow(
        guid=_text(_row_value(row, "guid", 0)).lower(),
        name=_text(_row_value(row, "name", 1)),
        account_type=_text(_row_value(row, "account_type", 2)).upper(),
        parent_guid=_optional_text(_row_value(row, "parent_guid", 3), lower=True),
        hidden=bool(_row_value(row, "hidden", 4)),
        placeholder=bool(_row_value(row, "placeholder", 5)),
        commodity_guid=_optional_text(_row_value(row, "commodity_guid", 6), lower=True),
        commodity_namespace=_optional_text(_row_value(row, "commodity_namespace", 7), upper=True),
        commodity_mnemonic=_optional_text(_row_value(row, "commodity_mnemonic", 8), upper=True),
        commodity_fraction=_optional_int(_row_value(row, "commodity_fraction", 9)),
    )


def _row_from_account(account: Any) -> _AccountOptionRow:
    commodity = getattr(account, "commodity", None)
    parent_guid = getattr(account, "parent_guid", None)
    if parent_guid is None:
        parent = getattr(account, "parent", None)
        parent_guid = account_guid(parent) if parent is not None else None
    return _AccountOptionRow(
        guid=account_guid(account),
        name=_text(getattr(account, "name", "")),
        account_type=_text(getattr(account, "type", None) or getattr(account, "account_type", "")).upper(),
        parent_guid=_optional_text(parent_guid, lower=True),
        hidden=bool(getattr(account, "hidden", False)),
        placeholder=bool(getattr(account, "placeholder", False)),
        commodity_guid=_optional_text(getattr(commodity, "guid", None), lower=True),
        commodity_namespace=_optional_text(getattr(commodity, "namespace", None), upper=True),
        commodity_mnemonic=_optional_text(getattr(commodity, "mnemonic", None), upper=True),
        commodity_fraction=_optional_int(getattr(commodity, "fraction", None)),
    )


def _row_value(row: Any, label: str, index: int) -> Any:
    value = getattr(row, label, None)
    if value is not None:
        return value
    mapping = getattr(row, "_mapping", None)
    if mapping is not None and label in mapping:
        return mapping[label]
    return row[index]


def _row_hidden(row: Any) -> bool:
    return bool(getattr(row, "hidden", False))


def _row_selectable(row: Any, *, request: AccountOptionsRequest, base_currency: str) -> bool:
    namespace = _row_namespace(row)
    mnemonic = _row_mnemonic(row, base_currency=base_currency)
    account_type = _row_account_type(row)
    if request.purpose == "transaction_create_preview":
        if bool(getattr(row, "placeholder", False)):
            return False
        if account_type not in ACCOUNT_OPTIONS_POSTING_TYPES:
            return False
        if namespace != "CURRENCY" or not mnemonic or mnemonic == "XXX":
            return False
        if request.currency is not None and mnemonic != request.currency:
            return False
        return True

    if namespace != "CURRENCY":
        return False
    expected_currency = request.currency or base_currency
    return bool(mnemonic) and mnemonic == expected_currency


def _matches_query(row: Any, query: str, *, full_name: str, display_name: str) -> bool:
    haystack = "\n".join(
        (
            str(getattr(row, "guid", "") or ""),
            str(getattr(row, "name", "") or ""),
            display_name,
            full_name,
            _row_account_type(row),
            _row_mnemonic(row, base_currency=""),
        )
    ).casefold()
    return query in haystack


def _option_item(
    row: Any,
    *,
    visibility: AccountVisibilityIndex,
    full_name: str,
    display_name: str,
) -> AccountOptionItemDTO:
    currency = _row_mnemonic(row, base_currency="XXX") or "XXX"
    namespace = _row_namespace(row) or ""
    return AccountOptionItemDTO(
        id=account_guid(row),
        parent_id=visibility.effective_parent_id(row),
        name=_text(getattr(row, "name", "")),
        display_name=display_name,
        full_name=full_name,
        type=_row_account_type(row),
        commodity=CommodityRefDTO(namespace=namespace, mnemonic=currency),
        currency=currency,
        hidden=bool(getattr(row, "hidden", False)),
        placeholder=bool(getattr(row, "placeholder", False)),
        selectable=True,
    )


def _row_account_type(row: Any) -> str:
    return _text(getattr(row, "account_type", None) or getattr(row, "type", "")).upper()


def _row_namespace(row: Any) -> str:
    namespace = getattr(row, "commodity_namespace", None)
    if namespace is None:
        namespace = getattr(getattr(row, "commodity", None), "namespace", None)
    return _text(namespace).upper()


def _row_mnemonic(row: Any, *, base_currency: str) -> str:
    mnemonic = getattr(row, "commodity_mnemonic", None)
    if mnemonic is None:
        commodity = getattr(row, "commodity", None)
        mnemonic = getattr(commodity, "mnemonic", None)
    return _normalized_currency(mnemonic) or _normalized_currency(base_currency) or ""


def _normalized_currency(value: Any) -> str | None:
    text = unicodedata.normalize("NFC", str(value or "")).strip().upper()
    return text or None


def _text(value: Any) -> str:
    return unicodedata.normalize("NFC", str(value or ""))


def _optional_text(value: Any, *, lower: bool = False, upper: bool = False) -> str | None:
    text = _text(value).strip()
    if not text:
        return None
    if lower:
        return text.lower()
    if upper:
        return text.upper()
    return text


def _optional_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _scan_limits() -> dict[str, int]:
    return {
        "candidate_accounts": ACCOUNT_OPTIONS_CANDIDATE_ROW_LIMIT,
        "returned_items": ACCOUNT_OPTIONS_MAX_LIMIT,
        "query_count": ACCOUNT_OPTIONS_QUERY_LIMIT,
        "serialized_bytes": ACCOUNT_OPTIONS_SERIALIZED_BYTES_LIMIT,
        "query_codepoints": ACCOUNT_OPTIONS_QUERY_CODEPOINT_LIMIT,
    }


def _enforce_serialized_byte_limit(
    response: AccountOptionsResponseDTO,
    *,
    offset: int,
    original_page_size: int,
) -> None:
    size = _serialized_response_bytes(response)
    if size <= ACCOUNT_OPTIONS_SERIALIZED_BYTES_LIMIT:
        response.scan.serialized_bytes = size
        return

    response.partial_failure = True
    if response.error_code is None:
        response.error_code = "response_bytes_limited"
    while response.items and size > ACCOUNT_OPTIONS_SERIALIZED_BYTES_LIMIT:
        response.items.pop()
        response.returned_count = len(response.items)
        response.scan.returned_items = len(response.items)
        response.next_cursor = str(offset + len(response.items))
        response.scan.exhausted = False
        size = _serialized_response_bytes(response)
    response.scan.serialized_bytes = size
    if not response.items and original_page_size > 0 and size > ACCOUNT_OPTIONS_SERIALIZED_BYTES_LIMIT:
        raise AccountOptionsError(
            "response_too_large",
            "account options response is too large for one bounded request",
            field="limit",
        )


def _serialized_response_bytes(response: AccountOptionsResponseDTO) -> int:
    try:
        return len(response.model_dump_json().encode("utf-8"))
    except Exception as exc:  # pragma: no cover - pydantic serialization should stay deterministic
        raise AccountOptionsError(
            "response_too_large",
            "account options response size could not be measured safely",
        ) from exc
