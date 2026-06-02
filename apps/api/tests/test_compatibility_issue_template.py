"""Regression guards for safe compatibility issue templates."""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
TEMPLATE = ROOT / ".github" / "ISSUE_TEMPLATE" / "compatibility-report.yml"


def _template_text() -> str:
    return TEMPLATE.read_text(encoding="utf-8")


def test_compatibility_issue_template_requests_only_safe_metadata_fields() -> None:
    text = _template_text()

    for required in (
        "Operating system",
        "Browser family/version",
        "Docker/runtime version",
        "GnuCash version",
        "GnuCash backend type",
        "Book/test scope",
        "Generic error class",
    ):
        assert required in text

    assert "synthetic" in text
    assert "disposable" in text
    assert "copied-restorable" in text
    assert "unknown" in text


def test_compatibility_issue_template_forbids_private_artifacts_and_raw_financial_data() -> None:
    text = _template_text().lower()

    for forbidden_prompt in (
        "do not upload gnucash books",
        "app dbs",
        "backups",
        "csv exports",
        "screenshots",
        ".env files",
        "tokens",
        "private paths",
        "account names",
        "transaction descriptions",
        "memos",
        "amounts",
    ):
        assert forbidden_prompt in text

    assert "safe_compatibility_report.py" in text
    assert "validate_compatibility_report.py" in text


def test_compatibility_issue_template_avoids_broad_support_claim_language() -> None:
    text = _template_text().lower()

    for unsafe_phrase in (
        "fully compatible",
        "supports all gnucash",
        "compatible with all gnucash",
        "production-ready compatibility",
        "real-book compatibility guaranteed",
    ):
        assert unsafe_phrase not in text

    assert "not a compatibility guarantee" in text
