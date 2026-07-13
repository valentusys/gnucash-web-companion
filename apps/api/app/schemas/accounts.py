"""DTOs for the bounded account hierarchy explorer endpoint."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

AccountExplorerMode = Literal["tree", "flat"]
AccountExplorerMatchState = Literal["match", "ancestor_context"]
AccountExplorerStructureStatus = Literal["root", "normal", "orphan_promoted", "cycle_broken_root", "cycle_member"]
AccountActivitySection = Literal["change", "recent_transactions"]
AccountActivitySectionStatusValue = Literal["ok", "empty", "error"]


class AccountExplorerPathSegmentDTO(BaseModel):
    """One ID-backed account path segment."""

    id: str
    name: str


class CommodityRefDTO(BaseModel):
    """Exact native commodity reference."""

    namespace: str
    mnemonic: str


class CommodityAmountDTO(BaseModel):
    """Exact finite non-exponent Decimal amount in one native commodity."""

    amount: str = Field(..., description="Finite non-exponent Decimal string")
    commodity: CommodityRefDTO


AccountExplorerBalanceDTO = CommodityAmountDTO


class AccountExplorerNodeDTO(BaseModel):
    """One account node in deterministic flat depth-first preorder."""

    id: str
    source_parent_id: str | None = None
    parent_id: str | None = None
    root_id: str
    path: list[AccountExplorerPathSegmentDTO]
    full_path: str
    depth: int
    name: str
    type: str
    commodity_namespace: str
    commodity_mnemonic: str
    hidden: bool = False
    placeholder: bool = False
    child_count: int = 0
    direct_balance: AccountExplorerBalanceDTO
    recursive_balances: list[AccountExplorerBalanceDTO] = Field(default_factory=list)
    match_state: AccountExplorerMatchState = "match"
    structure_status: AccountExplorerStructureStatus = "normal"


class AccountExplorerScanDTO(BaseModel):
    """Bounded scan counters exposed without private book data."""

    candidate_accounts: int = 0
    returned_nodes: int = 0
    split_rows: int = 0
    split_aggregate_rows: int = 0
    query_count: int = 0
    rollup_cells: int = 0
    serialized_bytes: int = 0
    exhausted: bool = True
    limits: dict[str, int] = Field(default_factory=dict)


class AccountExplorerResponseDTO(BaseModel):
    """Bounded account hierarchy explorer response."""

    book_id: int
    mode: AccountExplorerMode
    normalized_filters: dict[str, Any]
    root_ids: list[str]
    nodes: list[AccountExplorerNodeDTO]
    returned_count: int
    scan: AccountExplorerScanDTO
    balance_basis: Literal["native_commodity_account_natural_sign"] = "native_commodity_account_natural_sign"
    includes_currency_conversion: bool = False
    limitations: list[str] = Field(default_factory=list)


class AccountOverviewChildDTO(BaseModel):
    """Immediate child account summary for the bounded account overview."""

    id: str
    source_parent_id: str | None = None
    parent_id: str | None = None
    root_id: str
    path: list[AccountExplorerPathSegmentDTO]
    full_path: str
    depth: int
    name: str
    type: str
    commodity_namespace: str
    commodity_mnemonic: str
    hidden: bool = False
    placeholder: bool = False
    child_count: int = 0
    direct_balance: AccountExplorerBalanceDTO
    recursive_balances: list[AccountExplorerBalanceDTO] = Field(default_factory=list)
    structure_status: AccountExplorerStructureStatus = "normal"


class AccountOverviewResponseDTO(BaseModel):
    """Bounded read-only overview for one selected account."""

    book_id: int
    id: str
    source_parent_id: str | None = None
    parent_id: str | None = None
    root_id: str
    path: list[AccountExplorerPathSegmentDTO]
    full_path: str
    depth: int
    name: str
    type: str
    commodity_namespace: str
    commodity_mnemonic: str
    hidden: bool = False
    placeholder: bool = False
    direct_balance: AccountExplorerBalanceDTO
    recursive_balances: list[AccountExplorerBalanceDTO] = Field(default_factory=list)
    structure_status: AccountExplorerStructureStatus = "normal"
    breadcrumbs: list[AccountExplorerPathSegmentDTO]
    subtree_account_count: int
    child_count: int
    children: list[AccountOverviewChildDTO] = Field(default_factory=list)
    children_returned: int
    children_truncated: bool
    scan: AccountExplorerScanDTO
    balance_basis: Literal["native_commodity_account_natural_sign"] = "native_commodity_account_natural_sign"
    includes_currency_conversion: bool = False
    limitations: list[str] = Field(default_factory=list)


class AccountActivityRecentTransactionDTO(BaseModel):
    """One recent direct-account activity row without total-count semantics."""

    id: str
    date: str
    description: str
    matched_quantity: AccountExplorerBalanceDTO
    counter_account_name: str
    is_write_alpha_owned: bool = False


class AccountActivitySectionStatusDTO(BaseModel):
    """Per-section safe status for account activity."""

    section: AccountActivitySection
    status: AccountActivitySectionStatusValue
    detail: str | None = None


class AccountActivityScanDTO(BaseModel):
    """Bounded account activity counters exposed without exact totals."""

    selected_accounts: int = 1
    change_split_rows: int = 0
    recent_transaction_objects: int = 0
    recent_split_rows: int = 0
    query_count: int = 0
    serialized_bytes: int = 0
    limits: dict[str, int] = Field(default_factory=dict)


class AccountActivityResponseDTO(BaseModel):
    """Bounded direct-account activity response."""

    book_id: int
    account_id: str
    date_from: str
    date_to: str
    scope: Literal["direct_account"] = "direct_account"
    commodity_namespace: str
    commodity_mnemonic: str
    change: AccountExplorerBalanceDTO | None = None
    inflow: AccountExplorerBalanceDTO | None = None
    outflow: AccountExplorerBalanceDTO | None = None
    flow_status: Literal["not_applicable_for_generic_account"] = "not_applicable_for_generic_account"
    recent_transactions: list[AccountActivityRecentTransactionDTO] = Field(default_factory=list)
    limit: int
    returned_count: int
    has_more: bool = False
    transaction_explorer_compatible: bool = False
    partial_failure: bool = False
    section_statuses: list[AccountActivitySectionStatusDTO] = Field(default_factory=list)
    scan: AccountActivityScanDTO
    limitations: list[str] = Field(default_factory=list)
