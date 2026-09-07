"""QA-08 synthetic currency resolver scenarios, independent of configured metadata."""
from pathlib import Path
import hashlib
import pytest
import piecash

from app.services.reporting_currency import resolve_reporting_currency
from tests.support.generate_qa_regression_fixture import generate_qa_regression_fixture, SCENARIOS


@pytest.mark.parametrize('scenario,selected,reason', [('money','RUB','dominant_detected'), ('currency_eur','EUR','dominant_detected'), ('currency_tie',None,'dominance_tie'), ('empty',None,'no_eligible_currency')])
def test_currency_scenarios_are_deterministic_and_readonly(tmp_path,scenario,selected,reason):
    assert scenario in SCENARIOS, 'QA-08 needs deterministic tie and alternative-book fixtures'
    first=generate_qa_regression_fixture(tmp_path/'one',scenario=scenario)
    second=generate_qa_regression_fixture(tmp_path/'two',scenario=scenario)
    assert first['sha256']==second['sha256']
    path=Path(first['book_path'])
    with piecash.open_book(str(path),readonly=True,open_if_lock=True) as book:
        resolution=resolve_reporting_currency(book,None)
        assert resolution.selected_currency==selected
        assert resolution.reason==reason
        assert resolution.configured_currency is None
        assert resolution.status==('ready' if selected else 'setup_required')
    assert hashlib.sha256(path.read_bytes()).hexdigest()==first['sha256']
