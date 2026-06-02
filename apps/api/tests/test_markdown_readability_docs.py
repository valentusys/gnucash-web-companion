"""Regression tests for markdown readability guidance."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
GUIDE = ROOT / "docs/development/markdown-readability.md"
CHANGELOG = ROOT / "CHANGELOG.md"
README_RU = ROOT / "README.ru.md"
PROJECT_STATUS = ROOT / "PROJECT_STATUS.md"


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


def test_readme_ru_starts_with_compact_public_status_and_safety_navigation() -> None:
    text = README_RU.read_text(encoding="utf-8")

    status = text.index("## Текущий публичный статус")
    details = text.index("## Где смотреть подробности")
    post_release = text.index("## Последние post-release фазы")

    assert status < details < post_release
    assert "Короткая версия для review в терминале" in text
    assert "`v0.5.1-public-readonly-beta` не опубликован" in text
    assert "`v0.4.0-owner-writebeta` отложен" in text
    assert "`GNUCASH_WRITES_ENABLED=false` остаётся безопасным дефолтом" in text
    assert "real/private/original/only-copy books не являются безопасной write-целью" in text
    assert "без whole-repo reflow" in text


def test_project_status_starts_with_current_status_navigation_links() -> None:
    text = PROJECT_STATUS.read_text(encoding="utf-8")

    quick_navigation = text.index("## Quick navigation")
    current_snapshot = text.index("## Current status snapshot")
    repository = text.index("## Repository")

    assert quick_navigation < current_snapshot < repository
    assert "[README.md](README.md)" in text
    assert "[README.ru.md](README.ru.md)" in text
    assert "[#22](https://github.com/valentusys/gnucash-web-companion/issues/22)" in text
    assert "[#28](https://github.com/valentusys/gnucash-web-companion/issues/28)" in text
    assert "[#36](https://github.com/valentusys/gnucash-web-companion/issues/36)" in text
    assert "[v0.5.0-public-readonly-beta]" in text
    assert "`v0.5.1-public-readonly-beta` is not published" in text
    assert "`GNUCASH_WRITES_ENABLED=false` remains default" in text
    assert "no public write beta" in text
    assert "docs/handoff/overnight-2026-06-02-worker-07.md" in text
