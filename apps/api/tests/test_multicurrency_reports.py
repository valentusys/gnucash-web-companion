"""Integration tests for multi-currency report filtering using a real synthetic fixture.

These tests validate that report endpoints correctly exclude accounts and splits
whose commodity does not match the book's base currency (SEK). No fake currency
conversion is performed.

Fixture: tests/fixtures/test-book-multicurrency.gnucash.sqlite
    - Base currency: SEK
    - 10 SEK accounts (Assets, Bank, Checking, Expenses, Food, Transport,
      Income, Salary, Liabilities, Credit Card)
    - 3 EUR accounts (EUR Income, EUR Expenses, EUR Travel)
    - 5 SEK transactions + 1 EUR transaction (Paris hotel)
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.services.gnucash_book import GnuCashBookService

FIXTURE_PATH = str(
    Path(__file__).resolve().parent / "fixtures" / "test-book-multicurrency.gnucash.sqlite"
)


@pytest.fixture
def svc():
    """Return a GnuCashBookService configured for the multi-currency fixture."""
    return GnuCashBookService({"uri_or_path": FIXTURE_PATH, "base_currency": "SEK"})


# --- Account listing (not filtered by currency) ---

class TestMultiCurrencyAccountListing:
    def test_all_accounts_included(self, svc):
        """GET /accounts equivalent: list_accounts returns all 13 accounts regardless of currency."""
        accounts = svc.list_accounts()
        assert len(accounts) == 13

    def test_sek_accounts_present(self, svc):
        """All 10 SEK accounts are present."""
        accounts = svc.list_accounts()
        sek_accounts = [a for a in accounts if a.currency == "SEK"]
        assert len(sek_accounts) == 10

    def test_eur_accounts_present(self, svc):
        """All 3 EUR accounts are present."""
        accounts = svc.list_accounts()
        eur_accounts = [a for a in accounts if a.currency == "EUR"]
        assert len(eur_accounts) == 3
        eur_names = {a.name for a in eur_accounts}
        assert "EUR Income" in eur_names
        assert "EUR Expenses" in eur_names
        assert "EUR Travel" in eur_names


# --- Summary report (excludes non-base-currency accounts) ---

class TestMultiCurrencyReportSummary:
    def test_summary_excludes_eur_accounts_from_assets(self, svc):
        """Report summary assets include only SEK accounts; EUR accounts are excluded."""
        report = svc.get_report_summary()
        # Same as single-currency fixture: Assets (2729.50) + Expenses (1020.50) + Income (5000.00) = 8188.50
        assert report.assets == "8188.50"
        assert report.currency == "SEK"

    def test_summary_excludes_eur_from_liabilities(self, svc):
        """Report summary liabilities include only SEK accounts."""
        report = svc.get_report_summary()
        assert report.liabilities == "-2500.00"

    def test_summary_net_worth_excludes_eur(self, svc):
        """Net worth is based on SEK accounts only."""
        report = svc.get_report_summary()
        assert report.net_worth == "5688.50"

    def test_summary_income_excludes_eur(self, svc):
        """Income this month excludes EUR income."""
        report = svc.get_report_summary("2026-02-28")
        # Feb has no SEK income transactions
        assert report.income_this_month == "0.00"

    def test_summary_expenses_excludes_eur(self, svc):
        """Expenses this month excludes EUR expenses."""
        report = svc.get_report_summary("2026-02-28")
        # Feb SEK expenses: Bus pass (150) + Monthly expenses splits (350+200) = 700
        assert report.expenses_this_month == "-700.00"

    def test_summary_reports_base_currency_only_no_conversion_basis(self, svc):
        """Dashboard summary metadata must not imply converted multi-currency totals."""
        report = svc.get_report_summary("2026-02-28")

        assert report.reporting_basis == "base_currency_only"
        assert report.includes_currency_conversion is False
        limitations = " ".join(report.limitations)
        assert "reporting_basis=base_currency_only" in limitations
        assert "no currency conversion" in limitations
        assert "EUR" in limitations
        assert "excluded rather than converted or combined" in limitations

    def test_summary_unknown_base_currency_limitations_explain_zero_totals(self):
        """Unknown base-currency summaries must explain XXX/zero-total limitations."""
        unknown_base_svc = GnuCashBookService({"uri_or_path": FIXTURE_PATH, "base_currency": None})

        report = unknown_base_svc.get_report_summary("2026-02-28")

        assert report.currency == "XXX"
        assert report.reporting_basis == "base_currency_only"
        assert report.includes_currency_conversion is False
        assert report.assets == "0.00"
        assert report.liabilities == "0.00"
        limitations = " ".join(report.limitations)
        assert "unknown (XXX)" in limitations
        assert "zero totals may mean no matching base-currency accounts" in limitations
        assert "rather than an empty book" in limitations
        assert "no currency conversion" in limitations


# --- Cashflow report (excludes non-base-currency splits) ---

class TestMultiCurrencyCashflow:
    def test_cashflow_excludes_eur_splits(self, svc):
        """Cashflow for Q1 2026 excludes EUR transaction splits."""
        cashflow = svc.get_cashflow("2026-01-01", "2026-03-31")
        # Same as single-currency fixture
        assert cashflow.inflow == "5000.00"
        assert cashflow.outflow == "1020.50"
        assert cashflow.net == "3979.50"
        assert cashflow.currency == "SEK"

    def test_cashflow_february_excludes_eur(self, svc):
        """Cashflow for Feb 2026 excludes EUR Paris hotel transaction."""
        cashflow = svc.get_cashflow("2026-02-01", "2026-02-28")
        # Feb: bus pass (150) + monthly expenses (350+200) = 700 outflow, 0 inflow
        assert cashflow.inflow == "0.00"
        assert cashflow.outflow == "700.00"
        assert cashflow.net == "-700.00"


# --- Expenses by account (excludes non-base-currency accounts) ---

class TestMultiCurrencyExpensesByAccount:
    def test_expenses_exclude_eur_accounts(self, svc):
        """Expenses-by-account excludes EUR expense accounts."""
        expenses = svc.get_expenses_by_account("2026-01-01", "2026-03-31")
        # Should only have SEK expense accounts
        for expense in expenses:
            assert expense.currency == "SEK"

    def test_expenses_only_sek_accounts(self, svc):
        """Only SEK expense accounts appear in expenses-by-account."""
        expenses = svc.get_expenses_by_account("2026-01-01", "2026-03-31")
        account_names = {e.account_name for e in expenses}
        assert "Expenses:Food" in account_names
        assert "Expenses:Transport" in account_names
        # EUR Travel must NOT be present
        assert "EUR Expenses:EUR Travel" not in account_names

    def test_expenses_eur_travel_excluded(self, svc):
        """EUR Travel expense (120 EUR) is excluded from SEK expenses report."""
        expenses = svc.get_expenses_by_account("2026-02-01", "2026-02-28")
        account_names = {e.account_name for e in expenses}
        assert "EUR Travel" not in account_names
        # Feb SEK expenses: Transport (150+200) + Food (350)
        for expense in expenses:
            assert expense.currency == "SEK"
