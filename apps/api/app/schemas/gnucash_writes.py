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
