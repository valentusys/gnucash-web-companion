"""QA-03 order-independent unscoped magnitude and explicit account delta."""
from decimal import Decimal
import csv
import hashlib
import io
from pathlib import Path

import pytest

from app.models import Book
from app.services.gnucash_book import GnuCashBookService
from tests.support.generate_qa_regression_fixture import generate_qa_regression_fixture, guid
from tests.test_scheduled_transactions import point_sample_book_at
from tests.test_transactions import client, engine, session_factory, sample_book, auth_headers, auth_token


@pytest.fixture
def money_book(tmp_path, session_factory, sample_book):
    manifest = generate_qa_regression_fixture(tmp_path / 'money', scenario='money')
    point_sample_book_at(session_factory, sample_book, Path(manifest['book_path']))
    with session_factory() as session:
        session.get(Book, sample_book).base_currency = 'RUB'
        session.commit()
    return manifest


def explorer(client, headers, book, **params):
    response = client.get(f'/books/{book}/transactions/explorer', headers=headers, params={'date_from': '2026-09-01', 'date_to': '2026-09-02', 'page_size': 20, **params})
    assert response.status_code == 200, response.text
    return response.json()['items']


def test_unscoped_money_semantics_survive_split_permutation(client, auth_headers, sample_book, money_book, monkeypatch):
    baseline = {item['id']: item for item in explorer(client, auth_headers, sample_book)}
    original = GnuCashBookService._splits
    monkeypatch.setattr(GnuCashBookService, '_splits', lambda self, tx: list(reversed(original(self, tx))))
    reordered = {item['id']: item for item in explorer(client, auth_headers, sample_book)}
    for spec in money_book['transactions'].values():
        before, after = baseline[spec['id']], reordered[spec['id']]
        assert before['representative_amount'] == after['representative_amount'], 'split order cannot flip a displayed amount'
        assert before['amount_basis'] == after['amount_basis']
        if spec['magnitude'] is not None:
            assert before['amount_basis'] == 'neutral_magnitude'
            assert Decimal(before['representative_amount']['amount']) == Decimal(spec['magnitude'])
            assert before['representative_amount']['currency'] == 'RUB'
        else:
            assert before['amount_basis'] == 'multiple_amounts'
            assert before['representative_amount'] is None
            assert before['representative_account'] is None
    from types import SimpleNamespace as NS
    monkeypatch.setattr(GnuCashBookService, '_splits', lambda self, tx: [
        NS(guid=f'{index:032x}', account=split.account, value=split.value, quantity=split.quantity)
        for index, split in enumerate(reversed(original(self, tx)))
    ])
    for changed in explorer(client, auth_headers, sample_book):
        before = baseline[changed['id']]
        for field in ('amount_basis', 'representative_amount', 'representative_account', 'matched_amount'):
            assert changed[field] == before[field], f'split GUID/order must not change {field}'
    assert hashlib.sha256(Path(money_book['book_path']).read_bytes()).hexdigest() == money_book['sha256']


@pytest.mark.parametrize('account,currency,label,expected', [('cash','RUB','expense','-123.45'), ('expense','RUB','expense','123.45'), ('usd','USD','multicurrency','1.00')])
def test_selected_account_delta_and_csv_use_account_quantity(client, auth_headers, sample_book, session_factory, money_book, account, currency, label, expected):
    with session_factory() as session:
        session.get(Book, sample_book).base_currency = currency
        session.commit()
    account_id = guid(f'account:{account}')
    rows = explorer(client, auth_headers, sample_book, account_ids=account_id)
    row = next(row for row in rows if row['id'] == money_book['transactions'][label]['id'])
    assert row['amount_basis'] == 'selected_accounts'
    assert row['matched_amount'] == {'amount': expected, 'currency': currency}
    assert row['representative_amount'] == row['matched_amount']
    response = client.get(f'/books/{sample_book}/transactions/export', headers=auth_headers, params={'date_from':'2026-09-01','date_to':'2026-09-02','account_id':account_id})
    assert response.status_code == 200
    exported = list(csv.DictReader(io.StringIO(response.text)))
    assert {item['id'] for item in exported} == {item['id'] for item in rows}
    item = next(item for item in exported if item['id'] == row['id'])
    assert item['amount'] == expected and item['currency'] == currency
    if account == 'usd':
        filtered = explorer(client, auth_headers, sample_book, account_ids=account_id, min_amount='0.50', max_amount='2.00')
        csv_filtered = client.get(f'/books/{sample_book}/transactions/export', headers=auth_headers, params={'date_from':'2026-09-01','date_to':'2026-09-02','account_id':account_id,'min_amount':'0.50','max_amount':'2.00'})
        assert csv_filtered.status_code == 200
        assert {item['id'] for item in csv.DictReader(io.StringIO(csv_filtered.text))} == {item['id'] for item in filtered} == {row['id']}


def test_selected_group_zero_delta_is_not_first_split(client, auth_headers, sample_book, money_book):
    rows = explorer(client, auth_headers, sample_book, account_ids=[guid('account:cash'), guid('account:savings')])
    row = next(row for row in rows if row['id'] == money_book['transactions']['transfer']['id'])
    assert row['matched_amount'] == {'amount':'0.00','currency':'RUB'}
    assert row['representative_amount'] == row['matched_amount']
    assert row['amount_basis'] == 'selected_accounts'


@pytest.mark.parametrize('kind,sign', [('income','-'), ('expense','')])
def test_type_scope_uses_quantity_in_matching_account_currency(kind, sign):
    from types import SimpleNamespace as NS
    account = NS(guid='foreign',type=kind.upper(),commodity=NS(mnemonic='USD',namespace='CURRENCY'))
    split = NS(account=account,value=Decimal(sign+'90'),quantity=Decimal(sign+'1'))
    service = GnuCashBookService({'uri_or_path':'unused-synthetic','base_currency':'USD'})
    matches, amount = service._explorer_type_splits_and_amount([split],kind)
    assert matches == [split] and amount == Decimal('1')


def test_repeated_account_splits_use_net_quantity_for_list_and_filter():
    from types import SimpleNamespace as NS
    from datetime import date
    rub = NS(mnemonic='RUB', namespace='CURRENCY')
    a = NS(guid='a', name='Synthetic A', commodity=rub, parent=None)
    b = NS(guid='b', name='Synthetic B', commodity=rub, parent=None)
    tx = NS(guid='tx', post_date=date(2026,9,1), description='Synthetic net', currency=rub, splits=[NS(account=account,value=Decimal(value),quantity=Decimal(value)) for account,value in [(a,'-3'),(a,'1'),(b,'2')]])
    service = GnuCashBookService({'uri_or_path':'unused-synthetic'})
    assert service._transaction_to_list_item(tx, 'a').amount == '-2.00'
    assert service._transaction_matches(tx, 'a', None, None, None, min_amount=Decimal('2'), max_amount=Decimal('2'))


def test_csv_foreign_account_quantity_filter(client, auth_headers, sample_book, money_book):
    response = client.get(f'/books/{sample_book}/transactions/export', headers=auth_headers, params={'date_from':'2026-09-01','date_to':'2026-09-02','account_id':guid('account:usd'),'min_amount':'0.50','max_amount':'2.00'})
    assert response.status_code == 200
    rows = list(csv.DictReader(io.StringIO(response.text)))
    assert len(rows) == 1
    assert rows[0]['amount'] == '1.00' and rows[0]['currency'] == 'USD'


def test_unscoped_csv_ids_match_but_column_is_documented_account_delta(client, auth_headers, sample_book, money_book):
    rows = explorer(client, auth_headers, sample_book)
    response = client.get(f'/books/{sample_book}/transactions/export', headers=auth_headers, params={'date_from':'2026-09-01','date_to':'2026-09-02'})
    assert response.status_code == 200
    exported = list(csv.DictReader(io.StringIO(response.text)))
    assert {item['id'] for item in exported} == {item['id'] for item in rows}
    simple = {spec['id']: spec for spec in money_book['transactions'].values() if spec['magnitude'] is not None}
    for item in exported:
        assert item['account_id']
        if item['id'] in simple:
            assert abs(Decimal(item['amount'])) == Decimal(simple[item['id']]['magnitude'])
