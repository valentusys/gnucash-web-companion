"""Tests for read-only scheduled transaction awareness API endpoints."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

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


def install_fake_scheduled_book(monkeypatch, tmp_path, scheduled_transactions):
    book_path = tmp_path / "scheduled.gnucash"
    book_path.write_text("fake")

    def fake_open_book(path, readonly=False):
        assert readonly is True
        return FakeBookWithScheduledTransactions(scheduled_transactions=scheduled_transactions)

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

    response = client.get("/scheduled-transactions", headers=auth_headers)

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
            "limitations": [
                "Read-only summary metadata only; edit scheduled transactions in GnuCash Desktop.",
                "Next occurrence dates are not calculated by this pre-alpha view.",
                "Template split details are intentionally not exposed.",
                "Template account reference is present, but template split amounts, accounts, memos, transaction descriptions, and raw SQL are redacted.",
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
                recurrence=[],
            )
        ],
    )
    point_sample_book_at(session_factory, sample_book, book_path)

    response = client.get(f"/books/{sample_book}/scheduled-transactions", headers=auth_headers)

    assert response.status_code == 200
    data = response.json()
    assert data[0]["has_template_account"] is False
    assert data[0]["template_reference_status"] == "not_present_redacted"
    assert data[0]["recurrence"] == []
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
