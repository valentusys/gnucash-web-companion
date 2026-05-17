"""Compatibility documentation checks for committed synthetic GnuCash fixtures."""

from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[3]
FIXTURES = [
    ROOT / "apps/api/tests/fixtures/test-book.gnucash.sqlite",
    ROOT / "apps/api/tests/fixtures/test-book-multicurrency.gnucash.sqlite",
]
DOC = ROOT / "docs/gnucash-compatibility.md"


def _version_rows(path: Path) -> dict[str, int]:
    with sqlite3.connect(path) as conn:
        return dict(conn.execute("select table_name, table_version from versions"))


def test_committed_fixtures_have_expected_gnucash_schema_markers() -> None:
    """The documented compatibility baseline must match committed fixture schema markers."""

    for fixture in FIXTURES:
        rows = _version_rows(fixture)
        assert rows["Gnucash"] == 3_000_000
        assert rows["Gnucash-Resave"] == 19_920


def test_compatibility_doc_mentions_fixture_schema_markers() -> None:
    """Keep the compatibility matrix tied to real synthetic fixture metadata."""

    doc = DOC.read_text(encoding="utf-8")
    for fixture in FIXTURES:
        assert fixture.name in doc
    assert "Gnucash = 3000000" in doc
    assert "Gnucash-Resave = 19920" in doc
    assert "PostgreSQL/MySQL/MariaDB" in doc
    assert "GNUCASH_WRITES_ENABLED=false" in doc
