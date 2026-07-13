"""DTOs for the bounded account hierarchy explorer endpoint."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

AccountExplorerMode = Literal["tree", "flat"]
AccountExplorerMatchState = Literal["self", "ancestor_context"]
AccountExplorerStructureStatus = Literal["ok", "orphan_promoted", "cycle_broken_root", "cycle_member"]


class AccountExplorerPathSegmentDTO(BaseModel):
    """One ID-backed account path segment."""

    id: str
    name: str


class AccountExplorerBalanceDTO(BaseModel):
    """Exact native-commodity Decimal balance bucket."""

    amount: str = Field(..., description="Finite non-exponent Decimal string")
    commodity_namespace: str
    commodity_mnemonic: str


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
    match_state: AccountExplorerMatchState = "self"
    structure_status: AccountExplorerStructureStatus = "ok"


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
