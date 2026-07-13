"""Validation and bounded service helpers for account hierarchy explorer."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from fractions import Fraction
import re
import unicodedata
from typing import Any, Literal

import piecash
from sqlalchemy import func
from sqlalchemy.orm import joinedload

from app.schemas.accounts import (
    AccountExplorerBalanceDTO,
    AccountExplorerMode,
    AccountExplorerNodeDTO,
    AccountExplorerPathSegmentDTO,
    AccountExplorerResponseDTO,
    AccountExplorerScanDTO,
)

MAX_QUERY_CODEPOINTS = 120
MAX_TYPE_FILTERS = 20
MAX_CANDIDATE_ACCOUNTS = 10_000
MAX_RETURNED_NODES = 1_000
MAX_DEPTH = 64
MAX_COMMODITY_BUCKETS = 20
MAX_ROLLUP_CELLS = 50_000
MAX_SERIALIZED_RESPONSE_BYTES = 512 * 1024
MAX_DATA_QUERIES = 8

ACCOUNT_TYPE_RE = re.compile(r"^[A-Z][A-Z0-9_]{0,31}$")
GUID_RE = re.compile(r"^[0-9a-f]{32}$")
CREDIT_NATURAL_SIGN_TYPES = {"LIABILITY", "CREDIT", "PAYABLE", "EQUITY", "INCOME"}

VisibilityMode = Literal["exclude", "include", "only"]
StructureStatus = Literal["ok", "orphan_promoted", "cycle_broken_root", "cycle_member"]
CommodityKey = tuple[str, str]


class AccountExplorerError(ValueError):
    """Stable path-safe account explorer error."""

    def __init__(self, code: str, message: str, *, field: str | None = None, status_code: int = 422):
        super().__init__(message)
        self.code = code
        self.message = message
        self.field = field or ""
        self.status_code = status_code

    def detail(self) -> dict[str, str]:
        return {"code": self.code, "field": self.field, "message": self.message}


@dataclass(frozen=True)
class AccountExplorerQuery:
    mode: AccountExplorerMode
    query: str | None
    types: tuple[str, ...]
    hidden: VisibilityMode
    placeholder: VisibilityMode
    normalized_filters: dict[str, Any]


@dataclass
class _AccountRecord:
    id: str
    source_parent_id: str | None
    parent_id: str | None
    root_id: str | None
    name: str
    type: str
    commodity_namespace: str
    commodity_mnemonic: str
    hidden: bool
    placeholder: bool
    direct_raw: Decimal = Decimal("0")
    direct_split_count: int = 0

    @property
    def commodity_key(self) -> CommodityKey:
        return self.commodity_namespace, self.commodity_mnemonic


@dataclass(frozen=True)
class _SplitAggregateStats:
    split_rows: int
    aggregate_rows: int
    query_count: int


def build_account_explorer_query(
    *,
    mode: str | None,
    query: str | None,
    types: list[str] | None,
    hidden: str | None,
    placeholder: str | None,
) -> AccountExplorerQuery:
    parsed_mode = _parse_mode(mode)
    parsed_query = _parse_query(query)
    parsed_types = _parse_types(types)
    parsed_hidden = _parse_visibility(hidden, default="exclude", field="hidden")
    parsed_placeholder = _parse_visibility(placeholder, default="include", field="placeholder")
    normalized_filters = {
        "query": parsed_query,
        "types": list(parsed_types),
        "hidden": parsed_hidden,
        "placeholder": parsed_placeholder,
    }
    return AccountExplorerQuery(
        mode=parsed_mode,
        query=parsed_query,
        types=parsed_types,
        hidden=parsed_hidden,
        placeholder=parsed_placeholder,
        normalized_filters=normalized_filters,
    )


def build_account_explorer_response(
    book: Any,
    request: AccountExplorerQuery,
    *,
    book_id: int,
    base_currency: str,
) -> AccountExplorerResponseDTO:
    records, query_count, split_stats = _load_account_records(book, base_currency=base_currency)
    if query_count > MAX_DATA_QUERIES:
        raise AccountExplorerError(
            "result_too_complex",
            "Account hierarchy requires too many data reads for one bounded request; narrow the filters.",
        )
    if len(records) > MAX_CANDIDATE_ACCOUNTS:
        raise AccountExplorerError(
            "result_too_large",
            "Account hierarchy is too large for one bounded request; narrow the filters.",
        )

    records_by_id = _records_by_id(records)
    parent_by_id, structure_status = _effective_parent_map(records_by_id)
    children_by_parent = _children_by_parent(records_by_id, parent_by_id)
    preorder, depth_by_id, path_by_id, root_by_id = _preorder(records_by_id, children_by_parent)
    for account_id, root_id in root_by_id.items():
        records_by_id[account_id].root_id = root_id
        records_by_id[account_id].parent_id = parent_by_id[account_id]

    full_path_by_id = {
        account_id: ":".join(segment.name for segment in path_by_id[account_id])
        for account_id in records_by_id
    }
    self_matches = {
        account_id
        for account_id in preorder
        if _record_matches(records_by_id[account_id], full_path_by_id[account_id], request)
    }
    returned_ids = _returned_ids(request.mode, preorder, self_matches, parent_by_id)
    if len(returned_ids) > MAX_RETURNED_NODES:
        raise AccountExplorerError(
            "result_too_large",
            "Account hierarchy result is too large for one bounded request; narrow the filters.",
        )

    raw_recursive_buckets, rollup_cells = _recursive_buckets(records_by_id, children_by_parent, preorder)
    if rollup_cells > MAX_ROLLUP_CELLS:
        raise AccountExplorerError(
            "result_too_complex",
            "Account hierarchy balance rollups are too complex for one bounded request; narrow the filters.",
        )
    for account_id in returned_ids:
        if len(raw_recursive_buckets[account_id]) > MAX_COMMODITY_BUCKETS:
            raise AccountExplorerError(
                "too_many_commodities",
                "Account subtree has too many native commodities for one bounded request; narrow the filters.",
            )

    nodes = [
        _node_dto(
            records_by_id[account_id],
            path_by_id=path_by_id,
            full_path_by_id=full_path_by_id,
            depth_by_id=depth_by_id,
            children_by_parent=children_by_parent,
            raw_recursive_buckets=raw_recursive_buckets,
            match_state="self" if account_id in self_matches else "ancestor_context",
            structure_status=structure_status[account_id],
        )
        for account_id in returned_ids
    ]
    returned_root_ids = [
        root_id
        for root_id in _sorted_roots(records_by_id, children_by_parent)
        if any(root_by_id[account_id] == root_id for account_id in returned_ids)
    ]
    scan = AccountExplorerScanDTO(
        candidate_accounts=len(records),
        returned_nodes=len(nodes),
        split_rows=split_stats.split_rows,
        split_aggregate_rows=split_stats.aggregate_rows,
        query_count=query_count,
        rollup_cells=rollup_cells,
        serialized_bytes=0,
        exhausted=True,
        limits=_limits(),
    )
    response = AccountExplorerResponseDTO(
        book_id=book_id,
        mode=request.mode,
        normalized_filters=request.normalized_filters,
        root_ids=returned_root_ids,
        nodes=nodes,
        returned_count=len(nodes),
        scan=scan,
        balance_basis="native_commodity_account_natural_sign",
        includes_currency_conversion=False,
        limitations=[
            "Balances are exact Decimal strings in each account's native commodity and include no currency conversion.",
            "Recursive balances are native commodity buckets; commodities are never summed or converted across currencies.",
            "No transaction objects are materialized by this account hierarchy response.",
        ],
    )
    response.scan.serialized_bytes = _serialized_response_bytes(response)
    if response.scan.serialized_bytes > MAX_SERIALIZED_RESPONSE_BYTES:
        raise AccountExplorerError(
            "result_too_large",
            "Account hierarchy response is too large for one bounded request; narrow the filters.",
        )
    return response


def _parse_mode(value: str | None) -> AccountExplorerMode:
    text = (value or "tree").strip().lower()
    if text in {"tree", "flat"}:
        return text  # type: ignore[return-value]
    raise AccountExplorerError("invalid_mode", "mode must be tree or flat", field="mode")


def _parse_query(value: str | None) -> str | None:
    if value is None:
        return None
    text = unicodedata.normalize("NFC", str(value).strip())
    if not text:
        return None
    if len(text) > MAX_QUERY_CODEPOINTS:
        raise AccountExplorerError("invalid_query", "query must be at most 120 Unicode code points after trimming", field="query")
    return text


def _parse_types(values: list[str] | None) -> tuple[str, ...]:
    if not values:
        return ()
    normalized: list[str] = []
    for value in values:
        text = unicodedata.normalize("NFC", str(value).strip()).upper()
        if not ACCOUNT_TYPE_RE.match(text):
            raise AccountExplorerError("invalid_type", "type filters must match [A-Z][A-Z0-9_]{0,31}", field="type")
        normalized.append(text)
    if len(set(normalized)) != len(normalized):
        raise AccountExplorerError("duplicate_type", "type filters must be unique after normalization", field="type")
    if len(normalized) > MAX_TYPE_FILTERS:
        raise AccountExplorerError("too_many_types", "type accepts at most 20 unique values", field="type")
    return tuple(sorted(normalized))


def _parse_visibility(value: str | None, *, default: VisibilityMode, field: str) -> VisibilityMode:
    text = (value or default).strip().lower()
    if text in {"exclude", "include", "only"}:
        return text  # type: ignore[return-value]
    raise AccountExplorerError(f"invalid_{field}", f"{field} must be exclude, include, or only", field=field)


def _load_account_records(book: Any, *, base_currency: str) -> tuple[list[_AccountRecord], int, _SplitAggregateStats]:
    session = getattr(book, "session", None)
    query = getattr(session, "query", None) if session is not None else None
    if callable(query):
        accounts = list(
            query(piecash.Account)
            .options(joinedload(piecash.Account.commodity), joinedload(piecash.Account.parent))
            .limit(MAX_CANDIDATE_ACCOUNTS + 1)
            .all()
        )
        records = [_account_record(account, base_currency=base_currency) for account in accounts]
        records_by_id = _records_by_id(records, allow_over_limit=True)
        if len(records) > MAX_CANDIDATE_ACCOUNTS:
            return records, 1, _SplitAggregateStats(split_rows=0, aggregate_rows=0, query_count=0)
        split_stats = _load_sql_split_totals(session, records_by_id)
        return records, 1 + split_stats.query_count, split_stats

    accounts = list(getattr(book, "accounts", []) or [])
    records = [_account_record(account, base_currency=base_currency) for account in accounts]
    records_by_id = _records_by_id(records, allow_over_limit=True)
    if len(records) > MAX_CANDIDATE_ACCOUNTS:
        return records, 0, _SplitAggregateStats(split_rows=0, aggregate_rows=0, query_count=0)
    split_stats = _load_fallback_split_totals(accounts, records_by_id)
    return records, 0, split_stats


def _load_sql_split_totals(session: Any, records_by_id: dict[str, _AccountRecord]) -> _SplitAggregateStats:
    if not records_by_id:
        return _SplitAggregateStats(split_rows=0, aggregate_rows=0, query_count=0)
    _register_sqlite_rational_sum(session)
    split_table = piecash.Split.__table__
    account_guid = split_table.c.account_guid
    quantity_num = split_table.c.quantity_num
    quantity_denom = split_table.c.quantity_denom
    rows = (
        session.query(
            account_guid.label("account_guid"),
            func.gwc_rational_sum(quantity_num, quantity_denom).label("quantity_rational"),
            func.count().label("split_count"),
        )
        .select_from(split_table)
        .filter(account_guid.in_(tuple(records_by_id)))
        .group_by(account_guid)
        .all()
    )
    split_rows = 0
    aggregate_rows = 0
    for row in rows:
        aggregate_rows += 1
        account_id = _optional_guid(_row_value(row, "account_guid", 0))
        if account_id is None or account_id not in records_by_id:
            continue
        record = records_by_id[account_id]
        split_count = _non_negative_int(_row_value(row, "split_count", 2))
        record.direct_raw += _decimal_from_rational_text(_row_value(row, "quantity_rational", 1))
        record.direct_split_count += split_count
        split_rows += split_count
    if aggregate_rows > len(records_by_id):  # pragma: no cover - SQL GROUP BY defensive guard
        raise AccountExplorerError("result_too_complex", "Account hierarchy split aggregation returned too many groups.")
    return _SplitAggregateStats(split_rows=split_rows, aggregate_rows=aggregate_rows, query_count=1)


def _load_fallback_split_totals(accounts: list[Any], records_by_id: dict[str, _AccountRecord]) -> _SplitAggregateStats:
    scanned = 0
    aggregate_rows = 0
    for account in accounts:
        account_id = _guid(getattr(account, "guid", account))
        record = records_by_id.get(account_id)
        if record is None:
            continue
        account_split_count = 0
        for split in getattr(account, "splits", []) or []:
            scanned += 1
            account_split_count += 1
            record.direct_raw += _split_quantity(split)
            record.direct_split_count += 1
        if account_split_count:
            aggregate_rows += 1
    return _SplitAggregateStats(split_rows=scanned, aggregate_rows=aggregate_rows, query_count=0)


class _SQLiteRationalSum:
    def __init__(self) -> None:
        self.total = Fraction(0, 1)
        self.invalid = False

    def step(self, numerator: Any, denominator: Any) -> None:
        try:
            if numerator is None or denominator is None:
                self.invalid = True
                return
            denominator_int = int(denominator)
            if denominator_int == 0:
                self.invalid = True
                return
            self.total += Fraction(int(numerator), denominator_int)
        except (ArithmeticError, TypeError, ValueError, OverflowError):
            self.invalid = True

    def finalize(self) -> str:
        if self.invalid:
            return "invalid"
        return f"{self.total.numerator}/{self.total.denominator}"


def _register_sqlite_rational_sum(session: Any) -> None:
    bind = None
    get_bind = getattr(session, "get_bind", None)
    if callable(get_bind):
        bind = get_bind()
    dialect = getattr(bind, "dialect", None)
    if getattr(dialect, "name", None) != "sqlite":
        raise AccountExplorerError(
            "result_too_complex",
            "Account hierarchy split aggregation requires SQLite Decimal aggregation support in this runtime.",
        )
    connection = session.connection()
    raw_connection = getattr(connection, "connection", connection)
    raw_connection = getattr(raw_connection, "driver_connection", raw_connection)
    raw_connection = getattr(raw_connection, "connection", raw_connection)
    create_aggregate = getattr(raw_connection, "create_aggregate", None)
    if not callable(create_aggregate):
        raise AccountExplorerError(
            "result_too_complex",
            "Account hierarchy split aggregation could not install the bounded Decimal aggregate.",
        )
    create_aggregate("gwc_rational_sum", 2, _SQLiteRationalSum)


def _row_value(row: Any, label: str, index: int) -> Any:
    value = getattr(row, label, None)
    if value is not None:
        return value
    mapping = getattr(row, "_mapping", None)
    if mapping is not None and label in mapping:
        return mapping[label]
    return row[index]


def _non_negative_int(value: Any) -> int:
    try:
        parsed = int(value)
    except (TypeError, ValueError) as exc:
        raise AccountExplorerError("result_too_complex", "Account hierarchy split aggregation returned invalid counters.") from exc
    if parsed < 0:
        raise AccountExplorerError("result_too_complex", "Account hierarchy split aggregation returned invalid counters.")
    return parsed


def _account_record(account: Any, *, base_currency: str) -> _AccountRecord:
    account_id = _guid(getattr(account, "guid", account))
    parent_id = _parent_id(account)
    commodity = getattr(account, "commodity", None)
    namespace = str(getattr(commodity, "namespace", None) or getattr(account, "commodity_namespace", None) or "CURRENCY")
    mnemonic = str(getattr(commodity, "mnemonic", None) or getattr(account, "commodity_mnemonic", None) or base_currency or "XXX")
    return _AccountRecord(
        id=account_id,
        source_parent_id=parent_id,
        parent_id=None,
        root_id=None,
        name=unicodedata.normalize("NFC", str(getattr(account, "name", "") or "")),
        type=unicodedata.normalize("NFC", str(getattr(account, "type", "") or "")).upper(),
        commodity_namespace=unicodedata.normalize("NFC", namespace),
        commodity_mnemonic=unicodedata.normalize("NFC", mnemonic),
        hidden=bool(getattr(account, "hidden", False)),
        placeholder=bool(getattr(account, "placeholder", False)),
    )


def _parent_id(account: Any) -> str | None:
    parent_guid = getattr(account, "parent_guid", None)
    if parent_guid:
        return _guid(parent_guid)
    parent = getattr(account, "parent", None)
    if parent is None:
        return None
    return _guid(getattr(parent, "guid", parent))


def _records_by_id(records: list[_AccountRecord], *, allow_over_limit: bool = False) -> dict[str, _AccountRecord]:
    result: dict[str, _AccountRecord] = {}
    for record in records:
        if record.id in result:
            raise AccountExplorerError("result_too_complex", "Account hierarchy contains duplicate account identifiers.")
        result[record.id] = record
    if not allow_over_limit and len(result) != len(records):  # pragma: no cover - defensive
        raise AccountExplorerError("result_too_complex", "Account hierarchy contains duplicate account identifiers.")
    return result


def _effective_parent_map(records_by_id: dict[str, _AccountRecord]) -> tuple[dict[str, str | None], dict[str, StructureStatus]]:
    parent_by_id: dict[str, str | None] = {}
    structure_status: dict[str, StructureStatus] = {}
    for account_id, record in records_by_id.items():
        source_parent_id = record.source_parent_id
        if source_parent_id is not None and source_parent_id not in records_by_id:
            parent_by_id[account_id] = None
            structure_status[account_id] = "orphan_promoted"
        else:
            parent_by_id[account_id] = source_parent_id
            structure_status[account_id] = "ok"

    state: dict[str, int] = {}
    stack: list[str] = []
    stack_index: dict[str, int] = {}

    def visit(account_id: str) -> None:
        state[account_id] = 1
        stack_index[account_id] = len(stack)
        stack.append(account_id)
        parent_id = parent_by_id[account_id]
        if parent_id in records_by_id:
            parent_state = state.get(parent_id, 0)
            if parent_state == 0:
                visit(parent_id)
            elif parent_state == 1:
                cycle = stack[stack_index[parent_id] :]
                break_root = min(cycle)
                parent_by_id[break_root] = None
                for cycle_id in cycle:
                    structure_status[cycle_id] = "cycle_broken_root" if cycle_id == break_root else "cycle_member"
        stack.pop()
        stack_index.pop(account_id, None)
        state[account_id] = 2

    for account_id in sorted(records_by_id):
        if state.get(account_id, 0) == 0:
            visit(account_id)
    return parent_by_id, structure_status


def _children_by_parent(
    records_by_id: dict[str, _AccountRecord],
    parent_by_id: dict[str, str | None],
) -> dict[str | None, list[str]]:
    children: dict[str | None, list[str]] = defaultdict(list)
    for account_id in records_by_id:
        children[parent_by_id[account_id]].append(account_id)
    for siblings in children.values():
        siblings.sort(key=lambda account_id: _account_sort_key(records_by_id[account_id]))
    return dict(children)


def _sorted_roots(records_by_id: dict[str, _AccountRecord], children_by_parent: dict[str | None, list[str]]) -> list[str]:
    roots = list(children_by_parent.get(None, []))
    roots.sort(key=lambda account_id: _account_sort_key(records_by_id[account_id]))
    return roots


def _preorder(
    records_by_id: dict[str, _AccountRecord],
    children_by_parent: dict[str | None, list[str]],
) -> tuple[list[str], dict[str, int], dict[str, list[AccountExplorerPathSegmentDTO]], dict[str, str]]:
    preorder: list[str] = []
    depth_by_id: dict[str, int] = {}
    path_by_id: dict[str, list[AccountExplorerPathSegmentDTO]] = {}
    root_by_id: dict[str, str] = {}
    stack: list[tuple[str, int, str, list[AccountExplorerPathSegmentDTO]]] = []
    for root_id in reversed(_sorted_roots(records_by_id, children_by_parent)):
        stack.append((root_id, 0, root_id, []))
    while stack:
        account_id, depth, root_id, parent_path = stack.pop()
        if depth > MAX_DEPTH:
            raise AccountExplorerError(
                "result_too_deep",
                "Account hierarchy depth exceeds the bounded explorer limit.",
            )
        record = records_by_id[account_id]
        segment = AccountExplorerPathSegmentDTO(id=account_id, name=record.name)
        path = [*parent_path, segment]
        preorder.append(account_id)
        depth_by_id[account_id] = depth
        path_by_id[account_id] = path
        root_by_id[account_id] = root_id
        for child_id in reversed(children_by_parent.get(account_id, [])):
            stack.append((child_id, depth + 1, root_id, path))
    if len(preorder) != len(records_by_id):  # pragma: no cover - defensive graph repair
        raise AccountExplorerError("result_too_complex", "Account hierarchy could not be traversed safely.")
    return preorder, depth_by_id, path_by_id, root_by_id


def _record_matches(record: _AccountRecord, full_path: str, request: AccountExplorerQuery) -> bool:
    if request.hidden == "exclude" and record.hidden:
        return False
    if request.hidden == "only" and not record.hidden:
        return False
    if request.placeholder == "exclude" and record.placeholder:
        return False
    if request.placeholder == "only" and not record.placeholder:
        return False
    if request.types and record.type not in request.types:
        return False
    if request.query is not None:
        needle = request.query.casefold()
        if needle not in record.name.casefold() and needle not in full_path.casefold():
            return False
    return True


def _returned_ids(
    mode: AccountExplorerMode,
    preorder: list[str],
    self_matches: set[str],
    parent_by_id: dict[str, str | None],
) -> list[str]:
    if mode == "flat":
        returned = self_matches
    else:
        returned = set(self_matches)
        for account_id in self_matches:
            parent_id = parent_by_id[account_id]
            while parent_id is not None:
                if parent_id in returned:
                    parent_id = parent_by_id[parent_id]
                    continue
                returned.add(parent_id)
                parent_id = parent_by_id[parent_id]
    return [account_id for account_id in preorder if account_id in returned]


def _recursive_buckets(
    records_by_id: dict[str, _AccountRecord],
    children_by_parent: dict[str | None, list[str]],
    preorder: list[str],
) -> tuple[dict[str, dict[CommodityKey, Decimal]], int]:
    raw_recursive: dict[str, dict[CommodityKey, Decimal]] = {}
    rollup_cells = 0
    for account_id in reversed(preorder):
        record = records_by_id[account_id]
        buckets: dict[CommodityKey, Decimal] = {}
        if record.direct_split_count > 0:
            buckets[record.commodity_key] = record.direct_raw
        for child_id in children_by_parent.get(account_id, []):
            for key, value in raw_recursive[child_id].items():
                buckets[key] = buckets.get(key, Decimal("0")) + value
        raw_recursive[account_id] = buckets
        rollup_cells += len(buckets)
    return raw_recursive, rollup_cells


def _node_dto(
    record: _AccountRecord,
    *,
    path_by_id: dict[str, list[AccountExplorerPathSegmentDTO]],
    full_path_by_id: dict[str, str],
    depth_by_id: dict[str, int],
    children_by_parent: dict[str | None, list[str]],
    raw_recursive_buckets: dict[str, dict[CommodityKey, Decimal]],
    match_state: Literal["self", "ancestor_context"],
    structure_status: StructureStatus,
) -> AccountExplorerNodeDTO:
    direct_amount = _natural_sign(record.direct_raw, record.type)
    return AccountExplorerNodeDTO(
        id=record.id,
        source_parent_id=record.source_parent_id,
        parent_id=record.parent_id,
        root_id=record.root_id or record.id,
        path=path_by_id[record.id],
        full_path=full_path_by_id[record.id],
        depth=depth_by_id[record.id],
        name=record.name,
        type=record.type,
        commodity_namespace=record.commodity_namespace,
        commodity_mnemonic=record.commodity_mnemonic,
        hidden=record.hidden,
        placeholder=record.placeholder,
        child_count=len(children_by_parent.get(record.id, [])),
        direct_balance=_balance_dto(direct_amount, record.commodity_key),
        recursive_balances=[
            _balance_dto(_natural_sign(value, record.type), key)
            for key, value in sorted(raw_recursive_buckets[record.id].items(), key=lambda item: _commodity_sort_key(item[0]))
        ],
        match_state=match_state,
        structure_status=structure_status,
    )


def _balance_dto(amount: Decimal, key: CommodityKey) -> AccountExplorerBalanceDTO:
    return AccountExplorerBalanceDTO(
        amount=_decimal_string(amount),
        commodity_namespace=key[0],
        commodity_mnemonic=key[1],
    )


def _natural_sign(value: Decimal, account_type: str) -> Decimal:
    return -value if account_type in CREDIT_NATURAL_SIGN_TYPES else value


def _account_sort_key(record: _AccountRecord) -> tuple[str, str, str]:
    name = unicodedata.normalize("NFC", record.name)
    return name.casefold(), name, record.id


def _commodity_sort_key(key: CommodityKey) -> tuple[str, str, str, str]:
    namespace, mnemonic = key
    return namespace.casefold(), mnemonic.casefold(), namespace, mnemonic


def _split_quantity(split: Any) -> Decimal:
    value = getattr(split, "quantity", None)
    if value is None:
        value = getattr(split, "amount", None)
    if value is None:
        value = getattr(split, "value", None)
    return _decimal(value if value is not None else Decimal("0"))


def _decimal(value: Any) -> Decimal:
    if isinstance(value, float):
        raise AccountExplorerError("result_too_complex", "Account hierarchy contains unsafe non-Decimal money data.")
    try:
        parsed = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise AccountExplorerError("result_too_complex", "Account hierarchy contains unreadable Decimal data.") from exc
    if not parsed.is_finite():
        raise AccountExplorerError("result_too_complex", "Account hierarchy contains non-finite Decimal data.")
    return parsed


def _decimal_from_rational_text(value: Any) -> Decimal:
    text = str(value or "")
    try:
        numerator_text, denominator_text = text.split("/", 1)
        numerator = int(numerator_text)
        denominator = int(denominator_text)
    except (AttributeError, TypeError, ValueError) as exc:
        raise AccountExplorerError("result_too_complex", "Account hierarchy split aggregation returned unreadable Decimal data.") from exc
    return _decimal_from_fraction(numerator, denominator)


def _decimal_from_fraction(numerator: int, denominator: int) -> Decimal:
    if denominator == 0:
        raise AccountExplorerError("result_too_complex", "Account hierarchy contains invalid rational money data.")
    fraction = Fraction(numerator, denominator)
    numerator = fraction.numerator
    denominator = fraction.denominator
    twos = 0
    while denominator % 2 == 0:
        denominator //= 2
        twos += 1
    fives = 0
    while denominator % 5 == 0:
        denominator //= 5
        fives += 1
    if denominator != 1:
        raise AccountExplorerError("result_too_complex", "Account hierarchy contains non-terminating Decimal money data.")
    scale = max(twos, fives)
    scaled = numerator * (2 ** (scale - twos)) * (5 ** (scale - fives))
    result = Decimal(scaled).scaleb(-scale)
    if not result.is_finite():
        raise AccountExplorerError("result_too_complex", "Account hierarchy contains non-finite Decimal data.")
    return result


def _decimal_string(value: Decimal) -> str:
    if value.is_zero():
        return "0"
    text = format(value.normalize(), "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return "0" if text in {"", "-0"} else text


def _guid(value: Any) -> str:
    text = str(getattr(value, "guid", value) or "").strip().replace("-", "").lower()
    if not GUID_RE.match(text):
        raise AccountExplorerError("result_too_complex", "Account hierarchy contains an unreadable account identifier.")
    return text


def _optional_guid(value: Any) -> str | None:
    if value in (None, ""):
        return None
    return _guid(value)


def _serialized_response_bytes(response: AccountExplorerResponseDTO) -> int:
    response.scan.serialized_bytes = 0
    zero_size = len(response.model_dump_json().encode("utf-8"))
    size_without_zero = zero_size - 1
    for digits in range(1, 20):
        candidate = size_without_zero + digits
        if len(str(candidate)) == digits:
            return candidate
    raise AccountExplorerError("result_too_complex", "Account hierarchy response size could not be measured safely.")


def _limits() -> dict[str, int]:
    return {
        "candidate_accounts": MAX_CANDIDATE_ACCOUNTS,
        "returned_nodes": MAX_RETURNED_NODES,
        "depth": MAX_DEPTH,
        "commodity_buckets_per_subtree": MAX_COMMODITY_BUCKETS,
        "rollup_cells": MAX_ROLLUP_CELLS,
        "serialized_bytes": MAX_SERIALIZED_RESPONSE_BYTES,
        "data_queries": MAX_DATA_QUERIES,
        "query_codepoints": MAX_QUERY_CODEPOINTS,
        "type_filters": MAX_TYPE_FILTERS,
    }
