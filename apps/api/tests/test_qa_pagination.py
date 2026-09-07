"""QA-10 deterministic 32-row pagination source; never use a private book."""
import hashlib
import sqlite3
from tests.support.generate_qa_regression_fixture import generate_qa_regression_fixture


def test_generated_pagination_is_exact_and_deterministic(tmp_path):
    first = generate_qa_regression_fixture(tmp_path / 'first', scenario='pagination')
    second = generate_qa_regression_fixture(tmp_path / 'second', scenario='pagination')
    assert first['sha256'] == second['sha256']
    expected = {tx['id'] for tx in first['transactions'].values()}
    assert len(expected) == 32
    with sqlite3.connect(f"file:{first['book_path']}?mode=ro", uri=True) as db:
        assert db.execute('PRAGMA quick_check').fetchone() == ('ok',)
        assert {row[0] for row in db.execute('SELECT guid FROM transactions')} == expected
    assert hashlib.sha256(open(first['book_path'],'rb').read()).hexdigest() == first['sha256']
