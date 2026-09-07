"""QA-06: intentional structural-root suppression is not a broken parent link."""
from pathlib import Path
from types import SimpleNamespace
import hashlib

import piecash
import pytest

from app.services.account_explorer import (
    AccountExplorerError,
    build_account_explorer_query,
    build_account_explorer_response,
    build_account_overview_response,
)
from tests.support.generate_qa_regression_fixture import generate_qa_regression_fixture


def account(number, name, kind="BANK", parent=None, **kwargs):
    return SimpleNamespace(guid=f"{number:032x}", name=name, type=kind,
                           parent_guid=parent.guid if parent else None, parent=parent,
                           commodity=SimpleNamespace(namespace="CURRENCY", mnemonic="RUB"),
                           splits=[], hidden=kwargs.pop("hidden", False), placeholder=False, **kwargs)


def query(**kwargs):
    return build_account_explorer_query(**{**dict(mode=None, query=None, types=None, hidden=None, placeholder=None), **kwargs})


def explore(accounts, **filters):
    return build_account_explorer_response(SimpleNamespace(accounts=accounts), query(**filters), book_id=7, base_currency="RUB")


@pytest.mark.parametrize("name", ["Root", "Корневой счёт", "Arbitrary structural name"])
def test_root_suppression_keeps_children_normal_and_source_parent(name):
    root = account(1, name, "ROOT")
    child = account(2, "Savings", "ASSET", root)
    leaf = account(3, "Envelope", parent=child)
    data = explore([root, child, leaf])
    by_id = {node.id: node for node in data.nodes}
    assert root.guid not in by_id
    assert by_id[child.guid].structure_status == "root", "QA-06 canonical omitted root must not be an orphan"
    assert by_id[child.guid].source_parent_id == root.guid
    assert by_id[child.guid].parent_id is None
    assert by_id[leaf.guid].structure_status == "normal"
    overview = build_account_overview_response(SimpleNamespace(accounts=[root, child, leaf]), child.guid, book_id=7, base_currency="RUB")
    assert overview.structure_status == "root"


def test_filtered_known_ancestor_and_root_named_ordinary_account_are_not_orphans():
    root = account(1, "Unrelated name", "ROOT")
    parent = account(2, "Root", "ASSET", root, hidden=True)
    child = account(3, "Envelope", parent=parent)
    flat = explore([root, parent, child], mode="flat", types=["BANK"])
    assert len(flat.nodes) == 1
    assert flat.nodes[0].structure_status == "normal"
    assert flat.nodes[0].parent_id == parent.guid
    tree = explore([root, parent, child], query="Envelope")
    assert {node.id for node in tree.nodes} == {parent.guid, child.guid}
    assert next(node for node in tree.nodes if node.id == parent.guid).structure_status == "root"
    assert next(node for node in tree.nodes if node.id == parent.guid).match_state == "ancestor_context"


def test_unknown_parent_self_cycle_multi_cycle_and_duplicate_diagnostics_survive():
    orphan = account(10, "Orphan")
    orphan.parent_guid = f"{99:032x}"
    self_cycle = account(11, "Self")
    self_cycle.parent = self_cycle
    self_cycle.parent_guid = self_cycle.guid
    a = account(12, "Cycle A")
    b = account(13, "Cycle B", parent=a)
    a.parent, a.parent_guid = b, b.guid
    ordinary = account(14, "Root", "ASSET")
    data = explore([orphan, self_cycle, a, b, ordinary])
    statuses = {node.id: node.structure_status for node in data.nodes}
    assert statuses == {orphan.guid: "orphan_promoted", self_cycle.guid: "cycle_broken_root", a.guid: "cycle_broken_root", b.guid: "cycle_member", ordinary.guid: "root"}
    duplicate = account(14, "Duplicate")
    with pytest.raises(AccountExplorerError, match="duplicate account identifiers"):
        explore([ordinary, duplicate])


def test_missing_canonical_root_id_is_not_proof_parent_exists():
    orphan = account(10, "Orphan")
    orphan.parent_guid = f"{99:032x}"
    book = SimpleNamespace(accounts=[orphan], root_account_guid=orphan.parent_guid)
    data = build_account_explorer_response(book, query(), book_id=7, base_currency="RUB")
    assert data.nodes[0].structure_status == "orphan_promoted"


def test_sql_and_in_memory_hierarchy_parity_on_generated_book(tmp_path):
    fixture = generate_qa_regression_fixture(tmp_path / "generated", scenario="money")
    path = Path(fixture["book_path"])
    with piecash.open_book(str(path), readonly=True, open_if_lock=True) as book:
        sql = build_account_explorer_response(book, query(hidden="include"), book_id=7, base_currency="RUB")
        fallback_book = SimpleNamespace(accounts=list(book.accounts), root_account=book.root_account, root_template=book.root_template)
        fallback = build_account_explorer_response(fallback_book, query(hidden="include"), book_id=7, base_currency="RUB")
        assert [node.model_dump() for node in sql.nodes] == [node.model_dump() for node in fallback.nodes]
        assert sql.root_ids == fallback.root_ids
        assert all(node.structure_status == "root" for node in sql.nodes), "QA-06 actual SQLite canonical root is omitted intentionally"
        assert sql.scan.query_count == 2
    assert hashlib.sha256(path.read_bytes()).hexdigest() == fixture["sha256"]
