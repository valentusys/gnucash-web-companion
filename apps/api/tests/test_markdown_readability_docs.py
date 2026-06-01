"""Regression tests for markdown readability guidance."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
GUIDE = ROOT / "docs/development/markdown-readability.md"


def test_markdown_readability_guide_preserves_safety_and_triage_workflow() -> None:
    text = GUIDE.read_text(encoding="utf-8")

    assert "GNUCASH_WRITES_ENABLED=false" in text
    assert "real/private/original/only-copy GnuCash books" in text
    assert "not production-ready" in text
    assert "Status/readability triage" in text
    assert "Split long status docs before rewriting them" in text
    assert "Do not hide release/no-release decisions" in text
