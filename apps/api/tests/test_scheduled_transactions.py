"""Tests for read-only scheduled transaction awareness API endpoints."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
from typing import Any

from app.models import Book
from tests.test_transactions import (  # noqa: F401 - re-export fixtures for pytest
    auth_headers,
    auth_token,
    client,
    engine,
    sample_book,
    session_factory,
)


@dataclass
class FakeRecurrence:
    id: int = 0
    obj_guid: str = ""
    recurrence_period_type: str = "month"
    recurrence_mult: int = 1
    recurrence_period_start: date = date(2026, 6, 1)
    recurrence_weekend_adjust: str = "none"


@dataclass
class FakeScheduledTransaction:
    guid: str
    name: str
    enabled: bool = True
    start_date: date = date(2026, 6, 1)
    end_date: date | None = None
    last_occur: date | None = date(2026, 5, 1)
    num_occur: int | None = None
    rem_occur: int | None = None
    auto_create: bool = False
    auto_notify: bool = True
    adv_creation: int = 0
    adv_notify: int = 7
    instance_count: int = 0
    template_act_guid: str | None = "template-account-guid"
    template_account: Any | None = None
    recurrence: list[FakeRecurrence] = field(default_factory=lambda: [FakeRecurrence()])
    # Unsafe template/source fields must never appear in the public scheduled DTO.
    template_transaction_description: str = "Private template description"
    template_split_memo: str = "Private template memo"
    template_split_amount: str = "123.45"
    template_account_name: str = "Private:Account"
    raw_sql: str = "select * from scheduled_template_splits"


class FakeBookWithScheduledTransactions:
    def __init__(self, scheduled_transactions=None):
        self.accounts = []
        self.transactions = []
        self.scheduled_transactions = scheduled_transactions or []
        self.closed = False

    def close(self):
        self.closed = True


class FakeRecurrenceQuery:
    def __init__(self, rows):
        self.rows = rows
        self.row_limit = None

    def filter(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def limit(self, value):
        self.row_limit = value
        return self

    def all(self):
        if self.row_limit is None:
            return list(self.rows)
        return list(self.rows[: self.row_limit])


class FakePiecashSession:
    def __init__(self, recurrence_rows):
        self.recurrence_rows = recurrence_rows

    def query(self, model):
        return FakeRecurrenceQuery(self.recurrence_rows)


class FakeBookWithRecurrenceRows(FakeBookWithScheduledTransactions):
    def __init__(self, scheduled_transactions, recurrence_rows):
        super().__init__(scheduled_transactions=scheduled_transactions)
        self.session = FakePiecashSession(recurrence_rows)


@dataclass
class FakeCommodity:
    mnemonic: str


class FakePrivateCurrency:
    def __str__(self):
        return "PRIVATE-CURRENCY-MARKER"


@dataclass
class FakeTemplateTransaction:
    guid: str
    currency: Any


@dataclass
class FakeFormulaValue:
    value: str


class FakeTemplateSplit:
    def __init__(self, transaction, *, debit_formula: str = "", credit_formula: str = ""):
        self.transaction = transaction
        self.formulas = {
            "credit-formula": FakeFormulaValue(credit_formula),
            "debit-formula": FakeFormulaValue(debit_formula),
        }

    def __getitem__(self, key):
        if key != "sched-xaction":
            raise KeyError(key)
        return self.formulas


@dataclass
class FakeTemplateSplitWithoutFormulaSlots:
    transaction: FakeTemplateTransaction


@dataclass
class FakeTemplateAccount:
    splits: list[Any]


def install_fake_scheduled_book(monkeypatch, tmp_path, scheduled_transactions):
    book_path = tmp_path / "scheduled.gnucash"
    book_path.write_text("fake")

    def fake_open_book(path, readonly=False):
        assert readonly is True
        return FakeBookWithScheduledTransactions(scheduled_transactions=scheduled_transactions)

    import app.services.gnucash_book as gb_module

    monkeypatch.setattr(gb_module.piecash, "open_book", fake_open_book)
    return book_path


def install_fake_scheduled_book_with_rows(
    monkeypatch,
    tmp_path,
    scheduled_transactions,
    recurrence_rows,
    *,
    opened_books=None,
):
    book_path = tmp_path / "scheduled-all-rows.gnucash"
    book_path.write_text("fake")

    def fake_open_book(path, readonly=False):
        assert readonly is True
        opened = FakeBookWithRecurrenceRows(scheduled_transactions, recurrence_rows)
        if opened_books is not None:
            opened_books.append(opened)
        return opened

    import app.services.gnucash_book as gb_module

    monkeypatch.setattr(gb_module.piecash, "open_book", fake_open_book)
    return book_path


def point_sample_book_at(session_factory, sample_book, book_path):
    with session_factory() as session:
        book = session.query(Book).filter(Book.id == sample_book).first()
        book.uri_or_path = str(book_path)
        session.commit()


def test_default_scheduled_transactions_returns_safe_summary(
    client, auth_headers, sample_book, session_factory, monkeypatch, tmp_path
):
    book_path = install_fake_scheduled_book(
        monkeypatch,
        tmp_path,
        [FakeScheduledTransaction(guid="sx-1", name="Monthly rent")],
    )
    point_sample_book_at(session_factory, sample_book, book_path)

    response = client.get("/scheduled-transactions?as_of_date=2026-06-01", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data == [
        {
            "id": "sx-1",
            "name": "Monthly rent",
            "enabled": True,
            "start_date": "2026-06-01",
            "end_date": None,
            "last_occurred": "2026-05-01",
            "num_occurrences": None,
            "remaining_occurrences": None,
            "auto_create": False,
            "auto_notify": True,
            "advance_create_days": 0,
            "advance_notify_days": 7,
            "instance_count": 0,
            "has_template_account": True,
            "template_reference_status": "present_redacted",
            "recurrence": [
                {
                    "period_type": "month",
                    "multiplier": 1,
                    "period_start": "2026-06-01",
                    "weekend_adjust": "none",
                }
            ],
            "forecast": {
                "status": "ready",
                "reason": None,
                "as_of_date": "2026-06-01",
                "next_due_date": "2026-06-01",
                "is_overdue": False,
                "upcoming_7_days": ["2026-06-01"],
                "upcoming_30_days": ["2026-06-01"],
            },
            "amount": {
                "status": "unresolved",
                "amount": None,
                "currency": None,
                "unresolved_formula_count": 0,
                "reason": "template_data_unavailable",
            },
            "new_transactions_created": 0,
            "limitations": [
                "Read-only forecast only; edit scheduled transactions in GnuCash Desktop.",
                "Forecast dates are bounded to 30 days and never materialize transactions.",
                "Template account names, memos, descriptions, formulas, and raw SQL are never exposed.",
                "A template account reference is present; only a safely resolved constant amount or a redacted unresolved state is returned.",
            ],
        }
    ]
    assert "next" not in data[0]
    assert "splits" not in data[0]
    assert "template_act_guid" not in data[0]


def test_scheduled_transactions_sort_and_redact_template_details(
    client, auth_headers, sample_book, session_factory, monkeypatch, tmp_path
):
    book_path = install_fake_scheduled_book(
        monkeypatch,
        tmp_path,
        [
            FakeScheduledTransaction(guid="sx-late", name="Later disabled", enabled=False, start_date=date(2026, 9, 1)),
            FakeScheduledTransaction(guid="sx-early", name="Early enabled", enabled=True, start_date=date(2026, 1, 1)),
        ],
    )
    point_sample_book_at(session_factory, sample_book, book_path)

    response = client.get(f"/books/{sample_book}/scheduled-transactions", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert [item["id"] for item in data] == ["sx-early", "sx-late"]
    for item in data:
        serialized = str(item)
        assert "Private template description" not in serialized
        assert "Private template memo" not in serialized
        assert "Private:Account" not in serialized
        assert "123.45" not in serialized
        assert "raw_sql" not in item
        assert "template_transaction_description" not in item
        assert "template_split_memo" not in item
        assert "template_split_amount" not in item
        assert "template_account_name" not in item
        assert item["template_reference_status"] == "present_redacted"


def test_book_aware_scheduled_transactions_empty_state(
    client, auth_headers, sample_book, session_factory, monkeypatch, tmp_path
):
    book_path = install_fake_scheduled_book(monkeypatch, tmp_path, [])
    point_sample_book_at(session_factory, sample_book, book_path)

    response = client.get(f"/books/{sample_book}/scheduled-transactions", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == []


def test_scheduled_transactions_no_template_reference_stays_redacted(
    client, auth_headers, sample_book, session_factory, monkeypatch, tmp_path
):
    book_path = install_fake_scheduled_book(
        monkeypatch,
        tmp_path,
        [
            FakeScheduledTransaction(
                guid="sx-no-template",
                name="No template edge case",
                template_act_guid=None,
            )
        ],
    )
    point_sample_book_at(session_factory, sample_book, book_path)

    response = client.get(f"/books/{sample_book}/scheduled-transactions", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data[0]["has_template_account"] is False
    assert data[0]["template_reference_status"] == "not_present_redacted"
    assert data[0]["recurrence"] != []
    assert data[0]["amount"] == {
        "status": "not_available",
        "amount": None,
        "currency": None,
        "unresolved_formula_count": 0,
        "reason": "no_template_reference",
    }
    serialized = str(data[0])
    assert "No template account reference was reported" in serialized
    assert "template_split_amount" not in serialized
    assert "template_split_memo" not in serialized
    assert "template_transaction_description" not in serialized
    assert "Private template" not in serialized
    assert "raw_sql" not in data[0]


def test_scheduled_transactions_require_auth(client):
    response = client.get("/scheduled-transactions")

    assert response.status_code == 401


def test_scheduled_transactions_read_all_recurrence_rows_and_never_materialize(
    client, auth_headers, sample_book, session_factory, monkeypatch, tmp_path
):
    scheduled = FakeScheduledTransaction(
        guid="sx-all-rows",
        name="Composite schedule",
        start_date=date(2026, 1, 1),
        last_occur=date(2026, 5, 5),
        recurrence=[FakeRecurrence(recurrence_period_start=date(2099, 1, 1))],
    )
    recurrence_rows = [
        FakeRecurrence(id=11, obj_guid="sx-all-rows", recurrence_period_start=date(2026, 1, 1)),
        FakeRecurrence(id=12, obj_guid="sx-all-rows", recurrence_period_start=date(2026, 1, 5)),
    ]
    opened_books = []
    book_path = install_fake_scheduled_book_with_rows(
        monkeypatch,
        tmp_path,
        [scheduled],
        recurrence_rows,
        opened_books=opened_books,
    )
    point_sample_book_at(session_factory, sample_book, book_path)

    response = client.get(
        f"/books/{sample_book}/scheduled-transactions?as_of_date=2026-06-01",
        headers=auth_headers,
    )

    assert response.status_code == 200
    [item] = response.json()
    assert [row["period_start"] for row in item["recurrence"]] == ["2026-01-01", "2026-01-05"]
    assert item["forecast"] == {
        "status": "ready",
        "reason": None,
        "as_of_date": "2026-06-01",
        "next_due_date": "2026-06-01",
        "is_overdue": False,
        "upcoming_7_days": ["2026-06-01", "2026-06-05"],
        "upcoming_30_days": ["2026-06-01", "2026-06-05"],
    }
    assert item["new_transactions_created"] == 0
    assert len(opened_books) == 1
    assert opened_books[0].transactions == []


def test_scheduled_transaction_amount_is_exact_only_for_constant_balanced_formulas(
    client, auth_headers, sample_book, session_factory, monkeypatch, tmp_path
):
    transaction = FakeTemplateTransaction(guid="template-tx", currency=FakeCommodity("RUB"))
    template_account = FakeTemplateAccount(
        splits=[
            FakeTemplateSplit(transaction, debit_formula="125.50"),
            FakeTemplateSplit(transaction, credit_formula="125.50"),
        ]
    )
    scheduled = FakeScheduledTransaction(
        guid="sx-constant",
        name="Constant schedule",
        template_account=template_account,
    )
    book_path = install_fake_scheduled_book(monkeypatch, tmp_path, [scheduled])
    point_sample_book_at(session_factory, sample_book, book_path)

    response = client.get("/scheduled-transactions?as_of_date=2026-06-01", headers=auth_headers)

    assert response.status_code == 200
    amount = response.json()[0]["amount"]
    assert amount == {
        "status": "resolved",
        "amount": str(Decimal("125.50")),
        "currency": "RUB",
        "unresolved_formula_count": 0,
        "reason": None,
    }


def test_scheduled_transaction_amount_does_not_stringify_unknown_currency(
    client, auth_headers, sample_book, session_factory, monkeypatch, tmp_path
):
    transaction = FakeTemplateTransaction(guid="template-private-currency", currency=FakePrivateCurrency())
    template_account = FakeTemplateAccount(
        splits=[
            FakeTemplateSplit(transaction, debit_formula="125.50"),
            FakeTemplateSplit(transaction, credit_formula="125.50"),
        ]
    )
    scheduled = FakeScheduledTransaction(
        guid="sx-private-currency",
        name="Unknown currency schedule",
        template_account=template_account,
    )
    book_path = install_fake_scheduled_book(monkeypatch, tmp_path, [scheduled])
    point_sample_book_at(session_factory, sample_book, book_path)

    response = client.get("/scheduled-transactions?as_of_date=2026-06-01", headers=auth_headers)

    assert response.status_code == 200
    amount = response.json()[0]["amount"]
    assert amount["status"] == "unresolved"
    assert amount["amount"] is None
    assert amount["currency"] is None
    assert amount["reason"] == "currency_unavailable"
    assert "PRIVATE-CURRENCY-MARKER" not in response.text


def test_scheduled_transaction_variable_formula_is_unresolved_never_fake_zero(
    client, auth_headers, sample_book, session_factory, monkeypatch, tmp_path
):
    transaction = FakeTemplateTransaction(guid="template-variable", currency=FakeCommodity("RUB"))
    template_account = FakeTemplateAccount(
        splits=[
            FakeTemplateSplit(transaction, debit_formula="rent_amount"),
            FakeTemplateSplit(transaction, credit_formula="rent_amount"),
        ]
    )
    scheduled = FakeScheduledTransaction(
        guid="sx-variable",
        name="Variable schedule",
        template_account=template_account,
    )
    book_path = install_fake_scheduled_book(monkeypatch, tmp_path, [scheduled])
    point_sample_book_at(session_factory, sample_book, book_path)

    response = client.get("/scheduled-transactions?as_of_date=2026-06-01", headers=auth_headers)

    assert response.status_code == 200
    amount = response.json()[0]["amount"]
    assert amount["status"] == "unresolved"
    assert amount["amount"] is None
    assert amount["currency"] is None
    assert amount["unresolved_formula_count"] == 2
    assert amount["reason"] == "template_variables_unresolved"
    assert "0.00" not in str(amount)
    assert "rent_amount" not in str(amount)


def test_missing_template_formula_slots_are_unresolved_never_fake_zero(
    client, auth_headers, sample_book, session_factory, monkeypatch, tmp_path
):
    transaction = FakeTemplateTransaction(guid="template-missing", currency=FakeCommodity("RUB"))
    template_account = FakeTemplateAccount(
        splits=[
            FakeTemplateSplitWithoutFormulaSlots(transaction),
            FakeTemplateSplitWithoutFormulaSlots(transaction),
        ]
    )
    scheduled = FakeScheduledTransaction(
        guid="sx-missing-formulas",
        name="Missing formula schedule",
        template_account=template_account,
    )
    book_path = install_fake_scheduled_book(monkeypatch, tmp_path, [scheduled])
    point_sample_book_at(session_factory, sample_book, book_path)

    response = client.get("/scheduled-transactions?as_of_date=2026-06-01", headers=auth_headers)

    assert response.status_code == 200
    amount = response.json()[0]["amount"]
    assert amount["status"] == "unresolved"
    assert amount["amount"] is None
    assert amount["currency"] is None
    assert amount["reason"] == "template_shape_unsupported"
    assert "0.00" not in str(amount)


def test_empty_template_formulas_are_unresolved_never_inferred_as_zero(
    client, auth_headers, sample_book, session_factory, monkeypatch, tmp_path
):
    transaction = FakeTemplateTransaction(guid="template-empty", currency=FakeCommodity("RUB"))
    template_account = FakeTemplateAccount(
        splits=[FakeTemplateSplit(transaction), FakeTemplateSplit(transaction)]
    )
    scheduled = FakeScheduledTransaction(
        guid="sx-empty-formulas",
        name="Empty formula schedule",
        template_account=template_account,
    )
    book_path = install_fake_scheduled_book(monkeypatch, tmp_path, [scheduled])
    point_sample_book_at(session_factory, sample_book, book_path)

    response = client.get("/scheduled-transactions?as_of_date=2026-06-01", headers=auth_headers)

    assert response.status_code == 200
    amount = response.json()[0]["amount"]
    assert amount["status"] == "unresolved"
    assert amount["amount"] is None
    assert amount["currency"] is None
    assert amount["reason"] == "template_shape_unsupported"
    assert "0.00" not in str(amount)


def test_template_split_scan_is_bounded_and_unresolved(
    client, auth_headers, sample_book, session_factory, monkeypatch, tmp_path
):
    import app.services.gnucash_book as gb_module

    transaction = FakeTemplateTransaction(guid="template-many-splits", currency=FakeCommodity("RUB"))
    template_account = FakeTemplateAccount(
        splits=[
            FakeTemplateSplit(transaction, debit_formula="1"),
            FakeTemplateSplit(transaction, credit_formula="1"),
        ]
    )
    scheduled = FakeScheduledTransaction(
        guid="sx-many-template-splits",
        name="Many template splits",
        template_account=template_account,
    )
    book_path = install_fake_scheduled_book(monkeypatch, tmp_path, [scheduled])
    point_sample_book_at(session_factory, sample_book, book_path)
    monkeypatch.setattr(gb_module, "SCHEDULED_TEMPLATE_SPLIT_LIMIT", 1)

    response = client.get("/scheduled-transactions?as_of_date=2026-06-01", headers=auth_headers)

    assert response.status_code == 200
    amount = response.json()[0]["amount"]
    assert amount["status"] == "unresolved"
    assert amount["amount"] is None
    assert amount["reason"] == "template_shape_unsupported"


def test_template_formula_length_is_bounded_and_unresolved(
    client, auth_headers, sample_book, session_factory, monkeypatch, tmp_path
):
    import app.services.gnucash_book as gb_module

    transaction = FakeTemplateTransaction(guid="template-long-formula", currency=FakeCommodity("RUB"))
    template_account = FakeTemplateAccount(
        splits=[
            FakeTemplateSplit(transaction, debit_formula="12345"),
            FakeTemplateSplit(transaction, credit_formula="12345"),
        ]
    )
    scheduled = FakeScheduledTransaction(
        guid="sx-long-formula",
        name="Long formula",
        template_account=template_account,
    )
    book_path = install_fake_scheduled_book(monkeypatch, tmp_path, [scheduled])
    point_sample_book_at(session_factory, sample_book, book_path)
    monkeypatch.setattr(gb_module, "SCHEDULED_FORMULA_TEXT_LIMIT", 4)

    response = client.get("/scheduled-transactions?as_of_date=2026-06-01", headers=auth_headers)

    assert response.status_code == 200
    amount = response.json()[0]["amount"]
    assert amount["status"] == "unresolved"
    assert amount["amount"] is None
    assert amount["reason"] == "template_shape_unsupported"


def test_invalid_recurrence_metadata_returns_typed_redacted_record(
    client, auth_headers, sample_book, session_factory, monkeypatch, tmp_path
):
    private_marker = "PRIVATE-SCHEDULE-MARKER"
    scheduled = FakeScheduledTransaction(
        guid="sx-invalid",
        name="Synthetic unavailable schedule",
        recurrence=[
            FakeRecurrence(
                recurrence_period_type=f"unsupported-{private_marker}",
                recurrence_period_start=date(2026, 1, 1),
            )
        ],
    )
    book_path = install_fake_scheduled_book(monkeypatch, tmp_path, [scheduled])
    point_sample_book_at(session_factory, sample_book, book_path)

    response = client.get("/scheduled-transactions?as_of_date=2026-06-01", headers=auth_headers)

    assert response.status_code == 200
    [item] = response.json()
    assert item["id"] == "sx-invalid"
    assert item["forecast"]["status"] == "unavailable"
    assert item["forecast"]["reason"] == "scheduled_recurrence_invalid_metadata"
    assert item["forecast"]["next_due_date"] is None
    assert item["recurrence"] == []
    assert private_marker not in response.text


def test_non_progressing_recurrence_returns_typed_redacted_cycle_error(
    client, auth_headers, sample_book, session_factory, monkeypatch, tmp_path
):
    import app.services.scheduled_recurrence as recurrence_module

    private_marker = "PRIVATE-CYCLE-MARKER"
    scheduled = FakeScheduledTransaction(
        guid="sx-cycle",
        name=private_marker,
        start_date=date(2026, 1, 1),
        last_occur=date(2026, 5, 1),
    )
    book_path = install_fake_scheduled_book(monkeypatch, tmp_path, [scheduled])
    point_sample_book_at(session_factory, sample_book, book_path)
    monkeypatch.setattr(
        recurrence_module,
        "_next_recurrence_date",
        lambda recurrence, reference: reference,
    )

    response = client.get("/scheduled-transactions?as_of_date=2026-06-01", headers=auth_headers)

    assert response.status_code == 422
    assert response.json() == {
        "detail": {
            "code": "scheduled_recurrence_cycle",
            "message": "Scheduled transaction recurrence could not advance safely.",
        }
    }
    assert private_marker not in response.text


def test_recurrence_row_limit_returns_typed_redacted_error(
    client, auth_headers, sample_book, session_factory, monkeypatch, tmp_path
):
    import app.services.gnucash_book as gb_module

    scheduled = FakeScheduledTransaction(guid="sx-row-limit", name="Private row-limit schedule")
    recurrence_rows = [
        FakeRecurrence(id=1, obj_guid=scheduled.guid),
        FakeRecurrence(id=2, obj_guid=scheduled.guid),
    ]
    book_path = install_fake_scheduled_book_with_rows(
        monkeypatch,
        tmp_path,
        [scheduled],
        recurrence_rows,
    )
    point_sample_book_at(session_factory, sample_book, book_path)
    monkeypatch.setattr(gb_module, "SCHEDULED_RECURRENCE_ROW_LIMIT", 1)

    response = client.get("/scheduled-transactions?as_of_date=2026-06-01", headers=auth_headers)

    assert response.status_code == 422
    assert response.json() == {
        "detail": {
            "code": "scheduled_recurrence_invalid_metadata",
            "message": "Scheduled transaction recurrence metadata is invalid.",
        }
    }
    assert "Private row-limit schedule" not in response.text
