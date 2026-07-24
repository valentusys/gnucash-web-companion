"""Split-value transaction direction DTO builder."""

from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from typing import Any, Literal

from app.schemas.gnucash import TransactionDirectionDTO, TransactionDirectionEntryDTO
from app.services.account_visibility import AccountVisibilityIndex, account_guid, commodity_mnemonic, split_account_id


@dataclass
class _Aggregate:
    account: Any
    value: Decimal = Decimal("0")
    split_count: int = 0
    order: int = 0


def build_transaction_direction(
    transaction: Any,
    *,
    visibility: AccountVisibilityIndex | None = None,
    fallback_currency: str = "XXX",
) -> TransactionDirectionDTO:
    """Build a typed From/To direction from signed split.value amounts.

    Negative split values are sources (from_accounts); positive values are
    destinations (to_accounts).  Repeated same-account/same-sign splits are
    aggregated exactly and zero values are ignored.
    """

    from_entries: dict[str, _Aggregate] = {}
    to_entries: dict[str, _Aggregate] = {}
    order = 0
    currency = _transaction_currency(transaction, fallback_currency)

    for split in list(getattr(transaction, "splits", []) or []):
        account = getattr(split, "account", None)
        account_id = split_account_id(split)
        if account is None or not account_id:
            continue
        amount = _split_value(split)
        if amount == Decimal("0"):
            continue
        if currency == "XXX":
            currency = commodity_mnemonic(account) or fallback_currency
        bucket = from_entries if amount < 0 else to_entries
        if account_id not in bucket:
            bucket[account_id] = _Aggregate(account=account, order=order)
            order += 1
        aggregate = bucket[account_id]
        aggregate.value += amount
        aggregate.split_count += 1

    from_list = sorted(from_entries.values(), key=lambda item: item.order)
    to_list = sorted(to_entries.values(), key=lambda item: item.order)
    from_total = sum((abs(item.value) for item in from_list), Decimal("0"))
    to_total = sum((item.value for item in to_list), Decimal("0"))

    from_ids = set(from_entries)
    to_ids = set(to_entries)
    if from_ids & to_ids:
        status: Literal["resolved", "composite", "ambiguous"] = "ambiguous"
        reason: Literal[
            "balanced",
            "multiple_accounts",
            "no_nonzero_splits",
            "single_sided",
            "unbalanced",
            "account_on_both_sides",
        ] = "account_on_both_sides"
    elif not from_list and not to_list:
        status = "ambiguous"
        reason = "no_nonzero_splits"
    elif not from_list or not to_list:
        status = "ambiguous"
        reason = "single_sided"
    elif from_total != to_total:
        status = "ambiguous"
        reason = "unbalanced"
    elif len(from_list) == 1 and len(to_list) == 1:
        status = "resolved"
        reason = "balanced"
    else:
        status = "composite"
        reason = "multiple_accounts"

    return TransactionDirectionDTO(
        status=status,
        reason=reason,
        currency=currency,
        from_accounts=[_entry_dto(item, visibility=visibility) for item in from_list],
        to_accounts=[_entry_dto(item, visibility=visibility) for item in to_list],
    )


def _entry_dto(aggregate: _Aggregate, *, visibility: AccountVisibilityIndex | None) -> TransactionDirectionEntryDTO:
    account = aggregate.account
    if visibility is not None:
        display_name = visibility.display_name(account)
        full_name = visibility.full_name(account)
    else:
        display_name = str(getattr(account, "name", "") or "")
        full_name = display_name
    return TransactionDirectionEntryDTO(
        account_id=account_guid(account),
        display_name=display_name,
        full_name=full_name,
        value=_decimal_text(aggregate.value),
        split_count=aggregate.split_count,
    )


def _transaction_currency(transaction: Any, fallback_currency: str) -> str:
    for attr in ("currency", "commodity"):
        commodity = getattr(transaction, attr, None)
        mnemonic = getattr(commodity, "mnemonic", None)
        if mnemonic:
            return str(mnemonic).upper()
    return str(fallback_currency or "XXX").upper()


def _split_value(split: Any) -> Decimal:
    value = getattr(split, "value", None)
    if value is None:
        value = getattr(split, "amount", None)
    if value is None:
        value = Decimal("0")
    if isinstance(value, float):
        raise TypeError("split.value must not be float")
    try:
        parsed = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError("split.value must be a finite Decimal") from exc
    if not parsed.is_finite():
        raise ValueError("split.value must be finite")
    return parsed


def _decimal_text(value: Decimal) -> str:
    return format(value, "f")
