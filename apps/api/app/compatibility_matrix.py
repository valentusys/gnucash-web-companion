"""Conservative compatibility-matrix helpers for synthetic GnuCash fixture evidence."""

from __future__ import annotations

from dataclasses import dataclass
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


def unsafe_broad_support_phrases() -> tuple[str, ...]:
    """Phrases compatibility docs/UI must avoid unless a future release changes policy."""

    return (
        "fully compatible",
        "supports all gnucash",
        "compatible with all gnucash",
        "all sql backends are supported",
        "postgresql/mysql/mariadb supported",
        "production-ready compatibility",
        "real-book compatibility guaranteed",
    )
