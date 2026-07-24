"""Deterministic reporting-currency resolver for GnuCash reports."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Iterable

from app.schemas.gnucash import ReportingCurrencyCandidateDTO, ReportingCurrencyResolutionDTO
from app.services.account_visibility import (
    AccountVisibilityIndex,
    account_guid,
    account_type,
    build_account_visibility_index,
    commodity_mnemonic,
    commodity_namespace,
    split_account_id,
    transaction_splits,
)

ELIGIBLE_REPORTING_ACCOUNT_TYPES = frozenset(
    {
        "ASSET",
        "BANK",
        "CASH",
        "RECEIVABLE",
        "LIABILITY",
        "CREDIT",
        "PAYABLE",
        "EQUITY",
        "INCOME",
        "EXPENSE",
    }
)


class ReportingCurrencySetupRequired(Exception):
    """Raised by ready-only report sections when no deterministic currency exists."""

    def __init__(self, resolution: ReportingCurrencyResolutionDTO) -> None:
        self.resolution = resolution
        super().__init__("Reporting currency setup is required")

    def detail(self) -> dict[str, Any]:
        return {
            "code": "REPORTING_CURRENCY_SETUP_REQUIRED",
            "reporting_currency": self.resolution.model_dump(),
        }


@dataclass(frozen=True)
class _CandidateStats:
    currency: str
    distinct_transaction_ids: frozenset[str]
    nonzero_split_count: int
    active_leaf_account_ids: frozenset[str]
    eligible_leaf_account_count: int

    @property
    def score(self) -> tuple[int, int, int, int]:
        return (
            len(self.distinct_transaction_ids),
            self.nonzero_split_count,
            len(self.active_leaf_account_ids),
            self.eligible_leaf_account_count,
        )

    def dto(self) -> ReportingCurrencyCandidateDTO:
        return ReportingCurrencyCandidateDTO(
            currency=self.currency,
            distinct_transaction_count=len(self.distinct_transaction_ids),
            nonzero_split_count=self.nonzero_split_count,
            active_leaf_account_count=len(self.active_leaf_account_ids),
            eligible_leaf_account_count=self.eligible_leaf_account_count,
        )


def resolve_reporting_currency(
    book: Any,
    configured_currency: str | None,
    *,
    visibility: AccountVisibilityIndex | None = None,
    transactions: Iterable[Any] | None = None,
) -> ReportingCurrencyResolutionDTO:
    index = visibility or build_account_visibility_index(book)
    configured = _normalize_currency(configured_currency)
    stats_by_currency = _candidate_stats(book, index, transactions=transactions)
    candidates = [stats.dto() for stats in sorted(stats_by_currency.values(), key=lambda item: item.currency)]
    configured_status = _configured_status(book, index, configured, stats_by_currency)

    selected: str | None = None
    source = "none"
    status = "setup_required"
    reason = "no_eligible_currency"

    if configured_status == "valid" and configured is not None:
        selected = configured
        source = "configured"
        status = "ready"
        reason = "configured_valid"
    elif stats_by_currency:
        ranked = sorted(stats_by_currency.values(), key=lambda item: item.score, reverse=True)
        top = ranked[0]
        tied = [item for item in ranked if item.score == top.score]
        if len(tied) == 1:
            selected = top.currency
            source = "detected"
            status = "ready"
            reason = "dominant_detected"
        else:
            reason = "dominance_tie"

    excluded = sorted(currency for currency in stats_by_currency if currency != selected)
    return ReportingCurrencyResolutionDTO(
        status=status,  # type: ignore[arg-type]
        source=source,  # type: ignore[arg-type]
        reason=reason,  # type: ignore[arg-type]
        configured_currency=configured,
        configured_currency_status=configured_status,  # type: ignore[arg-type]
        selected_currency=selected,
        candidates=candidates,
        excluded_currencies=excluded,
        non_currency_commodities_excluded=_has_visible_non_currency_commodity(index),
    )


def require_ready_reporting_currency(
    book: Any,
    configured_currency: str | None,
    *,
    visibility: AccountVisibilityIndex | None = None,
    transactions: Iterable[Any] | None = None,
) -> ReportingCurrencyResolutionDTO:
    resolution = resolve_reporting_currency(book, configured_currency, visibility=visibility, transactions=transactions)
    if resolution.status != "ready" or resolution.selected_currency is None:
        raise ReportingCurrencySetupRequired(resolution)
    return resolution


def _candidate_stats(
    book: Any,
    index: AccountVisibilityIndex,
    *,
    transactions: Iterable[Any] | None = None,
) -> dict[str, _CandidateStats]:
    eligible_accounts: dict[str, Any] = {}
    eligible_count_by_currency: dict[str, int] = {}
    for account_id in sorted(index.visible_account_ids):
        account = index.accounts_by_id[account_id]
        if not _is_eligible_leaf_account(account, index):
            continue
        currency = commodity_mnemonic(account)
        eligible_accounts[account_id] = account
        eligible_count_by_currency[currency] = eligible_count_by_currency.get(currency, 0) + 1

    tx_ids_by_currency: dict[str, set[str]] = {currency: set() for currency in eligible_count_by_currency}
    split_count_by_currency: dict[str, int] = {currency: 0 for currency in eligible_count_by_currency}
    active_accounts_by_currency: dict[str, set[str]] = {currency: set() for currency in eligible_count_by_currency}

    transaction_rows = transactions if transactions is not None else list(getattr(book, "transactions", []) or [])
    for transaction in transaction_rows:
        if not index.transaction_is_visible(transaction):
            continue
        transaction_id = account_guid(transaction)
        for split in transaction_splits(transaction):
            account_id = split_account_id(split)
            if account_id not in eligible_accounts:
                split_account = getattr(split, "account", None)
                if account_id not in index.accounts_by_id and _is_eligible_unindexed_split_account(split_account):
                    currency = commodity_mnemonic(split_account)
                    eligible_accounts[account_id or account_guid(split_account)] = split_account
                    eligible_count_by_currency[currency] = eligible_count_by_currency.get(currency, 0) + 1
                    tx_ids_by_currency.setdefault(currency, set())
                    split_count_by_currency.setdefault(currency, 0)
                    active_accounts_by_currency.setdefault(currency, set())
                else:
                    continue
            if account_id not in eligible_accounts:
                continue
            value = _split_value(split)
            if value == Decimal("0"):
                continue
            currency = commodity_mnemonic(eligible_accounts[account_id])
            tx_ids_by_currency.setdefault(currency, set()).add(transaction_id)
            split_count_by_currency[currency] = split_count_by_currency.get(currency, 0) + 1
            active_accounts_by_currency.setdefault(currency, set()).add(account_id)

    result: dict[str, _CandidateStats] = {}
    for currency, eligible_count in eligible_count_by_currency.items():
        tx_ids = tx_ids_by_currency.get(currency, set())
        nonzero_count = split_count_by_currency.get(currency, 0)
        if eligible_count < 1 or not tx_ids or nonzero_count < 1:
            continue
        result[currency] = _CandidateStats(
            currency=currency,
            distinct_transaction_ids=frozenset(tx_ids),
            nonzero_split_count=nonzero_count,
            active_leaf_account_ids=frozenset(active_accounts_by_currency.get(currency, set())),
            eligible_leaf_account_count=eligible_count,
        )
    return result


def _is_eligible_leaf_account(account: Any, index: AccountVisibilityIndex) -> bool:
    account_id = account_guid(account)
    if not index.is_visible_id(account_id):
        return False
    if bool(getattr(account, "hidden", False)) or bool(getattr(account, "placeholder", False)):
        return False
    if index.visible_children(account_id):
        return False
    if account_type(account) not in ELIGIBLE_REPORTING_ACCOUNT_TYPES:
        return False
    if commodity_namespace(account) != "CURRENCY":
        return False
    mnemonic = commodity_mnemonic(account)
    return bool(mnemonic) and mnemonic != "XXX"


def _is_eligible_unindexed_split_account(account: Any) -> bool:
    if account is None:
        return False
    if bool(getattr(account, "hidden", False)) or bool(getattr(account, "placeholder", False)):
        return False
    if account_type(account) not in ELIGIBLE_REPORTING_ACCOUNT_TYPES:
        return False
    if commodity_namespace(account) != "CURRENCY":
        return False
    mnemonic = commodity_mnemonic(account)
    return bool(mnemonic) and mnemonic != "XXX"


def _configured_status(
    book: Any,
    index: AccountVisibilityIndex,
    configured: str | None,
    stats_by_currency: dict[str, _CandidateStats],
) -> str:
    if configured is None:
        return "missing"
    if configured == "XXX":
        return "xxx"
    if configured in stats_by_currency:
        return "valid"

    commodity_mnemonics = {
        _normalize_currency(getattr(commodity, "mnemonic", None))
        for commodity in list(getattr(book, "commodities", []) or [])
    }
    visible_currency_occurrence = False
    visible_non_currency_occurrence = False
    template_currency_occurrence = False
    any_occurrence = configured in commodity_mnemonics

    for account_id, account in index.accounts_by_id.items():
        mnemonic = commodity_mnemonic(account)
        if mnemonic != configured:
            continue
        any_occurrence = True
        namespace = commodity_namespace(account)
        if index.is_template_id(account_id):
            if namespace == "CURRENCY":
                template_currency_occurrence = True
            continue
        if not index.is_visible_id(account_id):
            continue
        if namespace == "CURRENCY":
            visible_currency_occurrence = True
        else:
            visible_non_currency_occurrence = True

    if visible_non_currency_occurrence and not visible_currency_occurrence:
        return "non_monetary"
    if visible_currency_occurrence:
        return "inactive"
    if template_currency_occurrence:
        return "template_only"
    if not any_occurrence:
        return "absent"
    return "inactive"


def _has_visible_non_currency_commodity(index: AccountVisibilityIndex) -> bool:
    return any(
        index.is_visible_id(account_id) and commodity_namespace(account) != "CURRENCY"
        for account_id, account in index.accounts_by_id.items()
    )


def _normalize_currency(value: Any) -> str | None:
    text = str(value or "").strip().upper()
    return text or None


def _split_value(split: Any) -> Decimal:
    value = getattr(split, "value", None)
    if value is None:
        return Decimal("0")
    if isinstance(value, float):
        raise TypeError("split.value must not be float")
    try:
        parsed = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("split.value must be a finite Decimal") from exc
    if not parsed.is_finite():
        raise ValueError("split.value must be finite")
    return parsed
