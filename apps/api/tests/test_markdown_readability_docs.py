"""Regression tests for markdown readability guidance."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
GUIDE = ROOT / "docs/development/markdown-readability.md"
CHANGELOG = ROOT / "CHANGELOG.md"


def test_markdown_readability_guide_preserves_safety_and_triage_workflow() -> None:
    text = GUIDE.read_text(encoding="utf-8")

    assert "GNUCASH_WRITES_ENABLED=false" in text
    assert "real/private/original/only-copy GnuCash books" in text
    assert "not production-ready" in text
    assert "Status/readability triage" in text
    assert "Split long status docs before rewriting them" in text
    assert "Do not hide release/no-release decisions" in text
    assert "Public announcement docs checklist" in text
    assert "README top status is concise" in text
    assert "PROJECT_STATUS starts with a quick navigation block" in text
    assert "Recent handoff and release docs keep safety verdicts visible" in text


def test_changelog_starts_with_readable_release_navigation() -> None:
    text = CHANGELOG.read_text(encoding="utf-8")

    quick_navigation = text.index("## Quick navigation")
    unreleased = text.index("## [Unreleased]")

    assert quick_navigation < unreleased
    assert "Current public read-only beta: `v0.5.0-public-readonly-beta`" in text
    assert "`v0.5.1-public-readonly-beta` is not published" in text
    assert "Default write mode remains `GNUCASH_WRITES_ENABLED=false`" in text
    assert "No public write beta, stable release, production claim, or security-audited claim" in text
