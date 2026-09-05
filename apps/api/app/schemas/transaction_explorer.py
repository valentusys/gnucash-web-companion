"""DTOs for the bounded transaction explorer endpoint."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from app.schemas.gnucash import MoneyDTO, TransactionDirectionDTO, default_transaction_direction


class TransactionExplorerAccountRefDTO(BaseModel):
    """Display-only representative account reference."""

    id: str
    name: str
    display_name: str | None = None
    full_name: str | None = None


class TransactionExplorerItemDTO(BaseModel):
    """One bounded explorer result row.

    Representative fields are display-only. Advanced filtering uses
    matched_amount/matched_account_ids according to amount_basis, never the
    representative split by accident.
    """

    id: str = Field(..., description="Transaction GUID")
    date: str = Field(..., description="Transaction post date as YYYY-MM-DD")
    description: str = Field(..., description="Transaction description")
    representative_amount: MoneyDTO | None
    representative_account: TransactionExplorerAccountRefDTO | None = None
    counter_account_name: str = Field(..., description="Counter account label for display only")
    direction: TransactionDirectionDTO = Field(default_factory=default_transaction_direction, description="Split-derived typed From/To direction")
    matched_amount: MoneyDTO | None = Field(None, description="Exact scoped amount when a scoped filter is active")
    amount_basis: Literal["selected_accounts", "income", "expense", "representative_split", "neutral_magnitude", "multiple_amounts"] = "representative_split"
    matched_account_ids: list[str] = Field(default_factory=list)
    is_write_alpha_owned: bool = False


class TransactionExplorerScanMetadataDTO(BaseModel):
    """Bounded scan counters exposed without exact totals or private data."""

    candidate_rows: int = 0
    split_rows: int = 0
    query_count: int = 0
    scan_limited: bool = False
    exhausted: bool = True
    limits: dict[str, int] = Field(default_factory=dict)


class TransactionExplorerPageDTO(BaseModel):
    """A bounded keyset explorer page without total count."""

    items: list[TransactionExplorerItemDTO]
    normalized_filters: dict[str, Any]
    sort: Literal["date_desc", "date_asc"]
    page_size: int
    returned_count: int
    has_more: bool
    has_previous: bool
    next_cursor: str | None = None
    previous_cursor: str | None = None
    scan: TransactionExplorerScanMetadataDTO
    limitations: list[str] = Field(default_factory=list)
