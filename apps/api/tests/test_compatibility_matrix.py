"""Phase 204 compatibility matrix regression tests from fixture metadata."""

from __future__ import annotations

from pathlib import Path

from app.compatibility_matrix import (
    build_matrix_row_from_metadata,
    fixture_scope_boundaries,
    unsafe_broad_support_phrases,
)

ROOT = Path(__file__).resolve().parents[3]
COMPATIBILITY_DOC = ROOT / "docs/gnucash-compatibility.md"
CHANGELOG = ROOT / "CHANGELOG.md"


def _desktop_metadata() -> dict[str, object]:
    return {
        "backend": "SQLite",
        "fixture_origin": "desktop-generated-synthetic",
        "desktop_generated_synthetic_fixture": True,
        "gnucash_desktop_version": "GnuCash 5.10",
        "versions": {"Gnucash": 3_000_000, "Gnucash-Resave": 19_920},
        "table_counts": {"accounts": 2, "transactions": 1, "splits": 1},
        "candidate_acceptance": {"accepted": True, "checked": True},
    }


def test_desktop_fixture_metadata_ingests_as_blocked_until_read_only_validation() -> None:
    row = build_matrix_row_from_metadata(_desktop_metadata())

    assert row.category == "manual_fixture_blocked"
    assert row.status == "metadata captured; read-only validation still required"
    assert row.backend == "SQLite"
    assert row.schema_markers == {"Gnucash": 3_000_000, "Gnucash-Resave": 19_920}
    assert row.table_counts["accounts"] == 2
    assert "operator-supplied: GnuCash 5.10; not independently validated" == row.desktop_version_evidence
    assert "not a tested Desktop-version support row" in row.safe_copy
    assert "requires disposable/manual creation" in row.support_claim


def test_desktop_fixture_metadata_can_only_be_tested_after_explicit_read_only_validation() -> None:
    row = build_matrix_row_from_metadata(
        _desktop_metadata(),
        read_only_validation_passed=True,
    )

    assert row.category == "tested_synthetic_fixture"
    assert row.status == "tested synthetic/disposable fixture evidence"
    assert row.desktop_version_evidence == "Desktop-generated synthetic fixture validated read-only"
    assert "no broad backend/version/real-book guarantee" in row.safe_copy


def test_non_sqlite_metadata_stays_unclaimed_backend() -> None:
    row = build_matrix_row_from_metadata(
        {
            "backend": "PostgreSQL",
            "fixture_origin": "desktop-generated-synthetic",
            "desktop_generated_synthetic_fixture": True,
            "gnucash_desktop_version": "GnuCash 5.10",
            "versions": {"Gnucash": 3_000_000},
            "table_counts": {"accounts": 2},
        },
        read_only_validation_passed=True,
    )

    assert row.category == "unclaimed_backend"
    assert row.status == "unclaimed backend"
    assert row.backend == "PostgreSQL"
    assert "Not claimed" in row.support_claim
    assert "keep this backend out of tested rows" in row.safe_copy


def test_compatibility_docs_separate_tested_blocked_and_unclaimed_sections() -> None:
    doc = COMPATIBILITY_DOC.read_text(encoding="utf-8")

    assert "## Tested synthetic/disposable fixture evidence" in doc
    assert "## Blocked/manual fixture work" in doc
    assert "## Unclaimed backends and formats" in doc
    assert "Phase 204 regression guard" in doc
    assert "metadata captured; read-only validation still required" in doc
    assert "PostgreSQL/MySQL/MariaDB GnuCash backends are unclaimed" in doc
    assert "XML books remain outside the SQL-book MVP" in doc


def test_compatibility_docs_describe_safe_public_report_evidence_classes() -> None:
    doc = COMPATIBILITY_DOC.read_text(encoding="utf-8")

    assert "Safe public compatibility feedback workflow" in doc
    assert "scripts/safe_compatibility_report.py" in doc
    assert "scripts/validate_compatibility_report.py" in doc
    assert "scripts/build_compatibility_matrix_row.py" in doc
    assert "tested-synthetic-fixture" in doc
    assert "tested-disposable-report" in doc
    assert "copied-restorable-report" in doc
    assert "unverified" in doc
    assert "not a compatibility guarantee" in doc


def test_fixture_scope_boundaries_are_explicit_and_non_claiming() -> None:
    boundaries = fixture_scope_boundaries()

    assert set(boundaries) == {"synthetic", "disposable", "copied-restorable", "unknown"}
    assert boundaries["synthetic"]["evidence_class"] == "tested-synthetic-fixture"
    assert boundaries["disposable"]["evidence_class"] == "tested-disposable-report"
    assert boundaries["copied-restorable"]["evidence_class"] == "copied-restorable-report"
    assert boundaries["unknown"]["evidence_class"] == "unverified"
    combined = " ".join(str(item) for value in boundaries.values() for item in value.values()).lower()
    assert "not a compatibility guarantee" in combined
    assert "private row data" in combined
    for phrase in unsafe_broad_support_phrases():
        assert phrase not in combined


def test_compatibility_docs_define_fixture_scope_boundaries() -> None:
    doc = COMPATIBILITY_DOC.read_text(encoding="utf-8")

    assert "## Fixture scope boundary vocabulary" in doc
    assert "`synthetic`" in doc
    assert "`disposable`" in doc
    assert "`copied-restorable`" in doc
    assert "`unknown`" in doc
    assert "private row data remains forbidden" in doc
    assert "does not become a tested matrix row" in doc


def test_compatibility_docs_and_changelog_do_not_claim_broad_support() -> None:
    combined = "\n".join(
        [
            COMPATIBILITY_DOC.read_text(encoding="utf-8"),
            CHANGELOG.read_text(encoding="utf-8"),
        ]
    ).lower()

    for phrase in unsafe_broad_support_phrases():
        assert phrase not in combined
