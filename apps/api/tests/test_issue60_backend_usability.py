"""Issue #60 backend usability contract tests over a generated real GnuCash book."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.routers.transactions import _resolve_general_preview_accounts
from app.services.gnucash_book import GnuCashBookService
from app.services.gnucash_exceptions import EntityNotFoundError
from app.services.transaction_direction import build_transaction_direction
from app.services.transaction_create_errors import TransactionCreateHTTPError
from tests.support.generate_issue60_usability_fixture import (
    BASE_CURRENCY,
    SECONDARY_CURRENCY,
    generate_issue60_usability_fixture,
    sha256_file,
)


def test_issue60_fixture_is_fixed_seed_readonly_source_and_disposable_copy(tmp_path: Path):
    first = generate_issue60_usability_fixture(tmp_path / "first")
    second = generate_issue60_usability_fixture(tmp_path / "second")

    assert first.source_hash == second.source_hash
    assert first.target_hash_before == first.source_hash
    assert second.target_hash_before == second.source_hash
    assert sha256_file(first.source_path) == first.source_hash
    assert first.source_path.is_relative_to(tmp_path)
    assert first.target_path.is_relative_to(tmp_path)
    assert first.source_path != first.target_path
    assert not (first.source_path.stat().st_mode & 0o222)
    assert first.target_path.stat().st_mode & 0o200
    assert first.expected["source_create_count"] == 1
    assert first.expected["disposable_copy_count"] == 1
    assert first.expected["target_create_count"] == 0
    assert first.expected["target_patch_count"] == 0
    assert first.expected["target_delete_count"] == 0
    assert first.expected["owner_private_access_count"] == 0


def test_issue60_reporting_currency_uses_detected_dominant_currency_not_xxx_or_fx(tmp_path: Path):
    fixture = generate_issue60_usability_fixture(tmp_path / "issue60")
    service = GnuCashBookService({"uri_or_path": str(fixture.source_path), "base_currency": None})

    summary = service.get_report_summary("2026-07-31")

    assert summary.status == "ready"
    assert summary.currency == BASE_CURRENCY
    assert summary.reporting_basis == "base_currency_only"
    assert summary.includes_currency_conversion is False
    assert summary.reporting_currency.status == "ready"
    assert summary.reporting_currency.source == "detected"
    assert summary.reporting_currency.reason == "dominant_detected"
    assert summary.reporting_currency.configured_currency is None
    assert summary.reporting_currency.configured_currency_status == "missing"
    assert summary.reporting_currency.selected_currency == BASE_CURRENCY
    assert summary.reporting_currency.excluded_currencies == [SECONDARY_CURRENCY]
    assert summary.reporting_currency.non_currency_commodities_excluded is True
    candidates = {candidate.currency: candidate for candidate in summary.reporting_currency.candidates}
    assert set(candidates) == {BASE_CURRENCY, SECONDARY_CURRENCY}
    assert candidates[BASE_CURRENCY].distinct_transaction_count > candidates[SECONDARY_CURRENCY].distinct_transaction_count
    assert "XXX" not in {summary.currency, summary.reporting_currency.selected_currency}


def test_issue60_visibility_hides_canonical_roots_templates_but_not_template_named_user_account(tmp_path: Path):
    fixture = generate_issue60_usability_fixture(tmp_path / "issue60")
    service = GnuCashBookService({"uri_or_path": str(fixture.source_path), "base_currency": BASE_CURRENCY})

    accounts = service.list_accounts()
    ids = {account.id for account in accounts}
    names = {account.name for account in accounts}
    display_by_full_name = {account.full_name: account.display_name for account in accounts}

    assert fixture.accounts["root"]["id"] not in ids
    assert fixture.accounts["template_root"]["id"] not in ids
    assert fixture.accounts["template_checking"]["id"] not in ids
    assert fixture.accounts["template_food"]["id"] not in ids
    assert all(account.type != "ROOT" for account in accounts)
    assert "Root Account" not in names
    assert fixture.accounts["visible_template_named"]["id"] in ids
    assert display_by_full_name["Активы:Банки:Сбербанк"] == "Сбербанк — Банки"
    assert display_by_full_name["Активы:Бизнес:Сбербанк"] == "Сбербанк — Бизнес"
    assert not any(account.id in (account.display_name or "") for account in accounts)

    with pytest.raises(EntityNotFoundError):
        service.get_account(fixture.accounts["root"]["id"])
    with pytest.raises(EntityNotFoundError):
        service.get_account(fixture.accounts["template_checking"]["id"])
    with pytest.raises(EntityNotFoundError):
        service.get_transaction(fixture.transactions["template_hidden"])


def test_issue60_latest_transactions_expose_split_value_direction_cases(tmp_path: Path):
    fixture = generate_issue60_usability_fixture(tmp_path / "issue60")
    service = GnuCashBookService({"uri_or_path": str(fixture.source_path), "base_currency": BASE_CURRENCY})

    rows = {item.id: item for item in service.list_transactions(limit=50)}
    assert fixture.transactions["template_hidden"] not in rows

    building = rows[fixture.transactions["building"]].direction
    assert building.status == "resolved"
    assert building.reason == "balanced"
    assert [(entry.display_name, entry.value) for entry in building.from_accounts] == [("Сбербанк — Банки", "-1000")]
    assert [(entry.display_name, entry.value) for entry in building.to_accounts] == [("Строительство", "1000")]

    three_split = rows[fixture.transactions["three_split"]].direction
    assert three_split.status == "composite"
    assert three_split.reason == "multiple_accounts"
    assert [entry.display_name for entry in three_split.from_accounts] == ["ВТБ"]
    assert [entry.display_name for entry in three_split.to_accounts] == ["Продукты", "Транспорт"]

    repeated = rows[fixture.transactions["repeated"]].direction
    assert repeated.status == "resolved"
    assert repeated.to_accounts[0].display_name == "Продукты"
    assert repeated.to_accounts[0].value == "200"
    assert repeated.to_accounts[0].split_count == 2

    zero = rows[fixture.transactions["zero"]].direction
    assert zero.status == "resolved"
    assert {entry.display_name for entry in zero.from_accounts + zero.to_accounts} == {"Сбербанк — Банки", "Транспорт"}

    ambiguous = rows[fixture.transactions["same_account_both_sides"]].direction
    assert ambiguous.status == "ambiguous"
    assert ambiguous.reason == "account_on_both_sides"
    assert [entry.display_name for entry in ambiguous.from_accounts] == ["Сбербанк — Банки"]
    assert [entry.display_name for entry in ambiguous.to_accounts] == ["Сбербанк — Банки"]

    empty_description = rows[fixture.transactions["empty_description"]]
    assert empty_description.description == ""
    assert empty_description.direction.status == "resolved"


def test_issue60_direction_entry_values_preserve_exact_decimal_strings():
    currency = SimpleNamespace(mnemonic=BASE_CURRENCY)
    source = SimpleNamespace(guid="a" * 32, name="Source", commodity=currency)
    destination = SimpleNamespace(guid="b" * 32, name="Destination", commodity=currency)
    transaction = SimpleNamespace(
        currency=currency,
        splits=[
            SimpleNamespace(account=source, value=Decimal("-1.2345")),
            SimpleNamespace(account=destination, value=Decimal("1.2345")),
        ],
    )

    direction = build_transaction_direction(transaction, fallback_currency=BASE_CURRENCY)

    assert direction.status == "resolved"
    assert direction.reason == "balanced"
    assert [entry.value for entry in direction.from_accounts] == ["-1.2345"]
    assert [entry.value for entry in direction.to_accounts] == ["1.2345"]


def test_issue60_create_validation_rejects_root_template_and_placeholder_accounts(tmp_path: Path):
    fixture = generate_issue60_usability_fixture(tmp_path / "issue60")
    service = GnuCashBookService({"uri_or_path": str(fixture.source_path), "base_currency": BASE_CURRENCY})
    accounts = service.list_accounts_by_ids(
        [
            fixture.accounts["root"]["id"],
            fixture.accounts["template_checking"]["id"],
            fixture.accounts["assets"]["id"],
            fixture.accounts["sber"]["id"],
        ]
    )
    by_id = {account.id: account for account in accounts}

    assert by_id[fixture.accounts["root"]["id"]].ordinary_visibility_excluded is True
    assert by_id[fixture.accounts["root"]["id"]].ordinary_visibility_reason == "root"
    assert by_id[fixture.accounts["template_checking"]["id"]].ordinary_visibility_excluded is True
    assert by_id[fixture.accounts["template_checking"]["id"]].ordinary_visibility_reason == "template"
    assert by_id[fixture.accounts["assets"]["id"]].placeholder is True
    assert by_id[fixture.accounts["sber"]["id"]].ordinary_visibility_excluded is False

    normalized = {
        "currency": BASE_CURRENCY,
        "splits": [
            {"account_id": fixture.accounts["root"]["id"], "amount": "-1.00"},
            {"account_id": fixture.accounts["sber"]["id"], "amount": "1.00"},
        ],
    }
    with pytest.raises(TransactionCreateHTTPError) as root_error:
        _resolve_general_preview_accounts(normalized, accounts)
    assert root_error.value.code == "ACCOUNT_NOT_POSTABLE"
    assert root_error.value.field_path == "splits[0].account_id"

    normalized["splits"][0]["account_id"] = fixture.accounts["template_checking"]["id"]
    with pytest.raises(TransactionCreateHTTPError) as template_error:
        _resolve_general_preview_accounts(normalized, accounts)
    assert template_error.value.code == "ACCOUNT_NOT_POSTABLE"

    normalized["splits"][0]["account_id"] = fixture.accounts["assets"]["id"]
    with pytest.raises(TransactionCreateHTTPError) as placeholder_error:
        _resolve_general_preview_accounts(normalized, accounts)
    assert placeholder_error.value.code == "ACCOUNT_NOT_POSTABLE"
