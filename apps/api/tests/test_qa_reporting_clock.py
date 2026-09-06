"""QA-04: one API calendar clock, no OS/host-clock changes in tests."""
from datetime import date, datetime
from pathlib import Path
from zoneinfo import ZoneInfo
import hashlib

import pytest

from app.services import reporting_clock
from app.routers import reports
from app.models import Book
from tests.support.generate_qa_regression_fixture import generate_qa_regression_fixture
from tests.test_scheduled_transactions import point_sample_book_at
from tests.test_transactions import client, engine, session_factory, sample_book, auth_headers, auth_token


CLOCK_CASES = [
    ('2026-09-05T15:30:00+00:00', 'Asia/Vladivostok', '2026-09-06'),
    ('2026-09-06T02:30:00+00:00', 'America/Los_Angeles', '2026-09-05'),
    ('2025-12-31T15:00:00+00:00', 'Asia/Vladivostok', '2026-01-01'),
    ('2024-02-29T23:30:00+00:00', 'Europe/Berlin', '2024-03-01'),
    ('2024-02-29T10:30:00+00:00', 'Europe/Berlin', '2024-02-29'),
    ('2026-03-08T06:59:00+00:00', 'America/New_York', '2026-03-08'),
    ('2026-03-08T07:01:00+00:00', 'America/New_York', '2026-03-08'),
]


def install_clock(monkeypatch, instant, zone):
    class FrozenLocalDate(date):
        @classmethod
        def today(cls):
            return datetime.fromisoformat(instant).astimezone(ZoneInfo(zone)).date()
    monkeypatch.setattr(reporting_clock, 'date', FrozenLocalDate)


@pytest.mark.parametrize('instant,zone,expected', CLOCK_CASES)
def test_clock_and_report_month_defaults_share_installation_date(monkeypatch, instant, zone, expected):
    install_clock(monkeypatch, instant, zone)
    assert reporting_clock.reporting_today().isoformat() == expected
    assert reports._current_month_range() == (expected[:7]+'-01', expected)


def test_clock_endpoint_requires_auth_and_book_access_without_opening_book(client, auth_headers, sample_book, monkeypatch):
    install_clock(monkeypatch, *CLOCK_CASES[0][:2])
    monkeypatch.setattr(reports, 'transaction_service_for', lambda *a, **k: pytest.fail('clock endpoint must not open or query a GnuCash book'))
    endpoint = f'/books/{sample_book}/reports/reporting-date'
    assert client.get(endpoint).status_code == 401
    response = client.get(endpoint, headers=auth_headers)
    assert response.status_code == 200
    assert response.json() == {'as_of_date': '2026-09-06', 'basis': 'api_local_calendar'}
    assert client.get('/books/999999/reports/reporting-date', headers=auth_headers).status_code == 404


@pytest.mark.parametrize('instant,zone,expected', CLOCK_CASES[:5])
def test_summary_scheduled_and_context_share_clock_but_explicit_asof_wins(client, auth_headers, sample_book, session_factory, tmp_path, monkeypatch, instant, zone, expected):
    install_clock(monkeypatch, instant, zone)
    manifest = generate_qa_regression_fixture(tmp_path/'clock',scenario='scheduled_valid')
    point_sample_book_at(session_factory,sample_book,Path(manifest['book_path']))
    with session_factory() as session:
        session.get(Book,sample_book).base_currency = 'RUB'
        session.commit()
    prefix = f'/books/{sample_book}'
    for params, asof in [({},expected), ({'as_of_date':'2026-09-01'},'2026-09-01')]:
        summary = client.get(prefix+'/reports/summary',headers=auth_headers,params=params)
        scheduled = client.get(prefix+'/scheduled-transactions',headers=auth_headers,params=params)
        assert summary.status_code == scheduled.status_code == 200
        assert summary.json()['as_of_date'] == asof
        assert all(item['forecast']['as_of_date'] == asof for item in scheduled.json())
    assert client.get(prefix+'/reports/reporting-date',headers=auth_headers).json()['as_of_date'] == expected
    assert hashlib.sha256(Path(manifest['book_path']).read_bytes()).hexdigest() == manifest['sha256']
