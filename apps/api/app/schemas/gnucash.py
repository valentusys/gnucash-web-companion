"""Pydantic DTOs for read-only GnuCash book data."""

from __future__ import annotations

from pydantic import BaseModel, Field


class MoneyDTO(BaseModel):
    """Exact decimal money amount with currency."""

    amount: str = Field(..., description="Decimal amount as string, e.g. '123.45'")
    currency: str = Field(..., description="ISO 4217 currency code, e.g. 'SEK'")


class AccountDTO(BaseModel):
    """GnuCash account information."""

    id: str = Field(..., description="Account GUID")
    name: str = Field(..., description="Short account name")
    full_name: str = Field(..., description="Colon-separated full path, e.g. 'Assets:Bank:Checking'")
    type: str = Field(..., description="Account type, e.g. 'BANK'")
    currency: str = Field(..., description="ISO 4217 currency code")
    balance: str = Field(..., description="Current balance as decimal string")
    placeholder: bool = Field(False, description="Whether this is a placeholder account")
    hidden: bool = Field(False, description="Whether this account is hidden")
    parent_id: str | None = Field(None, description="Parent account GUID, null for top-level")


class AccountTreeNodeDTO(AccountDTO):
    """Account DTO with nested children for tree views."""

    children: list["AccountTreeNodeDTO"] = Field(default_factory=list)


class TransactionSplitDTO(BaseModel):
    """A single split within a GnuCash transaction."""

    account_id: str = Field(..., description="Account GUID for this split")
    account_name: str = Field(..., description="Full account name for this split")
    memo: str = Field("", description="Split memo")
    amount: str = Field(..., description="Split amount as decimal string")
    currency: str = Field(..., description="ISO 4217 currency code")


class TransactionListItemDTO(BaseModel):
    """Summary of a single transaction for list views."""

    id: str = Field(..., description="Transaction GUID")
    date: str = Field(..., description="Transaction date as YYYY-MM-DD")
    description: str = Field(..., description="Transaction description")
    amount: str = Field(..., description="Amount relevant to the queried account as decimal string")
    currency: str = Field(..., description="ISO 4217 currency code")
    account_id: str = Field(..., description="The account this amount relates to")
    account_name: str = Field(..., description="Full name of the related account")
    counter_account_name: str = Field(..., description="Full name of the counter account or 'Split transaction'")


class TransactionDetailDTO(BaseModel):
    """Full transaction detail with all splits."""

    id: str = Field(..., description="Transaction GUID")
    date: str = Field(..., description="Transaction date as YYYY-MM-DD")
    description: str = Field(..., description="Transaction description")
    currency: str = Field(..., description="Transaction currency ISO 4217 code")
    splits: list[TransactionSplitDTO] = Field(default_factory=list, description="All splits in this transaction")


class BookSummaryDTO(BaseModel):
    """High-level summary of a GnuCash book."""

    account_count: int
    transaction_count: int
    currency: str


class CashflowDTO(BaseModel):
    """Basic cashflow totals over a date range."""

    date_from: str
    date_to: str
    currency: str
    inflow: str
    outflow: str
    net: str


class ReportSummaryDTO(BaseModel):
    """Dashboard summary: net worth, assets, liabilities, income/expenses this month.

    Multi-currency limitation: only accounts whose commodity matches the book's
    base currency are included. Accounts in other currencies are excluded with an
    explicit limitation message; no currency conversion is performed.
    """

    currency: str
    net_worth: str
    assets: str
    liabilities: str
    income_this_month: str
    expenses_this_month: str
    as_of_date: str
    reporting_basis: str = "base_currency_only"
    includes_currency_conversion: bool = False
    limitations: list[str] = Field(default_factory=list)


class ExpenseByAccountDTO(BaseModel):
    """Total expenses for a single account within a date range."""

    account_id: str
    account_name: str
    total: str
    currency: str


class CashflowPeriodDTO(BaseModel):
    """Cashflow totals broken down by month."""

    month: str  # YYYY-MM
    inflow: str
    outflow: str
    net: str


class PaginatedResponse(BaseModel):
    """Generic paginated response wrapper."""

    items: list = Field(default_factory=list)
    limit: int = 50
    offset: int = 0
    total: int = 0
