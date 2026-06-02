"""Conservative compatibility-matrix helpers for synthetic GnuCash fixture evidence."""

from __future__ import annotations

from dataclasses import dataclass
import json
import re
from typing import Any, Literal

MatrixCategory = Literal[
    "tested_synthetic_fixture",
    "manual_fixture_blocked",
    "unclaimed_backend",
]

UNCLAIMED_BACKEND_MESSAGE = (
    "Not claimed by this pre-alpha matrix. Add synthetic/disposable fixture metadata "
    "and read-only validation before documenting support."
)
MANUAL_FIXTURE_MESSAGE = (
    "Metadata is bounded and redacted, but a Desktop-generated synthetic fixture row "
    "requires disposable/manual creation plus default-read-only validation before any "
    "Desktop-version claim."
)
TESTED_SYNTHETIC_MESSAGE = (
    "Covered only by synthetic/disposable fixture evidence; not a broad real-book, "
    "all-version, or production compatibility guarantee."
)
ACCEPTANCE_GATE_BLOCKED_MESSAGE = (
    "Desktop fixture candidate acceptance gate only; keep #22 blocked until isolated "
    "Desktop-generated synthetic evidence passes fail-closed preflight and default-read-only validation."
)

DESKTOP_VERSION_RE = re.compile(r"^GnuCash\s+\d+(?:\.\d+){1,3}$")
PATH_RE = re.compile(r"([A-Za-z]:\\[^\s]*|/[^\s]+|\\\\[^\s]+)")
AMOUNT_RE = re.compile(r"(?i)(amount\s*)\d+[.,]\d{2}")
PRIVATE_KEY_RE = re.compile(r"(?i)(path|file|dir|account|memo|description|amount|secret|token|password|key)")
PRIVATE_LABEL_RE = re.compile(r"(?i)\b(account|memo|description)\s+[^,;\n{}\[\]]+")


class CandidatePreflightError(ValueError):
    """Path-redacted Desktop fixture candidate acceptance failure."""


class CompatibilityReportError(ValueError):
    """Fail-closed compatibility report validation failure."""


@dataclass(frozen=True)
class CompatibilityMatrixRow:
    """Display-ready row with explicit claim boundaries for docs/UI."""

    category: MatrixCategory
    status: str
    fixture_origin: str
    backend: str
    desktop_version_evidence: str
    schema_markers: dict[str, int]
    table_counts: dict[str, int]
    support_claim: str
    safe_copy: str


def _clean_string(value: Any, fallback: str) -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return fallback


def _int_dict(value: Any) -> dict[str, int]:
    if not isinstance(value, dict):
        return {}
    result: dict[str, int] = {}
    for key, raw in value.items():
        if isinstance(key, str) and isinstance(raw, int):
            result[key] = raw
    return result


def _assert_no_private_candidate_evidence(metadata: dict[str, Any]) -> None:
    for key, value in metadata.items():
        if PRIVATE_KEY_RE.search(key) and key not in {"default_read_only_validation"}:
            raise CandidatePreflightError("unsafe private-looking field in desktop fixture candidate")
        text = json.dumps(value, ensure_ascii=False)
        if PATH_RE.search(text) or AMOUNT_RE.search(text) or PRIVATE_LABEL_RE.search(text):
            raise CandidatePreflightError("unsafe private-looking value in desktop fixture candidate")


def validate_desktop_fixture_candidate_preflight(metadata: dict[str, Any]) -> dict[str, str | bool]:
    """Fail-closed acceptance gate for operator-supplied Desktop fixture metadata.

    This validates only redacted/synthetic/disposable evidence. It never opens a
    GnuCash book and never accepts copied/private/path/account/memo/description/
    amount-like evidence as a Desktop-generated fixture candidate.
    """

    if not isinstance(metadata, dict):
        raise CandidatePreflightError("desktop fixture candidate must be a JSON object")
    _assert_no_private_candidate_evidence(metadata)

    if metadata.get("desktop_generated_synthetic_fixture") is not True:
        raise CandidatePreflightError("missing desktop fixture marker")
    if metadata.get("fixture_origin") != "desktop-generated-synthetic":
        raise CandidatePreflightError("missing desktop fixture marker")
    if not DESKTOP_VERSION_RE.fullmatch(_clean_string(metadata.get("gnucash_desktop_version"), "")):
        raise CandidatePreflightError("missing desktop marker/version evidence")
    if metadata.get("backend") != "SQLite":
        raise CandidatePreflightError("unsupported backend for desktop fixture candidate")
    if "fixture_scope" not in metadata:
        raise CandidatePreflightError("missing desktop fixture marker")
    if metadata.get("fixture_scope") not in {"synthetic", "disposable"}:
        raise CandidatePreflightError("desktop fixture candidate must be synthetic/disposable only")
    if metadata.get("synthetic_disposable_evidence") != "operator-created-disposable-empty-book":
        raise CandidatePreflightError("missing desktop fixture marker")
    if metadata.get("default_read_only_validation") != "passed":
        raise CandidatePreflightError("missing default read-only validation marker")

    return {
        "accepted": True,
        "backend": "SQLite",
        "fixture_origin": "desktop-generated-synthetic",
        "default_read_only_validation": "passed",
    }


def _desktop_candidate_preflight_passed(metadata: dict[str, Any]) -> bool:
    try:
        validate_desktop_fixture_candidate_preflight(metadata)
    except CandidatePreflightError:
        return False
    return True


def build_matrix_row_from_metadata(
    metadata: dict[str, Any],
    *,
    read_only_validation_passed: bool = False,
) -> CompatibilityMatrixRow:
    """Classify collector JSON without turning metadata alone into broad support.

    Collector output is allowed to feed the matrix, but classification is deliberately
    conservative: unsupported backends remain unclaimed, and Desktop-generated
    synthetic metadata stays blocked/manual until a separate read-only validation pass
    is explicitly recorded by the caller.
    """

    backend = _clean_string(metadata.get("backend"), "unknown")
    fixture_origin = _clean_string(metadata.get("fixture_origin"), "not recorded")
    versions = _int_dict(metadata.get("versions"))
    table_counts = _int_dict(metadata.get("table_counts"))
    desktop_version = _clean_string(metadata.get("gnucash_desktop_version"), "not recorded")
    desktop_generated = metadata.get("desktop_generated_synthetic_fixture") is True

    if backend != "SQLite":
        return CompatibilityMatrixRow(
            category="unclaimed_backend",
            status="unclaimed backend",
            fixture_origin=fixture_origin,
            backend=backend,
            desktop_version_evidence="not tested by this SQL/SQLite fixture matrix",
            schema_markers=versions,
            table_counts=table_counts,
            support_claim=UNCLAIMED_BACKEND_MESSAGE,
            safe_copy="No support claim; keep this backend out of tested rows until a later explicit phase.",
        )

    if desktop_generated and not read_only_validation_passed:
        return CompatibilityMatrixRow(
            category="manual_fixture_blocked",
            status="metadata captured; read-only validation still required",
            fixture_origin=fixture_origin,
            backend=backend,
            desktop_version_evidence=f"operator-supplied: {desktop_version}; not independently validated",
            schema_markers=versions,
            table_counts=table_counts,
            support_claim=MANUAL_FIXTURE_MESSAGE,
            safe_copy="Blocked/manual fixture work, not a tested Desktop-version support row.",
        )

    if desktop_generated and not _desktop_candidate_preflight_passed(metadata):
        return CompatibilityMatrixRow(
            category="manual_fixture_blocked",
            status="candidate preflight failed; keep #22 blocked",
            fixture_origin=fixture_origin,
            backend=backend,
            desktop_version_evidence=f"operator-supplied: {desktop_version}; failed acceptance preflight",
            schema_markers=versions,
            table_counts=table_counts,
            support_claim=ACCEPTANCE_GATE_BLOCKED_MESSAGE,
            safe_copy="Acceptance gate only; not a tested Desktop-version support row.",
        )

    return CompatibilityMatrixRow(
        category="tested_synthetic_fixture",
        status="tested synthetic/disposable fixture evidence",
        fixture_origin=fixture_origin,
        backend=backend,
        desktop_version_evidence=(
            "Desktop-generated synthetic fixture validated read-only"
            if desktop_generated
            else "not Desktop-version evidence"
        ),
        schema_markers=versions,
        table_counts=table_counts,
        support_claim=TESTED_SYNTHETIC_MESSAGE,
        safe_copy="Tested synthetic fixture only; no broad backend/version/real-book guarantee.",
    )


def fixture_scope_boundaries() -> dict[str, dict[str, str]]:
    """Describe public feedback fixture scopes without broadening support claims."""

    return {
        "synthetic": {
            "evidence_class": "tested-synthetic-fixture",
            "meaning": "Committed or generated synthetic SQLite fixture evidence.",
            "boundary": "Synthetic fixture only; not a compatibility guarantee for real books or Desktop versions.",
        },
        "disposable": {
            "evidence_class": "tested-disposable-report",
            "meaning": "Operator-created disposable SQLite fixture evidence reviewed as a report.",
            "boundary": "Useful for triage only; not a compatibility guarantee and not a reusable fixture row by itself.",
        },
        "copied-restorable": {
            "evidence_class": "copied-restorable-report",
            "meaning": "A copied/restorable SQLite book stayed outside git and was reported only as redacted metadata.",
            "boundary": "Private row data remains forbidden; metadata alone does not become a tested matrix row.",
        },
        "unknown": {
            "evidence_class": "unverified",
            "meaning": "Unknown scope or non-SQLite/backend-mismatched report.",
            "boundary": "No support claim; future work needs explicit safe fixtures and validation.",
        },
    }


REPORT_ONLY_UNSAFE_PHRASES = (
    "production-ready",
    "security-audited",
)


def _check_safe_report_text(report: str) -> None:
    serialized = report.lower()
    for phrase in (*unsafe_broad_support_phrases(), *REPORT_ONLY_UNSAFE_PHRASES):
        if phrase in serialized:
            raise CompatibilityReportError("unsafe broad compatibility claim in matrix report")
    if PATH_RE.search(report) or AMOUNT_RE.search(report) or PRIVATE_LABEL_RE.search(report):
        raise CompatibilityReportError("unsafe private-looking value in matrix report")


def check_compatibility_matrix_report(report: str) -> dict[str, str | bool]:
    """Validate rendered compatibility-matrix text before docs/issues use it.

    The checker intentionally accepts only conservative operator summaries and fails
    closed for broad support wording or raw private-looking evidence. It validates
    rendered text only; it never opens a GnuCash book or reads any fixture path.
    """

    if not isinstance(report, str) or not report.strip():
        raise CompatibilityReportError("compatibility matrix report must be non-empty text")
    required_fragments = (
        "Compatibility matrix operator summary",
        "synthetic and disposable evidence only",
        "Desktop and manual fixture evidence remains blocked",
        "unclaimed backend",
        "Desktop fixture candidate gate status:",
        "No production, stable, security, public-write, all-version, or real-book claim.",
    )
    for fragment in required_fragments:
        if fragment not in report:
            raise CompatibilityReportError("compatibility matrix report is missing conservative wording")
    _check_safe_report_text(report)
    return {"accepted": True, "report_class": "conservative-compatibility-matrix-summary"}


def render_compatibility_matrix_report(rows: list[CompatibilityMatrixRow]) -> str:
    """Render a conservative operator-facing compatibility summary from matrix rows.

    The renderer uses already-redacted/classified rows only. It summarizes evidence
    classes and gate state without printing raw source paths, account names,
    descriptions, memos, amounts, or broad compatibility claims.
    """

    counts: dict[str, int] = {
        "tested_synthetic_fixture": 0,
        "manual_fixture_blocked": 0,
        "unclaimed_backend": 0,
    }
    for row in rows:
        counts[row.category] = counts.get(row.category, 0) + 1

    gate_status = "blocked"
    if counts["manual_fixture_blocked"] == 0 and counts["tested_synthetic_fixture"] > 0:
        gate_status = "no blocked Desktop candidate in supplied rows"

    lines = [
        "Compatibility matrix operator summary",
        f"tested_synthetic_fixture: {counts['tested_synthetic_fixture']}",
        f"manual_fixture_blocked: {counts['manual_fixture_blocked']}",
        f"unclaimed_backend: {counts['unclaimed_backend']}",
        "Scope: synthetic and disposable evidence only.",
        "Manual blockers: Desktop and manual fixture evidence remains blocked until isolated Desktop-generated synthetic metadata passes preflight and default-read-only validation.",
        "Backend boundary: unclaimed backend rows stay outside tested support until future explicit fixtures and validation exist.",
        f"Desktop fixture candidate gate status: {gate_status}.",
        "No production, stable, security, public-write, all-version, or real-book claim.",
    ]
    report = "\n".join(lines)
    check_compatibility_matrix_report(report)
    return report


def unsafe_broad_support_phrases() -> tuple[str, ...]:
    """Phrases compatibility docs/UI must avoid unless a future release changes policy."""

    return (
        "fully compatible",
        "supports all gnucash",
        "compatible with all gnucash",
        "all versions",
        "all sql backends are supported",
        "postgresql/mysql/mariadb supported",
        "real-book compatibility guaranteed",
        "real-book compatible",
        "stable support",
        "public write support",
    )
