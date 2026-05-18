"""Safe helpers for copied-book dogfood preflight checks.

The helpers intentionally return redacted, filename-only summaries so a dogfood
operator can record blocker evidence without committing private account data,
private filesystem paths, screenshots, exports, or a real GnuCash book.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Literal

DogfoodStatus = Literal["blocked", "ready"]
DogfoodFindingCategory = Literal[
    "release blocker",
    "usability issue",
    "known limitation",
    "not reproducible",
]


@dataclass(frozen=True)
class DogfoodPreflightResult:
    """Redacted dogfood preflight result safe to quote in docs/issues."""

    status: DogfoodStatus
    category: DogfoodFindingCategory
    safe_label: str
    reason: str

    def safe_summary(self) -> str:
        """Return a one-line summary without private directories or full paths."""
        return (
            f"status={self.status}; category={self.category}; "
            f"book={self.safe_label}; reason={self.reason}"
        )


def check_copied_book_candidate(
    candidate_path: str | Path | None,
    *,
    repo_root: str | Path,
) -> DogfoodPreflightResult:
    """Classify whether a copied personal book is safe to use for dogfood.

    This does not open or parse the GnuCash book. It only checks the concrete
    Phase 85/86 blocker class: whether a candidate copied book path exists and
    is outside the git working tree so it cannot be accidentally committed.
    """
    if candidate_path is None or str(candidate_path).strip() == "":
        return DogfoodPreflightResult(
            status="blocked",
            category="release blocker",
            safe_label="<not configured>",
            reason="candidate book path is not configured",
        )

    candidate = Path(candidate_path).expanduser()
    safe_label = candidate.name or "<unnamed book>"

    if not candidate.exists():
        return DogfoodPreflightResult(
            status="blocked",
            category="release blocker",
            safe_label=safe_label,
            reason="candidate book path does not exist",
        )

    resolved_candidate = candidate.resolve()
    resolved_repo_root = Path(repo_root).expanduser().resolve()
    try:
        resolved_candidate.relative_to(resolved_repo_root)
    except ValueError:
        return DogfoodPreflightResult(
            status="ready",
            category="not reproducible",
            safe_label=safe_label,
            reason="candidate book exists outside the git working tree",
        )

    return DogfoodPreflightResult(
        status="blocked",
        category="release blocker",
        safe_label=safe_label,
        reason="candidate book is inside the git working tree",
    )
