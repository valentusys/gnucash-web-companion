"""Pydantic DTOs for read-only GnuCash book data."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class MoneyDTO(BaseModel):
    """Exact decimal money amount with currency."""

    amount: str = Field(..., description="Decimal amount as string, e.g. '123.45'")
    currency: str = Field(..., description="ISO 4217 currency code, e.g. 'SEK'")


class AccountDTO(BaseModel):
    """GnuCash account information."""

    id: str = Field(..., description="Account GUID")
    name: str = Field(..., description="Short account name")
    display_name: str | None = Field(None, description="Compact duplicate-safe account label")
    full_name: str = Field(..., description="Colon-separated full path, e.g. 'Assets:Bank:Checking'")
    type: str = Field(..., description="Account type, e.g. 'BANK'")
    currency: str = Field(..., description="ISO 4217 currency code")
    balance: str = Field(..., description="Current balance as decimal string")
    placeholder: bool = Field(False, description="Whether this is a placeholder account")
    hidden: bool = Field(False, description="Whether this account is hidden")
    parent_id: str | None = Field(None, description="Parent account GUID, null for top-level")
    commodity_namespace: str | None = Field(
        None,
        exclude=True,
        description="Internal commodity namespace for write-preview safety checks; excluded from public serialization",
    )
    commodity_fraction: int | None = Field(
        None,
        exclude=True,
        description="Internal commodity fraction for write-preview decimal precision checks; excluded from public serialization",
    )
    ordinary_visibility_excluded: bool = Field(
        False,
        exclude=True,
        description="Internal guard: structural root/template subtree accounts are excluded from ordinary read surfaces",
    )
    ordinary_visibility_reason: str | None = Field(
        None,
        exclude=True,
        description="Internal guard reason for non-ordinary accounts; excluded from public serialization",
    )


class AccountTreeNodeDTO(AccountDTO):
    """Account DTO with nested children for tree views."""

    children: list["AccountTreeNodeDTO"] = Field(default_factory=list)


class TransactionSplitDTO(BaseModel):
    """A single split within a GnuCash transaction."""

    account_id: str = Field(..., description="Account GUID for this split")
    account_name: str = Field(..., description="Full account name for this split")
    account_display_name: str | None = Field(None, description="Compact duplicate-safe account label")
    memo: str = Field("", description="Split memo")
    reconcile_state: str = Field("", description="Raw GnuCash split reconciliation state code")
    amount: str = Field(..., description="Split amount as decimal string")
    currency: str = Field(..., description="ISO 4217 currency code")


class TransactionDirectionEntryDTO(BaseModel):
    """One aggregated account entry in a transaction direction side."""

    account_id: str
    display_name: str
    full_name: str
    value: str = Field(..., description="Exact signed Decimal string from split.value aggregation")
    split_count: int


class TransactionDirectionDTO(BaseModel):
    """Typed From/To direction derived from signed split.value amounts."""

    status: Literal["resolved", "composite", "ambiguous"]
    reason: Literal[
        "balanced",
        "multiple_accounts",
        "no_nonzero_splits",
        "single_sided",
        "unbalanced",
        "account_on_both_sides",
    ]
    currency: str
    from_accounts: list[TransactionDirectionEntryDTO]
    to_accounts: list[TransactionDirectionEntryDTO]


def default_transaction_direction() -> TransactionDirectionDTO:
    return TransactionDirectionDTO(
        status="ambiguous",
        reason="no_nonzero_splits",
        currency="XXX",
        from_accounts=[],
        to_accounts=[],
    )


class TransactionListItemDTO(BaseModel):
    """Summary of a single transaction for list views."""

    id: str = Field(..., description="Transaction GUID")
    date: str = Field(..., description="Transaction date as YYYY-MM-DD")
    description: str = Field(..., description="Transaction description")
    amount: str = Field(..., description="Amount relevant to the queried account as decimal string")
    currency: str = Field(..., description="ISO 4217 currency code")
    account_id: str = Field(..., description="The account this amount relates to")
    account_name: str = Field(..., description="Full name of the related account")
    account_display_name: str | None = Field(None, description="Compact duplicate-safe related account label")
    counter_account_name: str = Field(..., description="Full name of the counter account or 'Split transaction'")
    direction: TransactionDirectionDTO = Field(default_factory=default_transaction_direction, description="Split-derived typed From/To direction")
    is_write_alpha_owned: bool = Field(
        False,
        description="Safe app-metadata hint that this row was created by write-alpha; never authorizes writes by itself",
    )


class TransactionDetailDTO(BaseModel):
    """Full transaction detail with all splits."""

    id: str = Field(..., description="Transaction GUID")
    date: str = Field(..., description="Transaction date as YYYY-MM-DD")
    description: str = Field(..., description="Transaction description")
    currency: str = Field(..., description="Transaction currency ISO 4217 code")
    splits: list[TransactionSplitDTO] = Field(default_factory=list, description="All splits in this transaction")


class ScheduledTransactionRecurrenceDTO(BaseModel):
    """Raw recurrence metadata for a GnuCash scheduled transaction.

    This is intentionally not a computed next-run schedule.
    """

    period_type: str = Field("", description="Raw GnuCash recurrence period type")
    multiplier: int | None = Field(None, description="Raw GnuCash recurrence multiplier")
    period_start: str | None = Field(None, description="Raw recurrence start date as YYYY-MM-DD when available")
    weekend_adjust: str = Field("", description="Raw weekend adjustment mode when available")


class ScheduledTransactionDTO(BaseModel):
    """Safe read-only scheduled/recurring transaction summary metadata."""

    id: str = Field(..., description="Scheduled transaction GUID")
    name: str = Field("", description="Scheduled transaction name")
    enabled: bool = Field(False, description="Whether the scheduled transaction is enabled in GnuCash")
    start_date: str | None = Field(None, description="Configured schedule start date")
    end_date: str | None = Field(None, description="Configured schedule end date")
    last_occurred: str | None = Field(None, description="Last occurrence date recorded by GnuCash")
    num_occurrences: int | None = Field(None, description="Configured total occurrence count")
    remaining_occurrences: int | None = Field(None, description="Remaining occurrence count recorded by GnuCash")
    auto_create: bool = Field(False, description="Whether GnuCash is configured to auto-create instances")
    auto_notify: bool = Field(False, description="Whether GnuCash is configured to notify before creation")
    advance_create_days: int | None = Field(None, description="Configured advance creation days")
    advance_notify_days: int | None = Field(None, description="Configured advance notification days")
    instance_count: int | None = Field(None, description="Instance count recorded by GnuCash")
    has_template_account: bool = Field(False, description="Whether a template account reference is present")
    template_reference_status: str = Field(
        "not_present_redacted",
        description="Safe template-reference status only; never exposes template split/source data",
    )
    recurrence: list[ScheduledTransactionRecurrenceDTO] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)


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


class ReportingCurrencyCandidateDTO(BaseModel):
    currency: str
    distinct_transaction_count: int
    nonzero_split_count: int
    active_leaf_account_count: int
    eligible_leaf_account_count: int


class ReportingCurrencyResolutionDTO(BaseModel):
    status: Literal["ready", "setup_required"]
    source: Literal["configured", "detected", "none"]
    reason: Literal["configured_valid", "dominant_detected", "no_eligible_currency", "dominance_tie"]
    configured_currency: str | None
    configured_currency_status: Literal[
        "valid",
        "missing",
        "xxx",
        "absent",
        "template_only",
        "non_monetary",
        "inactive",
    ]
    selected_currency: str | None
    candidates: list[ReportingCurrencyCandidateDTO]
    excluded_currencies: list[str]
    non_currency_commodities_excluded: bool


def default_reporting_currency_resolution() -> ReportingCurrencyResolutionDTO:
    return ReportingCurrencyResolutionDTO(
        status="setup_required",
        source="none",
        reason="no_eligible_currency",
        configured_currency=None,
        configured_currency_status="missing",
        selected_currency=None,
        candidates=[],
        excluded_currencies=[],
        non_currency_commodities_excluded=False,
    )


class ReportSummaryDTO(BaseModel):
    """Ready dashboard summary with money totals in the resolved reporting currency."""

    status: Literal["ready"] = "ready"
    currency: str
    net_worth: str = Field(..., description="Signed Decimal string; equals assets minus natural-sign liabilities")
    assets: str = Field(..., description="Signed Decimal string asset total in the reporting currency")
    liabilities: str = Field(
        ...,
        description="Natural-sign Decimal string liability total in the reporting currency; positive means money owed",
    )
    income_this_month: str
    expenses_this_month: str
    as_of_date: str
    reporting_basis: str = "base_currency_only"
    includes_currency_conversion: bool = False
    limitations: list[str] = Field(default_factory=list)
    reporting_currency: ReportingCurrencyResolutionDTO = Field(default_factory=default_reporting_currency_resolution)


class ReportSummarySetupDTO(BaseModel):
    """Setup-required dashboard summary without money total fields."""

    status: Literal["setup_required"] = "setup_required"
    as_of_date: str
    reporting_basis: Literal["base_currency_only"] = "base_currency_only"
    includes_currency_conversion: bool = False
    limitations: list[str] = Field(default_factory=list)
    reporting_currency: ReportingCurrencyResolutionDTO = Field(default_factory=default_reporting_currency_resolution)


class PeriodReportSummaryDTO(BaseModel):
    """Balance-only summary for an arbitrary period report.

    Period income/expense totals live in the cashflow section. This avoids
    exposing dashboard-only income_this_month/expenses_this_month fields on an
    arbitrary date-range response.
    """

    currency: str
    net_worth: str = Field(..., description="Signed Decimal string; equals assets minus natural-sign liabilities")
    assets: str = Field(..., description="Signed Decimal string asset total in the reporting currency")
    liabilities: str = Field(
        ...,
        description="Natural-sign Decimal string liability total in the reporting currency; positive means money owed",
    )
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


class PeriodReportSectionStatusDTO(BaseModel):
    """Per-section status for an aggregate period report."""

    section: Literal["summary", "cashflow", "monthly_cashflow", "expenses_by_account"]
    status: Literal["ok", "empty", "error"]
    detail: str | None = Field(
        None,
        description="User-safe error detail for failed sections; never includes paths or internals.",
    )


class PeriodReportDTO(BaseModel):
    """Combined read-only period report for one book and date range.

    The report is explicit about its base-currency-only basis. Section statuses
    distinguish genuine empty results from partial read failures.
    """

    book_id: int
    date_from: str
    date_to: str
    currency: str
    reporting_basis: Literal["base_currency_only"] = "base_currency_only"
    includes_currency_conversion: bool = False
    limitations: list[str] = Field(default_factory=list)
    partial_failure: bool = False
    empty: bool = False
    section_statuses: list[PeriodReportSectionStatusDTO] = Field(default_factory=list)
    summary: PeriodReportSummaryDTO | None = None
    cashflow: CashflowDTO | None = None
    monthly_cashflow: list[CashflowPeriodDTO] = Field(default_factory=list)
    expenses_by_account: list[ExpenseByAccountDTO] = Field(default_factory=list)


class ReportMoneyDeltaDTO(BaseModel):
    """Signed Decimal-string delta for one comparable money field."""

    currency: str
    primary: str
    comparison: str
    delta: str = Field(..., description="primary minus comparison as a signed Decimal string")
    absolute_delta: str = Field(..., description="Absolute value of delta as a Decimal string")


class ReportSummaryComparisonDeltaDTO(BaseModel):
    """Comparable balance-summary deltas between two period reports."""

    currency: str
    net_worth: ReportMoneyDeltaDTO
    assets: ReportMoneyDeltaDTO
    liabilities: ReportMoneyDeltaDTO = Field(
        ..., description="Delta over natural-sign liability display values; positive delta means liabilities increased"
    )


class CashflowComparisonDeltaDTO(BaseModel):
    """Comparable cashflow deltas between two period reports."""

    currency: str
    inflow: ReportMoneyDeltaDTO
    outflow: ReportMoneyDeltaDTO
    net: ReportMoneyDeltaDTO


class ExpenseAccountComparisonDeltaDTO(BaseModel):
    """Comparable or explicitly non-comparable expense-account delta row."""

    account_id: str
    account_name: str
    currency: str
    primary_total: str
    comparison_total: str
    delta: str | None = None
    absolute_delta: str | None = None
    status: Literal["ok", "not_comparable"] = "ok"
    detail: str | None = Field(
        None,
        description="User-safe reason when this row is not comparable; never includes paths or internals.",
    )


class ReportComparisonSectionStatusDTO(BaseModel):
    """Per-delta-section status for a period comparison report."""

    section: Literal["summary", "cashflow", "expenses_by_account"]
    status: Literal["ok", "empty", "error", "not_comparable"]
    detail: str | None = Field(
        None,
        description="User-safe status detail for failed or non-comparable sections.",
    )


class ReportComparisonDeltaDTO(BaseModel):
    """Typed deltas derived from two read-only period reports."""

    currency: str
    reporting_basis: Literal["base_currency_only"] = "base_currency_only"
    includes_currency_conversion: bool = False
    comparable: bool = False
    partial_failure: bool = False
    section_statuses: list[ReportComparisonSectionStatusDTO] = Field(default_factory=list)
    summary: ReportSummaryComparisonDeltaDTO | None = None
    cashflow: CashflowComparisonDeltaDTO | None = None
    expenses_by_account: list[ExpenseAccountComparisonDeltaDTO] = Field(default_factory=list)


class PeriodReportComparisonDTO(BaseModel):
    """Read-only comparison of two explicit period reports for one book."""

    book_id: int
    comparison_mode: Literal["previous_equivalent", "same_period_last_year", "custom"]
    reporting_basis: Literal["base_currency_only"] = "base_currency_only"
    includes_currency_conversion: bool = False
    primary: PeriodReportDTO
    comparison: PeriodReportDTO
    limitations: list[str] = Field(default_factory=list)
    comparable: bool = False
    partial_failure: bool = False
    empty: bool = False
    delta_section_statuses: list[ReportComparisonSectionStatusDTO] = Field(default_factory=list)
    summary_delta: ReportSummaryComparisonDeltaDTO | None = None
    cashflow_delta: CashflowComparisonDeltaDTO | None = None
    expense_changes: list[ExpenseAccountComparisonDeltaDTO] = Field(default_factory=list)


class PaginatedResponse(BaseModel):
    """Generic paginated response wrapper."""

    items: list = Field(default_factory=list)
    limit: int = 50
    offset: int = 0
    total: int = 0
