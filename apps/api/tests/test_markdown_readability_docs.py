"""Regression tests for markdown readability guidance."""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
GUIDE = ROOT / "docs/development/markdown-readability.md"
CHANGELOG = ROOT / "CHANGELOG.md"
README_RU = ROOT / "README.ru.md"
README_EN = ROOT / "README.md"
PROJECT_STATUS = ROOT / "PROJECT_STATUS.md"
CHECKER = ROOT / "scripts/check_markdown_readability.py"
RELEASE_NOTES = ROOT / "docs/release/v0.5.0-public-readonly-beta-notes.md"
RELEASE_FINAL_GATE = ROOT / "docs/release/v0.5.0-public-readonly-beta-final-gate.md"
RELEASE_PUBLICATION_EVIDENCE = ROOT / "docs/release/v0.5.0-public-readonly-beta-publication-evidence.md"
COMPATIBILITY_DOC = ROOT / "docs/gnucash-compatibility.md"
ISSUE_28_CLOSURE_AUDIT = ROOT / "docs/development/issue-28-closure-audit.md"


def _load_checker():
    spec = importlib.util.spec_from_file_location("check_markdown_readability", CHECKER)
    assert spec is not None
    assert spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


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
    assert "### Current queue map" in text
    assert "#22 compatibility fixtures" in text
    assert "#28 Markdown source readability" in text
    assert "#36 controlled-write readiness" in text


def test_readme_ru_starts_with_compact_public_status_and_safety_navigation() -> None:
    text = README_RU.read_text(encoding="utf-8")

    status = text.index("## Текущий публичный статус")
    queue_map = text.index("## Карта открытых очередей")
    details = text.index("## Где смотреть подробности")
    post_release = text.index("## Последние post-release фазы")

    assert status < queue_map < details < post_release
    assert "Короткая версия для review в терминале" in text
    assert "`v0.5.1-public-readonly-beta` не опубликован" in text
    assert "`v0.4.0-owner-writebeta` отложен" in text
    assert "`GNUCASH_WRITES_ENABLED=false` остаётся безопасным дефолтом" in text
    assert "real/private/original/only-copy books не являются безопасной write-целью" in text
    assert "без whole-repo reflow" in text
    assert "#22" in text and "Desktop-generated synthetic SQLite fixture" in text
    assert "#28" in text and "raw Markdown" in text
    assert "#36" in text and "controlled-write readiness" in text


def test_readme_en_has_compact_public_status_and_queue_map() -> None:
    text = README_EN.read_text(encoding="utf-8")

    status = text.index("## Current status")
    queue_map = text.index("## Current queue map")
    assert status < queue_map
    assert "`v0.5.0-public-readonly-beta` remains current" in text
    assert "`v0.5.1-public-readonly-beta` is not published" in text
    assert "`GNUCASH_WRITES_ENABLED=false` remains default" in text
    assert "#22 compatibility fixtures" in text
    assert "Desktop-generated synthetic SQLite fixture" in text
    assert "#28 Markdown readability" in text
    assert "#36 controlled-write readiness" in text


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


def test_release_docs_have_conservative_readable_status_boundaries() -> None:
    notes = RELEASE_NOTES.read_text(encoding="utf-8")
    final_gate = RELEASE_FINAL_GATE.read_text(encoding="utf-8")
    publication = RELEASE_PUBLICATION_EVIDENCE.read_text(encoding="utf-8")
    checker = _load_checker()
    default_doc_names = {path.as_posix() for path in checker.DEFAULT_DOCS}

    assert "docs/release/v0.5.0-public-readonly-beta-notes.md" in default_doc_names
    assert "docs/release/v0.5.0-public-readonly-beta-final-gate.md" in default_doc_names
    assert "docs/release/v0.5.0-public-readonly-beta-publication-evidence.md" in default_doc_names
    assert "## Current public status" in notes
    assert "`v0.5.0-public-readonly-beta` is the current public read-only beta" in notes
    assert "`v0.5.1-public-readonly-beta` is not published" in notes
    assert "No public write beta" in notes
    assert "## Conservative boundaries" in final_gate
    assert "No public write beta" in final_gate
    assert "No production-ready, stable, or security-audited claim" in final_gate
    assert "## Reader shortcut" in publication
    assert "Published pre-release, not a stability claim" in publication
    assert "`v0.5.1-public-readonly-beta` is not published" in publication
    assert "No original/private/real-working/only-copy book safety claim" in publication


def test_compatibility_doc_has_readable_top_status_and_is_guarded() -> None:
    text = COMPATIBILITY_DOC.read_text(encoding="utf-8")
    checker = _load_checker()
    default_doc_names = {path.as_posix() for path in checker.DEFAULT_DOCS}

    assert "docs/gnucash-compatibility.md" in default_doc_names
    assert "Status: pre-alpha compatibility notes" in text.splitlines()[2]
    assert "#22 stays open until" in "\n".join(text.splitlines()[:30])
    assert "No real GnuCash Desktop version has been tested" in text
    assert "PostgreSQL/MySQL/MariaDB GnuCash backends are unclaimed" in text
    assert not checker.check_documents({"docs/gnucash-compatibility.md": text})


def test_compatibility_readability_guard_requires_top_blocker_navigation() -> None:
    checker = _load_checker()
    docs = {"docs/gnucash-compatibility.md": "# Compatibility\n\nStatus: read-only only.\n"}

    problems = checker.check_documents(docs)

    assert any("missing #22 Desktop fixture blocker navigation" in problem for problem in problems)


def test_markdown_readability_checker_fails_closed_for_missing_status_safety_and_links() -> None:
    checker = _load_checker()
    docs = {
        "README.md": "# README\n\nPublic overview without required status or safety signal.\n",
        "PROJECT_STATUS.md": "# Project status\n\nNo issue navigation here.\n",
        "docs/handoff/overnight-2026-06-02-worker-11.md": "# Handoff\n\nNo issue or status navigation.\n",
    }

    problems = checker.check_documents(docs)

    assert any("README.md: missing top status/safety signal" in problem for problem in problems)
    assert any("PROJECT_STATUS.md: missing issue navigation" in problem for problem in problems)
    assert any("overnight-2026-06-02-worker-11.md: missing issue or handoff navigation" in problem for problem in problems)


def test_markdown_readability_checker_flags_unstructured_long_prose_but_allows_urls_tables_and_code() -> None:
    checker = _load_checker()
    long_prose = "This is one excessively long prose line meant to be wrapped before public review because it is not a URL table row code block or generated command output and it hides readability problems in raw Markdown diffs."
    docs = {
        "README.md": "\n".join(
            [
                "# README",
                "",
                "Status: public read-only beta; writes disabled by default.",
                long_prose,
                "https://github.com/valentusys/gnucash-web-companion/issues/28/this/url/is/intentionally/long/and/allowed",
                "| Column | This deliberately long table cell is allowed because wrapping tables can make raw markdown harder to review mechanically |",
                "```text",
                long_prose,
                "```",
            ]
        )
    }

    problems = checker.check_documents(docs)

    assert any("README.md:4: long unstructured line" in problem for problem in problems)
    assert not any("README.md:5" in problem for problem in problems)
    assert not any("README.md:6" in problem for problem in problems)
    assert not any("README.md:8" in problem for problem in problems)


def test_markdown_readability_checker_requires_safety_preservation_guidance() -> None:
    checker = _load_checker()
    docs = {
        "docs/development/markdown-readability.md": "# Markdown guide\n\nWrap prose only.\n",
    }

    problems = checker.check_documents(docs)

    assert any("missing guidance that safety warnings must be preserved" in problem for problem in problems)


def test_issue_28_closure_audit_keeps_remaining_public_docs_and_safety_visible() -> None:
    text = ISSUE_28_CLOSURE_AUDIT.read_text(encoding="utf-8")

    assert "Status: keep #28 open" in text
    assert "README.md" in text
    assert "docs/community/public-readonly-beta-feedback-packet.md" in text
    assert "docs/community/announcement-draft.md" in text
    assert "scripts/check_markdown_readability.py" in text
    assert "scripts/check_public_status.py" in text
    assert "git diff --check" in text
    assert "v0.5.1-public-readonly-beta` not-published" in text
    assert "no public write beta" in text
