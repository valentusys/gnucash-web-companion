"""Integration tests for the read-only GnuCash service layer using a real synthetic fixture.

These tests validate GnuCashBookService against an actual piecash-opened SQLite book,
exercising the full read-only path with real SQL data instead of Python fakes.

Fixture: tests/fixtures/test-book.gnucash.sqlite (synthetic data, SEK only).
"""

from __future__ import annotations

from pathlib import Path

import pytest

from app.services.gnucash_book import GnuCashBookService
from app.services.gnucash_exceptions import BookNotFoundError

FIXTURE_PATH = str(Path(__file__).resolve().parent / "fixtures" / "test-book.gnucash.sqlite")


@pytest.fixture
def svc():
    """Return a GnuCashBookService configured for the synthetic fixture."""
    return GnuCashBookService({"uri_or_path": FIXTURE_PATH, "base_currency": "SEK"})


# --- Connection ---

class TestFixtureConnection:
    def test_fixture_connection(self, svc):
        """check_connection() returns True for the synthetic fixture."""
        assert svc.check_connection() is True


# --- Account tree ---

class TestFixtureAccountTree:
    def test_fixture_account_tree(self, svc):
        """Full account tree has correct structure and count."""
        accounts = svc.list_accounts()
        # piecash book.accounts has 10 non-ROOT accounts.
        # The ROOT account (book.root_account) is NOT in book.accounts,
        # so the service layer returns 10 accounts (no ROOT type).
        assert len(accounts) == 10

        # Verify all accounts have SEK currency
        for account in accounts:
            assert account.currency == "SEK"

        # Verify account types present (ROOT is not in the list)
        types = {a.type for a in accounts}
        assert "ASSET" in types
        assert "BANK" in types
        assert "EXPENSE" in types
        assert "INCOME" in types
        assert "LIABILITY" in types

        # Verify tree structure: 4 top-level roots
        # ROOT is not in _accounts(), so Assets/Expenses/Income/Liabilities
        # have parent_id pointing to ROOT's guid which is NOT in the nodes dict,
        # making them all root nodes.
        tree = svc.get_account_tree()
        assert len(tree) == 4

        tree_ids = {node.id: node for node in tree}

        # Each top-level node has the expected children
        assets = tree_ids[next(n.id for n in tree if n.name == "Assets")]
        expenses = tree_ids[next(n.id for n in tree if n.name == "Expenses")]
        income = tree_ids[next(n.id for n in tree if n.name == "Income")]
        liabilities = tree_ids[next(n.id for n in tree if n.name == "Liabilities")]

        assert len(assets.children) == 1  # Bank
        assert assets.children[0].name == "Bank"
        assert len(assets.children[0].children) == 1  # Checking
        assert assets.children[0].children[0].name == "Checking"

        assert len(expenses.children) == 2  # Food, Transport
        child_names = {c.name for c in expenses.children}
        assert child_names == {"Food", "Transport"}

        assert len(income.children) == 1  # Salary
        assert income.children[0].name == "Salary"

        assert len(liabilities.children) == 1  # Credit Card
        assert liabilities.children[0].name == "Credit Card"


# --- Account balances ---

class TestFixtureAccountBalances:
    def test_fixture_checking_balance(self, svc):
        """Checking balance == 2729.50 (5000 - 320.50 - 150 - 800 - 1000)."""
        accounts = svc.list_accounts()
        checking = next(a for a in accounts if a.name == "Checking")
        assert checking.balance == "2729.50"

    def test_fixture_food_balance(self, svc):
        """Food balance == 670.50 (320.50 + 350)."""
        accounts = svc.list_accounts()
        food = next(a for a in accounts if a.name == "Food")
        assert food.balance == "670.50"

    def test_fixture_salary_balance(self, svc):
        """Salary balance == 5000.00 (income account, positive in piecash convention)."""
        accounts = svc.list_accounts()
        salary = next(a for a in accounts if a.name == "Salary")
        assert salary.balance == "5000.00"

    def test_fixture_transport_balance(self, svc):
        """Transport balance == 350.00 (150 + 200)."""
        accounts = svc.list_accounts()
        transport = next(a for a in accounts if a.name == "Transport")
        assert transport.balance == "350.00"

    def test_fixture_credit_card_balance(self, svc):
        """Credit Card balance == -1250.00 (liability, negative in piecash convention)."""
        accounts = svc.list_accounts()
        cc = next(a for a in accounts if a.name == "Credit Card")
        assert cc.balance == "-1250.00"


# --- Transaction list ---

class TestFixtureTransactionList:
    def test_fixture_transaction_count(self, svc):
        """5 transactions returned."""
        transactions = svc.list_transactions()
        assert len(transactions) == 5

    def test_fixture_transaction_sort_order(self, svc):
        """Transactions sorted by date descending (newest first)."""
        transactions = svc.list_transactions()
        dates = [t.date for t in transactions]
        assert dates == sorted(dates, reverse=True)
        # Newest: 2026-03-01, oldest: 2026-01-15
        assert dates[0] == "2026-03-01"
        assert dates[-1] == "2026-01-15"

    def test_fixture_transaction_descriptions(self, svc):
        """All 5 expected descriptions are present."""
        transactions = svc.list_transactions()
        descriptions = {t.description for t in transactions}
        expected = {
            "January salary",
            "Grocery store",
            "Bus pass",
            "Monthly expenses",
            "Credit card payment",
        }
        assert descriptions == expected


# --- Transaction detail ---

class TestFixtureTransactionDetail:
    def test_fixture_multi_split_detail(self, svc):
        """Multi-split transaction (Monthly expenses) has 4 splits."""
        transactions = svc.list_transactions()
        multi_tx = next(t for t in transactions if t.description == "Monthly expenses")
        detail = svc.get_transaction(multi_tx.id)
        assert detail.description == "Monthly expenses"
        assert len(detail.splits) == 4
        # Verify split accounts
        split_accounts = {s.account_name for s in detail.splits}
        assert "Assets:Bank:Checking" in split_accounts
        assert "Expenses:Food" in split_accounts
        assert "Expenses:Transport" in split_accounts
        assert "Liabilities:Credit Card" in split_accounts

    def test_fixture_two_split_detail(self, svc):
        """Two-split transaction (January salary) has 2 splits."""
        transactions = svc.list_transactions()
        salary_tx = next(t for t in transactions if t.description == "January salary")
        detail = svc.get_transaction(salary_tx.id)
        assert len(detail.splits) == 2
        assert detail.currency == "SEK"


# --- Summary ---

class TestFixtureSummary:
    def test_fixture_summary(self, svc):
        """Summary: 10 accounts, 5 transactions, currency SEK."""
        summary = svc.get_summary()
        assert summary.account_count == 10
        assert summary.transaction_count == 5
        assert summary.currency == "SEK"


# --- Cashflow ---

class TestFixtureCashflow:
    def test_fixture_cashflow_january(self, svc):
        """Cashflow for Jan 2026: salary inflow, grocery outflow."""
        cashflow = svc.get_cashflow("2026-01-01", "2026-01-31")
        assert cashflow.inflow == "5000.00"
        assert cashflow.outflow == "320.50"
        assert cashflow.net == "4679.50"
        assert cashflow.currency == "SEK"

    def test_fixture_cashflow_february(self, svc):
        """Cashflow for Feb 2026: bus pass + monthly expenses outflow."""
        cashflow = svc.get_cashflow("2026-02-01", "2026-02-28")
        assert cashflow.inflow == "0.00"
        assert cashflow.outflow == "700.00"
        assert cashflow.net == "-700.00"

    def test_fixture_cashflow_full_range(self, svc):
        """Cashflow for full Q1 2026 range."""
        cashflow = svc.get_cashflow("2026-01-01", "2026-03-31")
        assert cashflow.inflow == "5000.00"
        assert cashflow.outflow == "1020.50"
        assert cashflow.net == "3979.50"


# --- Report summary ---

class TestFixtureReportSummary:
    def test_fixture_report_summary(self, svc):
        """Report summary returns non-zero assets and liabilities."""
        report = svc.get_report_summary()
        # Asset/liability totals use only leaf balance-sheet accounts, avoiding
        # parent/root hierarchy double-counting.
        assert report.assets == "2729.50"
        assert report.liabilities == "-1250.00"
        assert report.currency == "SEK"

    def test_fixture_report_as_of_february(self, svc):
        """Report as of Feb 2028 shows Feb income/expenses."""
        report = svc.get_report_summary("2026-02-28")
        # Feb has no income transactions, only expenses
        assert report.income_this_month == "0.00"
        # Feb expenses: Bus pass (150) + Monthly expenses splits (350+200) = 700
        # expenses_this_month is stored as negative per the service layer convention
        assert report.expenses_this_month == "-700.00"


# --- Error handling ---

class TestFixtureErrors:
    def test_fixture_missing_book_error(self, svc):
        """Non-existent path raises BookNotFoundError."""
        bad_svc = GnuCashBookService({
            "uri_or_path": "/nonexistent/path/book.gnucash.sqlite",
            "base_currency": "SEK",
        })
        with pytest.raises(BookNotFoundError):
            bad_svc.check_connection()
