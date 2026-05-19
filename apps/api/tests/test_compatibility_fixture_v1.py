"""Phase 46 compatibility fixture v1 tests.

These tests validate a generated disposable GnuCash SQLite fixture through the
same read-only service layer used by the API. The fixture is synthetic and is
created in pytest's tmp_path, so no binary GnuCash book is committed.
"""

from __future__ import annotations

import importlib.util
import json
import shutil
from pathlib import Path
from types import ModuleType

import pytest

from app.services.gnucash_book import GnuCashBookService


def _load_generator() -> ModuleType:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "create_compatibility_fixture_v1.py"
    spec = importlib.util.spec_from_file_location("create_compatibility_fixture_v1", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _load_desktop_tooling_probe() -> ModuleType:
    script_path = Path(__file__).resolve().parents[1] / "scripts" / "probe_gnucash_desktop_tooling.py"
    spec = importlib.util.spec_from_file_location("probe_gnucash_desktop_tooling", script_path)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


_generator = _load_generator()
FIXTURE_ID = _generator.FIXTURE_ID
create_fixture = _generator.create_fixture
fixture_metadata = _generator.fixture_metadata
sha256_file = _generator.sha256_file


@pytest.fixture
def compatibility_fixture_path(tmp_path: Path) -> Path:
    path = tmp_path / "compatibility-v1.gnucash.sqlite"
    return create_fixture(path)


@pytest.fixture
def svc(compatibility_fixture_path: Path) -> GnuCashBookService:
    return GnuCashBookService({"uri_or_path": str(compatibility_fixture_path), "base_currency": "SEK"})


class TestCompatibilityFixtureV1Generation:
    def test_generator_creates_non_committed_fixture_with_metadata(self, compatibility_fixture_path: Path):
        assert compatibility_fixture_path.exists()
        assert "tests/fixtures" not in compatibility_fixture_path.as_posix()

        metadata = fixture_metadata(compatibility_fixture_path)
        assert metadata["fixture_id"] == FIXTURE_ID
        assert metadata["format"] == "GnuCash SQLite"
        assert metadata["base_currency"] == "SEK"
        assert metadata["contains_real_data"] is False
        assert metadata["desktop_version"] == "not desktop-generated in Phase 46 v1"
        assert metadata["account_count_expected"] == 15
        assert metadata["transaction_count_expected"] == 9
        assert metadata["runtime_context"]["generator_version"] == "phase-102"
        assert metadata["runtime_context"]["python_version"]
        assert metadata["runtime_context"]["sqlite_version"]
        assert metadata["runtime_context"]["piecash_version"]
        assert metadata["sha256"] == sha256_file(compatibility_fixture_path)
        assert metadata["versions"]["Gnucash"] >= 3000000

    def test_desktop_tooling_absence_is_safe_blocker_not_desktop_evidence(self, monkeypatch):
        probe = _load_desktop_tooling_probe()
        monkeypatch.setattr(probe.shutil, "which", lambda command: None)

        metadata = probe.probe_tooling()
        serialized = json.dumps(metadata, sort_keys=True)

        assert metadata["desktop_tooling_available"] is False
        assert metadata["commands"]["gnucash"]["available"] is False
        assert metadata["commands"]["gnucash-cli"]["available"] is False
        assert metadata["safe_next_step"].startswith("Install or provide GnuCash Desktop/CLI")
        assert "version_output" not in metadata["commands"]["gnucash"]
        assert "/home" not in serialized
        assert "<redacted>" not in serialized

    def test_read_only_service_does_not_mutate_fixture(self, compatibility_fixture_path: Path):
        before = sha256_file(compatibility_fixture_path)
        service = GnuCashBookService({"uri_or_path": str(compatibility_fixture_path), "base_currency": "SEK"})

        assert service.check_connection() is True
        service.list_accounts()
        service.list_transactions(limit=100)
        service.get_report_summary("2024-01-31")

        after = sha256_file(compatibility_fixture_path)
        assert after == before


class TestCompatibilityFixtureV1ReadOnlyCoverage:
    def test_account_tree_matches_fixture_model(self, svc: GnuCashBookService):
        accounts = svc.list_accounts()
        assert len(accounts) == 15
        assert {account.currency for account in accounts} == {"SEK"}

        names_by_type = {(account.name, account.type) for account in accounts}
        assert ("Checking", "BANK") in names_by_type
        assert ("Savings", "BANK") in names_by_type
        assert ("Cash", "CASH") in names_by_type
        assert ("Credit Card", "CREDIT") in names_by_type
        assert ("Opening Balances", "EQUITY") in names_by_type

        tree = svc.get_account_tree()
        assert {node.name for node in tree} == {
            "Assets",
            "Liabilities",
            "Income",
            "Expenses",
            "Equity",
        }
        assets = next(node for node in tree if node.name == "Assets")
        assert {child.name for child in assets.children} == {"Checking", "Savings", "Cash"}

    def test_transaction_list_has_expected_synthetic_transactions(self, svc: GnuCashBookService):
        transactions = svc.list_transactions(limit=100)
        assert len(transactions) == 9
        assert [tx.date for tx in transactions] == sorted(
            [tx.date for tx in transactions], reverse=True
        )
        descriptions = {tx.description for tx in transactions}
        assert descriptions == {
            "Fixture opening checking",
            "Fixture opening savings",
            "Fixture salary",
            "Fixture interest",
            "Fixture grocery",
            "Fixture monthly split",
            "Fixture transfer to cash",
            "Fixture credit card cycle",
            "Fixture credit card payment",
        }
        assert all(description.startswith("Fixture ") for description in descriptions)

    def test_split_transaction_detail_is_readable(self, svc: GnuCashBookService):
        split_tx = next(
            tx for tx in svc.list_transactions(limit=100) if tx.description == "Fixture monthly split"
        )
        detail = svc.get_transaction(split_tx.id)

        assert detail.description == "Fixture monthly split"
        assert detail.currency == "SEK"
        assert len(detail.splits) == 4
        split_accounts = {split.account_name for split in detail.splits}
        assert "Assets:Checking" in split_accounts
        assert "Expenses:Groceries" in split_accounts
        assert "Expenses:Utilities" in split_accounts
        assert "Expenses:Travel" in split_accounts

    def test_reports_basic_values_are_available(self, svc: GnuCashBookService):
        summary = svc.get_summary()
        assert summary.account_count == 15
        assert summary.transaction_count == 9
        assert summary.currency == "SEK"

        report = svc.get_report_summary("2024-01-31")
        assert report.currency == "SEK"
        assert report.assets == "10937.78"
        assert report.liabilities == "0.00"
        assert report.net_worth == "10937.78"
        assert report.income_this_month == "3012.34"
        assert report.expenses_this_month == "-543.45"

    def test_generated_fixture_copy_can_be_loaded_from_documented_path(
        self, compatibility_fixture_path: Path, tmp_path: Path
    ):
        copied = tmp_path / "documented-manual-copy.gnucash.sqlite"
        shutil.copy2(compatibility_fixture_path, copied)

        copied_service = GnuCashBookService({"uri_or_path": str(copied), "base_currency": "SEK"})
        assert copied_service.check_connection() is True
        assert copied_service.get_summary().transaction_count == 9
