"""Phase 204 compatibility matrix regression tests from fixture metadata."""

from __future__ import annotations

from pathlib import Path
import subprocess
import sys

from app.compatibility_matrix import (
    CandidatePreflightError,
    CompatibilityReportError,
    build_matrix_row_from_metadata,
    check_compatibility_matrix_report,
    fixture_scope_boundaries,
    render_compatibility_matrix_report,
    summarize_compatibility_next_action,
    unsafe_broad_support_phrases,
    validate_desktop_fixture_candidate_preflight,
)

import pytest

ROOT = Path(__file__).resolve().parents[3]
COMPATIBILITY_DOC = ROOT / "docs/gnucash-compatibility.md"
CHANGELOG = ROOT / "CHANGELOG.md"
PREFLIGHT_SCRIPT = ROOT / "scripts/preflight_desktop_fixture_candidate.py"


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


def test_desktop_fixture_candidate_preflight_accepts_only_synthetic_disposable_metadata() -> None:
    result = validate_desktop_fixture_candidate_preflight(
        {
            **_desktop_metadata(),
            "fixture_scope": "synthetic",
            "synthetic_disposable_evidence": "operator-created-disposable-empty-book",
            "default_read_only_validation": "passed",
        }
    )

    assert result == {
        "accepted": True,
        "backend": "SQLite",
        "fixture_origin": "desktop-generated-synthetic",
        "default_read_only_validation": "passed",
    }


def test_desktop_fixture_candidate_preflight_fails_closed_for_missing_markers() -> None:
    unsafe = _desktop_metadata()

    with pytest.raises(CandidatePreflightError, match="missing desktop fixture marker"):
        validate_desktop_fixture_candidate_preflight(unsafe)

    with pytest.raises(CandidatePreflightError, match="default read-only validation"):
        validate_desktop_fixture_candidate_preflight(
            {
                **unsafe,
                "fixture_scope": "synthetic",
                "synthetic_disposable_evidence": "operator-created-disposable-empty-book",
            }
        )


def test_desktop_fixture_candidate_preflight_rejects_private_or_copied_evidence() -> None:
    base = {
        **_desktop_metadata(),
        "fixture_scope": "synthetic",
        "synthetic_disposable_evidence": "operator-created-disposable-empty-book",
        "default_read_only_validation": "passed",
    }
    cases = [
        {"fixture_scope": "copied-restorable"},
        {"backend": "PostgreSQL"},
        {"private_path_hint": "/home/person/book.gnucash"},
        {"diagnostic_note": "account Personal memo Lunch"},
        {"diagnostic_note": "description Sample amount 10.00"},
    ]

    for update in cases:
        with pytest.raises(CandidatePreflightError):
            validate_desktop_fixture_candidate_preflight({**base, **update})


def test_desktop_fixture_candidate_preflight_cli_redacts_rejections(tmp_path: Path) -> None:
    candidate = tmp_path / "candidate.json"
    candidate.write_text(
        """{
          "backend": "SQLite",
          "fixture_origin": "desktop-generated-synthetic",
          "desktop_generated_synthetic_fixture": true,
          "gnucash_desktop_version": "GnuCash 5.14",
          "fixture_scope": "synthetic",
          "synthetic_disposable_evidence": "operator-created-disposable-empty-book",
          "default_read_only_validation": "passed",
          "diagnostic_note": "account Personal memo Lunch"
        }""",
        encoding="utf-8",
    )

    proc = subprocess.run(
        [sys.executable, str(PREFLIGHT_SCRIPT), str(candidate)],
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=ROOT,
    )

    assert proc.returncode == 2
    assert proc.stdout == ""
    assert "unsafe private-looking value" in proc.stderr
    assert "Personal" not in proc.stderr
    assert "Lunch" not in proc.stderr


def test_desktop_fixture_metadata_can_only_be_tested_after_explicit_read_only_validation() -> None:
    metadata = {
        **_desktop_metadata(),
        "fixture_scope": "synthetic",
        "synthetic_disposable_evidence": "operator-created-disposable-empty-book",
        "default_read_only_validation": "passed",
    }
    row = build_matrix_row_from_metadata(metadata, read_only_validation_passed=True)

    assert row.category == "tested_synthetic_fixture"
    assert row.status == "tested synthetic/disposable fixture evidence"
    assert row.desktop_version_evidence == "Desktop-generated synthetic fixture validated read-only"
    assert "no broad backend/version/real-book guarantee" in row.safe_copy


def test_desktop_fixture_metadata_stays_blocked_when_preflight_marker_missing() -> None:
    row = build_matrix_row_from_metadata(_desktop_metadata(), read_only_validation_passed=True)

    assert row.category == "manual_fixture_blocked"
    assert row.status == "candidate preflight failed; keep #22 blocked"
    assert "acceptance gate only" in row.support_claim


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
    assert "redacted #22 next-action summary" in " ".join(doc.split())
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


def test_compatibility_matrix_report_renders_conservative_operator_summary() -> None:
    tested = build_matrix_row_from_metadata(
        {
            "backend": "SQLite",
            "fixture_origin": "generated-synthetic",
            "versions": {"Gnucash": 3_000_000},
            "table_counts": {"accounts": 2, "transactions": 1},
        }
    )
    blocked = build_matrix_row_from_metadata(_desktop_metadata())
    unclaimed = build_matrix_row_from_metadata({"backend": "PostgreSQL", "table_counts": {"accounts": 2}})

    report = render_compatibility_matrix_report([tested, blocked, unclaimed])

    assert "Compatibility matrix operator summary" in report
    assert "tested_synthetic_fixture: 1" in report
    assert "manual_fixture_blocked: 1" in report
    assert "unclaimed_backend: 1" in report
    assert "synthetic and disposable evidence only" in report
    assert "Desktop and manual fixture evidence remains blocked" in report
    assert "unclaimed backend" in report
    assert "Desktop fixture candidate gate status: blocked" in report
    assert check_compatibility_matrix_report(report)["accepted"] is True
    assert "/" not in report
    assert "Personal" not in report
    assert "Lunch" not in report


def test_compatibility_next_action_summary_keeps_issue_22_blocker_explicit() -> None:
    tested = build_matrix_row_from_metadata(
        {
            "backend": "SQLite",
            "fixture_origin": "generated-synthetic",
            "versions": {"Gnucash": 3_000_000},
            "table_counts": {"accounts": 2},
        }
    )
    blocked = build_matrix_row_from_metadata(_desktop_metadata())
    unclaimed = build_matrix_row_from_metadata({"backend": "PostgreSQL"})

    summary = summarize_compatibility_next_action([tested, blocked, unclaimed])

    assert summary["issue"] == "#22"
    assert summary["state"] == "blocked"
    assert "isolated Desktop-generated synthetic SQLite fixture" in summary["next_action"]
    assert "default-read-only validation" in summary["next_action"]
    assert "PostgreSQL/MySQL/MariaDB remain unclaimed" in summary["boundary"]
    assert "no broad Desktop/backend support claim" in summary["boundary"]
    serialized = " ".join(str(value) for value in summary.values())
    assert "/home" not in serialized
    assert "C:\\" not in serialized
    assert "Personal" not in serialized
    assert "Lunch" not in serialized


def test_compatibility_matrix_report_checker_fails_closed_for_unsafe_claims_and_private_values() -> None:
    unsafe_reports = [
        "Compatibility matrix operator summary\nall versions are supported",
        "Compatibility matrix operator summary\nreal-book compatible",
        "Compatibility matrix operator summary\nproduction-ready",
        "Compatibility matrix operator summary\nstable support",
        "Compatibility matrix operator summary\nsecurity-audited",
        "Compatibility matrix operator summary\npublic write support",
        "Compatibility matrix operator summary\n/private/owner/book.gnucash.sqlite",
        "Compatibility matrix operator summary\naccount Personal memo Lunch",
        "Compatibility matrix operator summary\namount 10.00",
    ]

    for report in unsafe_reports:
        with pytest.raises(CompatibilityReportError):
            check_compatibility_matrix_report(report)


def test_unsafe_broad_support_phrase_list_covers_report_checker_policy() -> None:
    phrases = unsafe_broad_support_phrases()

    assert "all versions" in phrases
    assert "real-book compatible" in phrases
    assert "stable support" in phrases
    assert "public write support" in phrases


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
