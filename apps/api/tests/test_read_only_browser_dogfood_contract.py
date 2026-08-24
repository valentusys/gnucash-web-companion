"""Deterministic contract tests for the stock read-only browser dogfood harness."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[3]
HARNESS_PATH = REPO_ROOT / "scripts" / "smoke" / "read-only-browser-dogfood.py"

spec = importlib.util.spec_from_file_location("read_only_browser_dogfood", HARNESS_PATH)
assert spec is not None and spec.loader is not None
harness = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = harness
spec.loader.exec_module(harness)


def test_bounded_transactions_url_uses_supported_explorer_state() -> None:
    url = harness._bounded_transactions_url("http://127.0.0.1:18080/")

    assert url == (
        "http://127.0.0.1:18080/transactions?"
        "date_from=2024-01-01&date_to=2024-12-31&"
        "transaction_state=unreconciled&sort=date_desc&page_size=25"
    )
    assert "query=" not in url
    assert "limit=" not in url
    assert "offset=" not in url


def test_export_guard_accepts_supported_date_and_state_filters() -> None:
    harness._assert_export_preserves_supported_filters(
        "/transactions/export?date_from=2024-01-01&date_to=2024-12-31&"
        "transaction_state=unreconciled"
    )


@pytest.mark.parametrize(
    "href",
    [
        None,
        "/transactions/export?date_to=2024-12-31&transaction_state=unreconciled",
        "/transactions/export?date_from=2024-01-01&transaction_state=unreconciled",
        "/transactions/export?date_from=2024-01-01&date_to=2024-12-31",
        "/transactions/export?date_from=2023-01-01&date_to=2024-12-31&transaction_state=unreconciled",
    ],
)
def test_export_guard_rejects_missing_or_changed_supported_filters(href: str | None) -> None:
    with pytest.raises(harness.DogfoodFailure, match="supported active filters"):
        harness._assert_export_preserves_supported_filters(href)
