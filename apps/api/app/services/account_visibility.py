"""Canonical account visibility and compact display-label helpers.

This module owns the #60 ordinary-account policy.  It hides only canonical
GnuCash structural roots and the canonical Template Root subtree, promotes
normal root children to top-level rows, and computes compact duplicate-safe
labels without exposing GUIDs as display text.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable
import unicodedata

MAX_ACCOUNT_ANCESTRY_DEPTH = 128


def account_guid(value: Any) -> str:
    """Return a stable normalized GnuCash account identifier for objects/values."""

    raw = getattr(value, "guid", value)
    return str(raw or "").strip().lower()


def account_parent_guid(account: Any) -> str | None:
    parent_guid = getattr(account, "parent_guid", None)
    if parent_guid:
        return account_guid(parent_guid)
    parent = getattr(account, "parent", None)
    if parent is None:
        return None
    parent_id = account_guid(parent)
    return parent_id or None


def account_type(account: Any) -> str:
    value = getattr(account, "type", None)
    if value is None:
        value = getattr(account, "account_type", None)
    return unicodedata.normalize("NFC", str(value or "")).upper()


def account_name(account: Any) -> str:
    return unicodedata.normalize("NFC", str(getattr(account, "name", "") or ""))


def account_code(account: Any) -> str:
    return unicodedata.normalize("NFC", str(getattr(account, "code", "") or "").strip())


def commodity_namespace(account: Any) -> str:
    commodity = getattr(account, "commodity", None)
    namespace = getattr(commodity, "namespace", None)
    if namespace is None:
        namespace = getattr(account, "commodity_namespace", None)
    if namespace is None and (getattr(commodity, "mnemonic", None) or getattr(account, "commodity_mnemonic", None) or getattr(account, "currency", None)):
        return "CURRENCY"
    return unicodedata.normalize("NFC", str(namespace or "")).upper()


def commodity_mnemonic(account: Any) -> str:
    commodity = getattr(account, "commodity", None)
    mnemonic = getattr(commodity, "mnemonic", None)
    if mnemonic is None:
        mnemonic = getattr(account, "commodity_mnemonic", None)
    if mnemonic is None:
        mnemonic = getattr(account, "currency", None)
    return unicodedata.normalize("NFC", str(mnemonic or "")).upper()


def split_account_id(split: Any) -> str | None:
    account_guid_value = getattr(split, "account_guid", None)
    if account_guid_value:
        return account_guid(account_guid_value)
    account = getattr(split, "account", None)
    if account is None:
        return None
    account_id = account_guid(account)
    return account_id or None


def transaction_splits(transaction: Any) -> list[Any]:
    return list(getattr(transaction, "splits", []) or [])


@dataclass(frozen=True)
class AccountPathSegment:
    id: str
    name: str
    display_name: str


@dataclass(frozen=True)
class AccountVisibilityIndex:
    accounts_by_id: dict[str, Any]
    root_account_id: str | None
    template_root_id: str | None
    structural_root_ids: frozenset[str]
    template_account_ids: frozenset[str]
    visible_account_ids: frozenset[str]
    effective_parent_by_id: dict[str, str | None]
    visible_children_by_id: dict[str | None, tuple[str, ...]]
    full_name_by_id: dict[str, str]
    display_name_by_id: dict[str, str]
    diagnostic_code: str | None = None

    def is_template_id(self, account_id: str | None) -> bool:
        return bool(account_id) and account_guid(account_id) in self.template_account_ids

    def is_structural_root_id(self, account_id: str | None) -> bool:
        return bool(account_id) and account_guid(account_id) in self.structural_root_ids

    def is_visible_id(self, account_id: str | None) -> bool:
        return bool(account_id) and account_guid(account_id) in self.visible_account_ids

    def is_visible_account(self, account: Any) -> bool:
        return self.is_visible_id(account_guid(account))

    def is_excluded_id(self, account_id: str | None) -> bool:
        return bool(account_id) and not self.is_visible_id(account_id)

    def exclusion_reason(self, account_id: str | None) -> str | None:
        if not account_id:
            return None
        normalized = account_guid(account_id)
        if normalized in self.template_account_ids:
            return "template"
        if normalized in self.structural_root_ids:
            return "root"
        if normalized in self.accounts_by_id and normalized not in self.visible_account_ids:
            return "excluded"
        return None

    def effective_parent_id(self, account: Any) -> str | None:
        return self.effective_parent_by_id.get(account_guid(account))

    def visible_children(self, account_id: str | None) -> tuple[str, ...]:
        return self.visible_children_by_id.get(account_id, ())

    def child_count(self, account: Any) -> int:
        return len(self.visible_children(account_guid(account)))

    def full_name(self, account: Any) -> str:
        account_id = account_guid(account)
        return self.full_name_by_id.get(account_id) or _fallback_account_full_name(account)

    def display_name(self, account: Any) -> str:
        account_id = account_guid(account)
        return self.display_name_by_id.get(account_id) or _trimmed_leaf(account)

    def path_segments(self, account: Any) -> list[AccountPathSegment]:
        account_id = account_guid(account)
        lineage = _lineage_ids(account_id, self.effective_parent_by_id)
        return [
            AccountPathSegment(
                id=item_id,
                name=account_name(self.accounts_by_id[item_id]),
                display_name=self.display_name_by_id.get(item_id) or account_name(self.accounts_by_id[item_id]),
            )
            for item_id in lineage
            if item_id in self.accounts_by_id and item_id in self.visible_account_ids
        ]

    def transaction_is_visible(self, transaction: Any) -> bool:
        for split in transaction_splits(transaction):
            account_id = split_account_id(split)
            if account_id is not None and account_guid(account_id) in self.accounts_by_id and not self.is_visible_id(account_id):
                return False
        return True


def build_account_visibility_index(book: Any, accounts: Iterable[Any] | None = None) -> AccountVisibilityIndex:
    all_accounts = _collect_accounts(book, accounts)
    accounts_by_id = {account_guid(account): account for account in all_accounts if account_guid(account)}
    parent_by_id = {account_id: account_parent_guid(account) for account_id, account in accounts_by_id.items()}

    root_account_id = _canonical_book_guid(book, "root_account_guid", "root_account")
    template_root_id = _canonical_book_guid(book, "root_template_guid", "root_template")

    diagnostic_code: str | None = None
    if not template_root_id:
        template_root_id, template_diag = _fallback_template_root_id(accounts_by_id, parent_by_id)
        diagnostic_code = template_diag or diagnostic_code
    if not root_account_id:
        root_account_id, root_diag = _fallback_normal_root_id(accounts_by_id, parent_by_id, template_root_id)
        diagnostic_code = root_diag or diagnostic_code

    template_ids = _descendant_ids(template_root_id, parent_by_id) if template_root_id else set()
    structural_roots = {
        account_id
        for account_id, account in accounts_by_id.items()
        if account_type(account) == "ROOT" and account_id not in template_ids
    }
    if root_account_id:
        structural_roots.add(root_account_id)

    excluded = set(template_ids) | structural_roots
    visible_ids = {account_id for account_id in accounts_by_id if account_id not in excluded}
    effective_parent_by_id = _effective_parent_map(accounts_by_id, parent_by_id, visible_ids, structural_roots)
    visible_children_by_id = _visible_children(accounts_by_id, effective_parent_by_id, visible_ids)
    full_name_by_id = _full_names(accounts_by_id, parent_by_id, visible_ids, template_ids, structural_roots)
    display_name_by_id = _display_names(accounts_by_id, effective_parent_by_id, visible_ids, full_name_by_id)

    return AccountVisibilityIndex(
        accounts_by_id=accounts_by_id,
        root_account_id=root_account_id,
        template_root_id=template_root_id,
        structural_root_ids=frozenset(structural_roots),
        template_account_ids=frozenset(template_ids),
        visible_account_ids=frozenset(visible_ids),
        effective_parent_by_id=effective_parent_by_id,
        visible_children_by_id=visible_children_by_id,
        full_name_by_id=full_name_by_id,
        display_name_by_id=display_name_by_id,
        diagnostic_code=diagnostic_code,
    )


def visible_accounts(index: AccountVisibilityIndex) -> list[Any]:
    rows = [index.accounts_by_id[account_id] for account_id in index.visible_account_ids]
    rows.sort(key=lambda account: _account_sort_key(account, index))
    return rows


def visible_transactions(book: Any, index: AccountVisibilityIndex) -> list[Any]:
    transactions = list(getattr(book, "transactions", []) or [])
    return [transaction for transaction in transactions if index.transaction_is_visible(transaction)]


def _collect_accounts(book: Any, accounts: Iterable[Any] | None) -> list[Any]:
    result: list[Any] = []
    seen_objects: set[int] = set()
    seen_ids: set[str] = set()

    def add(account: Any) -> None:
        if account is None:
            return
        object_id = id(account)
        account_id = account_guid(account)
        if object_id in seen_objects or (account_id and account_id in seen_ids):
            return
        seen_objects.add(object_id)
        if account_id:
            seen_ids.add(account_id)
        result.append(account)
        parent = getattr(account, "parent", None)
        if parent is not None:
            add(parent)

    for account in list(accounts) if accounts is not None else list(getattr(book, "accounts", []) or []):
        add(account)
    add(getattr(book, "root_account", None))
    add(getattr(book, "root_template", None))
    return result


def _canonical_book_guid(book: Any, guid_attr: str, object_attr: str) -> str | None:
    raw = getattr(book, guid_attr, None)
    if raw:
        normalized = account_guid(raw)
        if normalized:
            return normalized
    obj = getattr(book, object_attr, None)
    if obj is not None:
        normalized = account_guid(obj)
        if normalized:
            return normalized
    return None


def _fallback_template_root_id(
    accounts_by_id: dict[str, Any], parent_by_id: dict[str, str | None]
) -> tuple[str | None, str | None]:
    candidates = [
        account_id
        for account_id, account in accounts_by_id.items()
        if parent_by_id.get(account_id) is None
        and account_type(account) == "ROOT"
        and _normalized_name(account) == "template root"
    ]
    if len(candidates) == 1:
        return candidates[0], "canonical_template_root_fallback_used"
    if len(candidates) > 1:
        return None, "canonical_template_root_ambiguous"
    return None, "canonical_template_root_missing"


def _fallback_normal_root_id(
    accounts_by_id: dict[str, Any],
    parent_by_id: dict[str, str | None],
    template_root_id: str | None,
) -> tuple[str | None, str | None]:
    candidates = [
        account_id
        for account_id, account in accounts_by_id.items()
        if parent_by_id.get(account_id) is None and account_type(account) == "ROOT" and account_id != template_root_id
    ]
    if len(candidates) == 1:
        return candidates[0], "canonical_root_fallback_used"
    if len(candidates) > 1:
        return None, "canonical_root_ambiguous"
    return None, "canonical_root_missing"


def _descendant_ids(root_id: str | None, parent_by_id: dict[str, str | None]) -> set[str]:
    if not root_id:
        return set()
    result: set[str] = set()
    children: dict[str, list[str]] = {}
    for account_id, parent_id in parent_by_id.items():
        if parent_id:
            children.setdefault(parent_id, []).append(account_id)
    frontier = [root_id]
    for _depth in range(MAX_ACCOUNT_ANCESTRY_DEPTH):
        if not frontier:
            return result
        next_frontier: list[str] = []
        for account_id in frontier:
            if account_id in result:
                continue
            result.add(account_id)
            next_frontier.extend(children.get(account_id, []))
        frontier = next_frontier
    return result


def _effective_parent_map(
    accounts_by_id: dict[str, Any],
    parent_by_id: dict[str, str | None],
    visible_ids: set[str],
    structural_roots: set[str],
) -> dict[str, str | None]:
    effective: dict[str, str | None] = {}
    for account_id in accounts_by_id:
        if account_id not in visible_ids:
            effective[account_id] = None
            continue
        parent_id = parent_by_id.get(account_id)
        if parent_id in structural_roots:
            effective[account_id] = None
        elif parent_id in visible_ids:
            effective[account_id] = parent_id
        else:
            effective[account_id] = None
    return effective


def _visible_children(
    accounts_by_id: dict[str, Any],
    effective_parent_by_id: dict[str, str | None],
    visible_ids: set[str],
) -> dict[str | None, tuple[str, ...]]:
    children: dict[str | None, list[str]] = {}
    for account_id in visible_ids:
        children.setdefault(effective_parent_by_id.get(account_id), []).append(account_id)
    for siblings in children.values():
        siblings.sort(key=lambda account_id: _plain_account_sort_key(accounts_by_id[account_id]))
    return {parent_id: tuple(ids) for parent_id, ids in children.items()}


def _lineage_ids(account_id: str, effective_parent_by_id: dict[str, str | None]) -> list[str]:
    lineage: list[str] = []
    seen: set[str] = set()
    current: str | None = account_id
    for _depth in range(MAX_ACCOUNT_ANCESTRY_DEPTH):
        if current is None or current in seen:
            break
        seen.add(current)
        lineage.append(current)
        current = effective_parent_by_id.get(current)
    return list(reversed(lineage))


def _full_names(
    accounts_by_id: dict[str, Any],
    parent_by_id: dict[str, str | None],
    visible_ids: set[str],
    template_ids: set[str],
    structural_roots: set[str],
) -> dict[str, str]:
    names: dict[str, str] = {}
    for account_id in visible_ids:
        lineage = _source_lineage_ids(account_id, parent_by_id)
        names[account_id] = ":".join(
            account_name(accounts_by_id[item_id])
            for item_id in lineage
            if _full_name_includes_id(item_id, accounts_by_id, visible_ids, template_ids, structural_roots)
        )
    return names


def _source_lineage_ids(account_id: str, parent_by_id: dict[str, str | None]) -> list[str]:
    lineage: list[str] = []
    seen: set[str] = set()
    current: str | None = account_id
    for _depth in range(MAX_ACCOUNT_ANCESTRY_DEPTH):
        if current is None or current in seen:
            break
        seen.add(current)
        lineage.append(current)
        current = parent_by_id.get(current)
    return list(reversed(lineage))


def _full_name_includes_id(
    account_id: str,
    accounts_by_id: dict[str, Any],
    visible_ids: set[str],
    template_ids: set[str],
    structural_roots: set[str],
) -> bool:
    if account_id in template_ids:
        return False
    if account_id in visible_ids:
        return True
    if account_id in structural_roots:
        account = accounts_by_id.get(account_id)
        return bool(account is not None and _normalized_name(account) not in {"root account", "template root"})
    return False


def _display_names(
    accounts_by_id: dict[str, Any],
    effective_parent_by_id: dict[str, str | None],
    visible_ids: set[str],
    full_name_by_id: dict[str, str],
) -> dict[str, str]:
    groups: dict[str, list[str]] = {}
    for account_id in visible_ids:
        key = unicodedata.normalize("NFC", _trimmed_leaf(accounts_by_id[account_id])).casefold()
        groups.setdefault(key, []).append(account_id)

    result: dict[str, str] = {}
    for group_ids in groups.values():
        if len(group_ids) == 1:
            account_id = group_ids[0]
            result[account_id] = _trimmed_leaf(accounts_by_id[account_id])
            continue
        unresolved = set(group_ids)
        max_ancestor_count = max(len(_lineage_ids(account_id, effective_parent_by_id)) - 1 for account_id in group_ids)
        for suffix_len in range(1, max_ancestor_count + 1):
            candidates: dict[str, list[str]] = {}
            for account_id in unresolved:
                label = _ancestor_suffix_label(accounts_by_id, effective_parent_by_id, account_id, suffix_len)
                candidates.setdefault(label, []).append(account_id)
            for label, ids in candidates.items():
                if len(ids) == 1:
                    result[ids[0]] = label
            unresolved = {ids[0] for ids in candidates.values() if len(ids) > 1}
            if not unresolved:
                break
        if unresolved:
            by_code: dict[str, list[str]] = {}
            for account_id in unresolved:
                code = account_code(accounts_by_id[account_id])
                if code:
                    by_code.setdefault(f"{_trimmed_leaf(accounts_by_id[account_id])} — {code}", []).append(account_id)
            for label, ids in by_code.items():
                if len(ids) == 1:
                    result[ids[0]] = label
                    unresolved.discard(ids[0])
        if unresolved:
            by_type_commodity: dict[str, list[str]] = {}
            for account_id in unresolved:
                account = accounts_by_id[account_id]
                suffix = " ".join(part for part in (account_type(account), commodity_mnemonic(account)) if part)
                by_type_commodity.setdefault(f"{_trimmed_leaf(account)} — {suffix}".rstrip(), []).append(account_id)
            for label, ids in by_type_commodity.items():
                if len(ids) == 1:
                    result[ids[0]] = label
                    unresolved.discard(ids[0])
        if unresolved:
            ordered = sorted(unresolved)
            for ordinal, account_id in enumerate(ordered, start=1):
                result[account_id] = f"{_trimmed_leaf(accounts_by_id[account_id])} #{ordinal}"
    return result


def _ancestor_suffix_label(
    accounts_by_id: dict[str, Any],
    effective_parent_by_id: dict[str, str | None],
    account_id: str,
    suffix_len: int,
) -> str:
    leaf = _trimmed_leaf(accounts_by_id[account_id])
    lineage = _lineage_ids(account_id, effective_parent_by_id)
    ancestors = lineage[:-1]
    if not ancestors:
        return leaf
    suffix_ids = ancestors[-suffix_len:]
    suffix = " / ".join(account_name(accounts_by_id[item_id]) for item_id in suffix_ids)
    return f"{leaf} — {suffix}" if suffix else leaf


def _fallback_account_full_name(account: Any) -> str:
    names: list[str] = []
    current = account
    seen: set[int] = set()
    for _depth in range(MAX_ACCOUNT_ANCESTRY_DEPTH):
        if current is None or id(current) in seen:
            break
        seen.add(id(current))
        if account_type(current) != "ROOT" and account_name(current):
            names.append(account_name(current))
        current = getattr(current, "parent", None)
    return ":".join(reversed(names))


def _trimmed_leaf(account: Any) -> str:
    name = account_name(account).strip()
    return name or "Unnamed account"


def _normalized_name(account: Any) -> str:
    return _trimmed_leaf(account).casefold()


def _plain_account_sort_key(account: Any) -> tuple[str, str, str]:
    name = account_name(account)
    return name.casefold(), name, account_guid(account)


def _account_sort_key(account: Any, index: AccountVisibilityIndex) -> tuple[str, str, str, str]:
    full_name = index.full_name(account)
    display_name = index.display_name(account)
    return full_name.casefold(), display_name.casefold(), full_name, account_guid(account)
