"""QA-01: per-record recurrence isolation, real SQLite + both HTTP aliases."""
from datetime import date
import hashlib
from pathlib import Path

import pytest

from app.services.gnucash_book import GnuCashBookService
from app.services.gnucash_exceptions import GnuCashReadError
from tests.support.generate_qa_regression_fixture import generate_qa_regression_fixture
from tests.test_scheduled_transactions import (
    FakeRecurrence, FakeScheduledTransaction, install_fake_scheduled_book,
    point_sample_book_at,
    auth_headers, auth_token, client, engine, sample_book, session_factory,
)
from tests.test_transactions import viewer_user, viewer_token, viewer_headers


@pytest.mark.parametrize("scenario,ready,unavailable", [("scheduled_partial", 15, 1), ("scheduled_invalid", 0, 1), ("empty", 0, 0)])
def test_generated_schedules_survive_one_invalid_row(client, auth_headers, sample_book, session_factory, tmp_path, scenario, ready, unavailable):
    fixture = generate_qa_regression_fixture(tmp_path / scenario, scenario=scenario)
    path = Path(fixture["book_path"])
    point_sample_book_at(session_factory, sample_book, path)
    service = GnuCashBookService({"uri_or_path": str(path)})
    items = service.list_scheduled_transactions(as_of_date=date(2026, 9, 6))
    assert sum(item.forecast.status == "ready" for item in items) == ready
    assert sum(item.forecast.status == "unavailable" for item in items) == unavailable
    expected = [item.model_dump() for item in items]
    for prefix in ("", f"/books/{sample_book}"):
        response = client.get(f"{prefix}/scheduled-transactions?as_of_date=2026-09-06", headers=auth_headers)
        assert response.status_code == 200, response.text
        assert response.json() == expected
    for item in items:
        assert item.new_transactions_created == 0
        if item.forecast.status == "unavailable":
            assert item.forecast.model_dump() == {
                "status": "unavailable", "reason": "scheduled_recurrence_invalid_metadata",
                "as_of_date": "2026-09-06", "next_due_date": None, "is_overdue": False,
                "upcoming_7_days": [], "upcoming_30_days": [],
            }
            assert item.recurrence == []
            assert item.has_template_account is True
            assert item.template_reference_status == 'present_redacted'
            assert item.amount.status == "not_available"
            assert item.amount.amount is None and item.amount.currency is None
        else:
            assert item.forecast.upcoming_30_days == ["2026-10-01"]
    assert hashlib.sha256(path.read_bytes()).hexdigest() == fixture["sha256"]


@pytest.mark.parametrize("changes", [
    {"recurrence": []},
    {"recurrence": [FakeRecurrence(recurrence_mult=0)]},
    {"recurrence": [FakeRecurrence(recurrence_mult="not-int")]},
    {"recurrence": [FakeRecurrence(recurrence_period_start="not-date")]},
    {"recurrence": [FakeRecurrence(recurrence_period_type="unsupported-PRIVATE-MARKER")]},
    {"start_date": "not-date"}, {"num_occur": -1}, {"adv_creation": "not-int"},
    {"enabled": False, "recurrence": []},
    {"template_act_guid": None, "recurrence": []},
])
def test_record_metadata_errors_are_isolated(monkeypatch, tmp_path, changes):
    schedules = [
        FakeScheduledTransaction(guid="ok", name="Synthetic valid"),
        FakeScheduledTransaction(guid="bad", name="Synthetic unavailable", **changes),
        FakeScheduledTransaction(guid="disabled", name="Synthetic disabled", enabled=False),
        FakeScheduledTransaction(guid="exhausted", name="Synthetic exhausted", num_occur=1, rem_occur=0),
    ]
    path = install_fake_scheduled_book(monkeypatch, tmp_path, schedules)
    service = GnuCashBookService({"uri_or_path": str(path)})
    items = service.list_scheduled_transactions(as_of_date=date(2026, 6, 1))
    assert {item.id: item.forecast.status for item in items} == {
        "ok": "ready", "bad": "unavailable", "disabled": "disabled", "exhausted": "exhausted",
    }
    assert "PRIVATE-MARKER" not in str([item.model_dump() for item in items])
    unavailable = next(item for item in items if item.id == "bad")
    assert unavailable.has_template_account == bool(changes.get("template_act_guid", "template-account-guid"))
    schedules.reverse()
    assert service.list_scheduled_transactions(as_of_date=date(2026, 6, 1)) == items


def test_global_recurrence_read_error_is_not_a_partial_success(monkeypatch, tmp_path):
    path = install_fake_scheduled_book(monkeypatch, tmp_path, [FakeScheduledTransaction(guid="ok", name="Synthetic")])
    def failed_read(*args):
        raise GnuCashReadError("global read unavailable")
    monkeypatch.setattr(GnuCashBookService, "_scheduled_recurrence_rows", failed_read)
    with pytest.raises(GnuCashReadError):
        GnuCashBookService({"uri_or_path": str(path)}).list_scheduled_transactions(as_of_date=date(2026, 6, 1))


def test_recurrence_cycle_still_fails_closed(monkeypatch, tmp_path):
    from app.services.gnucash_exceptions import ScheduledRecurrenceError
    path = install_fake_scheduled_book(monkeypatch, tmp_path, [FakeScheduledTransaction(guid="ok", name="Synthetic")])
    def cycle(*args, **kwargs):
        raise ScheduledRecurrenceError("scheduled_recurrence_cycle")
    monkeypatch.setattr(GnuCashBookService, "_scheduled_transaction_to_dto", cycle)
    with pytest.raises(ScheduledRecurrenceError) as exc:
        GnuCashBookService({"uri_or_path": str(path)}).list_scheduled_transactions(as_of_date=date(2026, 6, 1))
    assert exc.value.code == "scheduled_recurrence_cycle"


def test_record_unexpected_error_is_not_swallowed(monkeypatch, tmp_path):
    path = install_fake_scheduled_book(monkeypatch, tmp_path, [FakeScheduledTransaction(guid="ok", name="Synthetic")])
    def failed_record(*args, **kwargs):
        raise RuntimeError("unexpected programming error")
    monkeypatch.setattr(GnuCashBookService, "_scheduled_transaction_to_dto", failed_record)
    with pytest.raises(GnuCashReadError):
        GnuCashBookService({"uri_or_path": str(path)}).list_scheduled_transactions(as_of_date=date(2026, 6, 1))


def test_invalid_schedule_never_bypasses_book_access(client, viewer_headers, sample_book, session_factory, tmp_path):
    fixture = generate_qa_regression_fixture(tmp_path / "access")
    point_sample_book_at(session_factory, sample_book, Path(fixture["book_path"]))
    for prefix in ("", f"/books/{sample_book}"):
        response = client.get(f"{prefix}/scheduled-transactions", headers=viewer_headers)
        assert response.status_code == 403
        assert "SYNTHETIC" not in response.text


@pytest.mark.parametrize("failure", ["missing", "permission", "query"])
def test_global_scheduled_failure_remains_path_safe_http_error(client, auth_headers, sample_book, session_factory, monkeypatch, tmp_path, failure):
    path = tmp_path / "PRIVATE-GLOBAL-PATH.gnucash.sqlite"
    if failure != "missing":
        path.write_text("synthetic placeholder")
    point_sample_book_at(session_factory, sample_book, path)
    if failure == "permission":
        import app.services.gnucash_book as module
        def denied(*args, **kwargs):
            raise PermissionError(str(path))
        monkeypatch.setattr(module.piecash, "open_book", denied)
    elif failure == "query":
        def failed(*args, **kwargs):
            raise GnuCashReadError(str(path))
        monkeypatch.setattr(GnuCashBookService, "list_scheduled_transactions", failed)
    for prefix in ("", f"/books/{sample_book}"):
        response = client.get(f"{prefix}/scheduled-transactions", headers=auth_headers)
        assert response.status_code == 503
        assert "PRIVATE-GLOBAL-PATH" not in response.text
