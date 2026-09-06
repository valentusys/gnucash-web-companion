"""Generated fixtures are reproducible, isolated and never overwrite caller data."""
from pathlib import Path
import hashlib
import sqlite3

import pytest

from tests.support.generate_qa_regression_fixture import generate_qa_regression_fixture


def snapshot(path):
    with sqlite3.connect(f"file:{path}?mode=ro", uri=True) as db:
        assert db.execute("pragma quick_check").fetchone() == ("ok",)
        return list(db.iterdump())


def test_generated_scheduled_partial_structure_and_determinism(tmp_path):
    first = generate_qa_regression_fixture(tmp_path / "first")
    second = generate_qa_regression_fixture(tmp_path / "second")
    assert first.get("seed") == second.get("seed") == 20260906
    paths = [Path(item["book_path"]) for item in (first, second)]
    assert all(path.is_relative_to(tmp_path) for path in paths)
    assert snapshot(paths[0]) == snapshot(paths[1])
    assert paths[0].read_bytes() == paths[1].read_bytes()
    assert first["sha256"] == hashlib.sha256(paths[0].read_bytes()).hexdigest()
    assert first["scenario"] == "scheduled_partial"
    with sqlite3.connect(f"file:{paths[0]}?mode=ro", uri=True) as db:
        assert db.execute("select count(*) from schedxactions").fetchone() == (16,)
        assert db.execute("select count(*) from recurrences").fetchone() == (15,)
        assert db.execute("select count(*) from transactions").fetchone() == (0,)
        assert db.execute("select count(*) from splits").fetchone() == (0,)
        assert db.execute("select count(*) from schedxactions where name like 'SYNTHETIC QA %'").fetchone() == (16,)
    assert paths[0].stat().st_mode & 0o222 == 0


@pytest.mark.parametrize("scenario,counts", [("scheduled_valid", (15, 15)), ("scheduled_invalid", (1, 0)), ("empty", (0, 0))])
def test_generated_scenarios_are_separate(tmp_path, scenario, counts):
    fixture = generate_qa_regression_fixture(tmp_path / scenario, scenario=scenario)
    assert fixture.get("scenario") == scenario
    with sqlite3.connect(f"file:{fixture['book_path']}?mode=ro", uri=True) as db:
        assert (db.execute("select count(*) from schedxactions").fetchone()[0], db.execute("select count(*) from recurrences").fetchone()[0]) == counts


def test_generated_money_scenario_is_deterministic_and_balanced(tmp_path):
    first = generate_qa_regression_fixture(tmp_path / "money1", scenario="money")
    second = generate_qa_regression_fixture(tmp_path / "money2", scenario="money")
    assert Path(first["book_path"]).read_bytes() == Path(second["book_path"]).read_bytes()
    assert set(first["transactions"]) == {"income", "expense", "refund", "transfer", "credit", "zero", "large", "composite", "multicurrency"}
    from fractions import Fraction
    with sqlite3.connect(f"file:{first['book_path']}?mode=ro", uri=True) as db:
        for tx in first["transactions"].values():
            values = db.execute("select value_num,value_denom from splits where tx_guid=?", (tx["id"],)).fetchall()
            assert sum((Fraction(n, d) for n, d in values), Fraction()) == 0
        assert db.execute("select count(*) from schedxactions").fetchone() == (0,)
    assert first["transactions"]["large"]["magnitude"] == "90071992547409.91"


def test_generator_refuses_existing_directory_or_symlink(tmp_path):
    existing = tmp_path / "existing"
    existing.mkdir()
    marker = existing / "keep.txt"
    marker.write_text("do not overwrite")
    alias = tmp_path / "alias"
    alias.symlink_to(existing, target_is_directory=True)
    for path in (existing, alias):
        with pytest.raises(FileExistsError):
            generate_qa_regression_fixture(path)
        assert marker.read_text() == "do not overwrite"
        assert sorted(p.name for p in existing.iterdir()) == ["keep.txt"]


def test_generator_rejects_unknown_scenario_before_writing(tmp_path):
    target = tmp_path / "unknown"
    with pytest.raises(ValueError, match="Unknown synthetic scenario"):
        generate_qa_regression_fixture(target, scenario="private-copy")
    assert not target.exists()
