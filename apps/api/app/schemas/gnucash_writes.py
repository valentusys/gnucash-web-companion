"""Pydantic DTOs for controlled GnuCash write operations."""

from __future__ import annotations

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


class TransactionPatchRequestDTO(BaseModel):
    """Request body for patching an existing transaction.

    Only description, date, and split memos can be edited.
    Split amounts and accounts cannot be changed.
    """

    model_config = ConfigDict(extra="forbid")

    description: str | None = Field(None, description="New transaction description")
    date: str | None = Field(None, description="New transaction date as YYYY-MM-DD")
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
