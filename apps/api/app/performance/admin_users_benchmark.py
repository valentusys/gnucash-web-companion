"""Synthetic app-metadata evidence schema for issue #57 admin-user reliability.

The helpers in this module intentionally describe local synthetic app-DB samples
only. They do not open GnuCash books, do not use private data, and do not make
production performance claims.
"""

from __future__ import annotations

import statistics
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field

ADMIN_USERS_SYNTHETIC_NON_PRODUCTION_CLAIM = (
    "local synthetic app-metadata SQLite evidence only; no private books, no "
    "GnuCash source opens, and no production performance claim or wall-clock gate"
)


@dataclass(frozen=True)
class AdminUsersCaseEvidence:
    """One measured app-DB admin-user reliability/performance case."""

    name: str
    dataset: str
    sample_count: int
    repeat_count: int
    duration_ms_min: float
    duration_ms_median: float
    duration_ms_max: float
    response_bytes: int
    observed_sqlite_statement_count: int
    observed_sqlite_query_count: int
    orm_user_row_load_count: int
    orm_book_row_load_count: int
    orm_access_row_load_count: int
    preflight_open_count: int = 0
    piecash_open_count: int = 0
    gnucash_service_open_count: int = 0
    transaction_materialization_count: int = 0
    app_metadata_mutation_counts_by_operation: dict[str, int] = field(default_factory=dict)
    gnucash_mutation_capable_request_count: int = 0
    deterministic_ordering_or_pagination: bool = True
    synthetic_non_production_claim: str = ADMIN_USERS_SYNTHETIC_NON_PRODUCTION_CLAIM


def build_admin_users_case_evidence(
    *,
    name: str,
    dataset: str,
    durations_ms: Sequence[float],
    response_bytes: int,
    observed_sqlite_statement_count: int,
    observed_sqlite_query_count: int,
    orm_user_row_load_count: int,
    orm_book_row_load_count: int,
    orm_access_row_load_count: int,
    preflight_open_count: int = 0,
    piecash_open_count: int = 0,
    gnucash_service_open_count: int = 0,
    transaction_materialization_count: int = 0,
    app_metadata_mutation_counts_by_operation: Mapping[str, int] | None = None,
    gnucash_mutation_capable_request_count: int = 0,
    deterministic_ordering_or_pagination: bool = True,
) -> AdminUsersCaseEvidence:
    """Build deterministic evidence without asserting on wall-clock duration."""

    if not durations_ms:
        raise ValueError("at least one measured sample is required")
    return AdminUsersCaseEvidence(
        name=name,
        dataset=dataset,
        sample_count=len(durations_ms),
        repeat_count=len(durations_ms),
        duration_ms_min=min(durations_ms),
        duration_ms_median=float(statistics.median(durations_ms)),
        duration_ms_max=max(durations_ms),
        response_bytes=response_bytes,
        observed_sqlite_statement_count=observed_sqlite_statement_count,
        observed_sqlite_query_count=observed_sqlite_query_count,
        orm_user_row_load_count=orm_user_row_load_count,
        orm_book_row_load_count=orm_book_row_load_count,
        orm_access_row_load_count=orm_access_row_load_count,
        preflight_open_count=preflight_open_count,
        piecash_open_count=piecash_open_count,
        gnucash_service_open_count=gnucash_service_open_count,
        transaction_materialization_count=transaction_materialization_count,
        app_metadata_mutation_counts_by_operation=dict(
            app_metadata_mutation_counts_by_operation or {}
        ),
        gnucash_mutation_capable_request_count=gnucash_mutation_capable_request_count,
        deterministic_ordering_or_pagination=deterministic_ordering_or_pagination,
    )
