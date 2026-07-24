"""Pydantic DTOs for controlled GnuCash write operations."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator

DECIMAL_STRING_PATTERN = r"^-?(?:0|[1-9]\d*)(?:\.\d+)?$"
CURRENCY_CODE_PATTERN = r"^[A-Z]{3}$"


class TransactionSplitWriteDTO(BaseModel):
    """A single split in a transaction create request."""

    model_config = ConfigDict(extra="forbid")

    account_id: str = Field(..., min_length=1, description="Account GUID for this split")
    amount: str = Field(
        ...,
        pattern=DECIMAL_STRING_PATTERN,
        description="Split amount as decimal string, e.g. '-320.00'",
    )
    currency: str = Field(
        ...,
        pattern=CURRENCY_CODE_PATTERN,
        description="ISO 4217 currency code, e.g. 'SEK'",
    )
    memo: str = Field("", description="Split memo")

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        return value.upper()


class TransactionCreateRequestDTO(BaseModel):
    """Request body for creating a new transaction."""

    model_config = ConfigDict(extra="forbid")

    date: str = Field(..., description="Transaction date as YYYY-MM-DD")
    description: str = Field("", description="Transaction description")
    splits: list[TransactionSplitWriteDTO] = Field(
        ..., description="At least two splits required"
    )




class TransactionCreatePreviewRequestDTO(BaseModel):
    """Non-mutating owner web-UI preview request for one future CREATE."""

    model_config = ConfigDict(extra="forbid")

    date: str = Field(..., description="Transaction date as YYYY-MM-DD")
    debit_account_id: str = Field(..., description="Source/debit account GUID")
    credit_account_id: str = Field(..., description="Destination/credit account GUID")
    amount: str = Field(
        ...,
        pattern=DECIMAL_STRING_PATTERN,
        description="Positive amount as decimal string, e.g. '320.00'",
    )
    currency: str = Field(..., pattern=CURRENCY_CODE_PATTERN, description="ISO 4217 currency code")
    description: str = Field(..., description="Transaction description")
    memo: str = Field("", description="Optional split memo metadata")

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        return value.upper()


class TransactionCreateGeneralPreviewSplitRequestDTO(BaseModel):
    """One split in the #59 general non-mutating product CREATE preview."""

    model_config = ConfigDict(extra="forbid")

    account_id: str = Field(..., min_length=1)
    amount: str = Field(..., pattern=DECIMAL_STRING_PATTERN)
    memo: str = ""


class TransactionCreateGeneralPreviewRequestDTO(BaseModel):
    """General 2..50 split non-mutating product CREATE preview request."""

    model_config = ConfigDict(extra="forbid")

    date: str
    description: str
    currency: str = Field(..., pattern=CURRENCY_CODE_PATTERN)
    splits: list[TransactionCreateGeneralPreviewSplitRequestDTO]

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        return value.upper()


class TransactionCreatePreviewAccountDTO(BaseModel):
    """Resolved account display data for a non-mutating create preview."""

    id: str
    name: str
    display_name: str | None = None
    full_name: str
    type: str = "UNKNOWN"
    currency: str


class TransactionCreatePreviewDTO(BaseModel):
    """Private, normalized preview for one future transaction CREATE."""

    preview_only: bool = Field(True, description="Always true; no write was executed")
    writes_enabled_required_for_create: bool | None = None
    create_count: int = Field(1, description="Exact future CREATE count represented by this preview")
    confirm_allowed: bool = False
    preview_token: str | None = None
    expires_at: str | None = None
    idempotency_key: str | None = None
    create_generation: int | None = None
    date: str
    amount: str | None = None
    currency: str
    description: str
    memo: str | None = None
    debit_account: TransactionCreatePreviewAccountDTO | None = None
    credit_account: TransactionCreatePreviewAccountDTO | None = None
    splits: list[dict[str, Any] | TransactionSplitWriteDTO]
    warnings: list[Any] = Field(default_factory=list)


class TransactionPatchRequestDTO(BaseModel):
    """Request body for patching an existing transaction.

    Only description and split memos can be edited. Transaction dates,
    split amounts, accounts, split structure, and currencies cannot be changed.
    """

    model_config = ConfigDict(extra="forbid")

    description: str | None = Field(None, description="New transaction description")
    split_memos: dict[str, str] | None = Field(
        None,
        description="Map of split GUID to new memo text",
    )


class TransactionValidationResultDTO(BaseModel):
    """Result of validating a transaction before creation."""

    valid: bool = Field(..., description="Whether the transaction passes all validation checks")
    errors: list[str] = Field(default_factory=list, description="Validation errors that prevent writing")
    warnings: list[str] = Field(default_factory=list, description="Non-fatal warnings")
    summary: dict = Field(default_factory=dict, description="Normalized summary of the transaction")


class TransactionWriteResultDTO(BaseModel):
    """Result of a successful transaction write operation."""

    transaction_id: str = Field(..., description="GUID of the created/updated transaction")
    backup_path: str = Field(..., description="Path to the backup created before the write")
    audit_log_id: int | None = Field(None, description="ID of the audit log entry")
    readback_verified: bool | None = Field(
        None,
        description="True when the route performed read-only verification after a CREATE write",
    )
    readback_transaction_id: str | None = Field(
        None,
        description="GUID observed by the post-write read-back verification",
    )
    readback_transaction_present: bool | None = Field(
        None,
        description="True when the created transaction was found through the read-only path",
    )
    readback_split_count: int | None = Field(
        None,
        description="Split count observed by post-write read-only verification",
    )
    readback_split_balance_verified: bool | None = Field(
        None,
        description="True when read-back splits balance to zero by currency",
    )
    readback_split_balance_by_currency: dict[str, str] | None = Field(
        None,
        description="Read-back split totals by currency, expressed as decimal strings",
    )
    readback_currency: str | None = Field(
        None,
        description="Transaction currency observed by post-write read-only verification",
    )
    readback_currency_consistent: bool | None = Field(
        None,
        description="True when transaction, split, account, and request currencies match",
    )
    readback_account_balance_deltas_verified: bool | None = Field(
        None,
        description="True when read-only account balances changed by the created split amounts",
    )
    readback_account_balance_delta_count: int | None = Field(
        None,
        description="Number of request accounts whose balance delta was verified",
    )
    readback_account_balance_delta_total_by_currency: dict[str, str] | None = Field(
        None,
        description="Sum of verified account balance deltas by currency, expressed as decimal strings",
    )


class WriteAlphaAuditSummaryItemDTO(BaseModel):
    """Redacted audit-log summary for operator review of disposable write-alpha runs."""

    id: int = Field(..., description="App metadata audit row ID")
    action: str = Field(..., description="Write-alpha action name")
    result: str = Field(..., description="started, success, failed, or unknown")
    timestamp: str = Field(..., description="Audit timestamp from app metadata")
    transaction_id_prefix: str | None = Field(
        None, description="At most eight characters of the transaction GUID"
    )
    backup_present: bool = Field(..., description="Whether a redacted backup marker exists")
    backup_artifact_ref: str | None = Field(
        None,
        description="Opaque stable reference for distinguishing redacted backup artifacts",
    )
    error: str | None = Field(None, description="User-safe error summary without paths")


class WriteAlphaAuditSummaryDTO(BaseModel):
    """Read-only, redacted operator summary for current app metadata DB audit rows."""

    book_id: int = Field(..., description="Book ID whose app-metadata audit rows were summarized")
    items: list[WriteAlphaAuditSummaryItemDTO] = Field(default_factory=list)
    total_count: int = Field(..., description="Total filtered audit rows before response limiting")
    returned_count: int = Field(..., description="Number of redacted rows returned")
    counts_by_action: dict[str, int] = Field(
        default_factory=dict, description="Filtered row counts grouped by safe action label"
    )
    counts_by_result: dict[str, int] = Field(
        default_factory=dict, description="Filtered row counts grouped by safe result label"
    )
    ownership_summary: dict[str, int | str | None] = Field(
        default_factory=dict,
        description=(
            "Safe app-metadata ownership evidence: write-alpha-created count, "
            "non-owned mutation rejection count, and last mutation type"
        ),
    )
    filters: dict[str, str | int | None] = Field(
        default_factory=dict, description="Applied non-sensitive filter metadata"
    )
    pagination: dict[str, int | bool | None] = Field(
        default_factory=dict,
        description="Bounded limit/offset review metadata without exposing raw audit payloads",
    )
    time_window: dict[str, str | None] = Field(
        default_factory=dict, description="Safe requested and returned timestamp window metadata"
    )
    status_summary: list[str] = Field(
        default_factory=list, description="Bounded operator-safe status summary rows"
    )
    limitations: list[str] = Field(default_factory=list)
