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


@dataclass(frozen=True)
class WriteAlphaDogfoodPlanResult:
    """Redacted write-alpha dogfood plan preflight result.

    This helper validates only operator intent and path classes. It does not
    open, parse, copy, or mutate a GnuCash book, and it never returns absolute
    paths, account names, descriptions, memos, or amounts.
    """

    status: DogfoodStatus
    safe_label: str
    reason: str
    source_class: str
    runtime_class: str
    backup_class: str
    size_bytes: int | None = None

    def safe_summary(self) -> str:
        """Return a one-line summary without private directories or full paths."""
        fields = [
            f"status={self.status}",
            f"book={self.safe_label}",
            f"reason={self.reason}",
            f"source={self.source_class}",
            f"runtime={self.runtime_class}",
            f"backups={self.backup_class}",
        ]
        if self.size_bytes is not None:
            fields.append(f"size_bytes={self.size_bytes}")
        return "; ".join(fields)


def _is_inside(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
    except ValueError:
        return False
    return True


def _is_allowed_ignored_runtime_path(path: str | Path, *, repo_root: Path, allowed_root: str) -> bool:
    candidate = (repo_root / path).resolve() if not Path(path).is_absolute() else Path(path).resolve()
    allowed = (repo_root / allowed_root).resolve()
    return _is_inside(candidate, allowed) and candidate.name != ".gitkeep"


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
    if not _is_inside(resolved_candidate, resolved_repo_root):
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


def check_write_alpha_dogfood_plan(
    source_book_path: str | Path | None,
    *,
    repo_root: str | Path,
    disposable_copy_acknowledged: bool,
    runtime_book_path: str | Path = "data/books/write-alpha-dogfood.gnucash.sqlite",
    backup_dir_path: str | Path = "data/backups/write-alpha-dogfood",
) -> WriteAlphaDogfoodPlanResult:
    """Preflight a local-only write-alpha dogfood command path.

    The source must be an existing copied/disposable book outside the git working
    tree. The runtime copy target must be under ignored `data/books/`, backups
    under ignored `data/backups/`, and the operator must explicitly acknowledge
    that the source is not a real/private/only-copy authoritative book.
    """
    repo = Path(repo_root).expanduser().resolve()
    safe_label = "<not configured>"

    if source_book_path is None or str(source_book_path).strip() == "":
        return WriteAlphaDogfoodPlanResult(
            status="blocked",
            safe_label=safe_label,
            reason="source copied/disposable book path is not configured",
            source_class="missing",
            runtime_class="not checked",
            backup_class="not checked",
        )

    source = Path(source_book_path).expanduser()
    safe_label = source.name or "<unnamed book>"

    if not disposable_copy_acknowledged:
        return WriteAlphaDogfoodPlanResult(
            status="blocked",
            safe_label=safe_label,
            reason="disposable copied-book acknowledgement is required",
            source_class="unacknowledged",
            runtime_class="not checked",
            backup_class="not checked",
        )

    if not source.exists() or not source.is_file():
        return WriteAlphaDogfoodPlanResult(
            status="blocked",
            safe_label=safe_label,
            reason="source copied/disposable book file does not exist",
            source_class="missing",
            runtime_class="not checked",
            backup_class="not checked",
        )

    if _is_inside(source, repo):
        return WriteAlphaDogfoodPlanResult(
            status="blocked",
            safe_label=safe_label,
            reason="source copied/disposable book must stay outside the git working tree",
            source_class="inside repo",
            runtime_class="not checked",
            backup_class="not checked",
            size_bytes=source.stat().st_size,
        )

    runtime_ok = _is_allowed_ignored_runtime_path(
        runtime_book_path, repo_root=repo, allowed_root="data/books"
    )
    backup_ok = _is_allowed_ignored_runtime_path(
        backup_dir_path, repo_root=repo, allowed_root="data/backups"
    )

    if not runtime_ok:
        return WriteAlphaDogfoodPlanResult(
            status="blocked",
            safe_label=safe_label,
            reason="runtime copy target must be under ignored data/books/",
            source_class="external copied/disposable",
            runtime_class="unsafe",
            backup_class="not checked",
            size_bytes=source.stat().st_size,
        )

    if not backup_ok:
        return WriteAlphaDogfoodPlanResult(
            status="blocked",
            safe_label=safe_label,
            reason="backup directory must be under ignored data/backups/",
            source_class="external copied/disposable",
            runtime_class="ignored data/books",
            backup_class="unsafe",
            size_bytes=source.stat().st_size,
        )

    return WriteAlphaDogfoodPlanResult(
        status="ready",
        safe_label=safe_label,
        reason="write-alpha dogfood plan is local-only and ready for operator-run dry path",
        source_class="external copied/disposable",
        runtime_class="ignored data/books",
        backup_class="ignored data/backups",
        size_bytes=source.stat().st_size,
    )
