"""Safe helpers for copied-book dogfood preflight checks.

The helpers intentionally return redacted, filename/class/checksum summaries so a
dogfood operator can record blocker evidence without committing private account
data, private filesystem paths, screenshots, exports, or a real GnuCash book.
"""

from __future__ import annotations

import hashlib
import subprocess
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
    parse, copy, or mutate a GnuCash book, and it never returns absolute paths,
    account names, descriptions, memos, or amounts. A ready result may include
    bounded file metadata only: size and a short checksum.
    """

    status: DogfoodStatus
    safe_label: str
    reason: str
    source_class: str
    runtime_class: str
    backup_class: str
    size_bytes: int | None = None
    checksum_sha256_12: str | None = None
    dry_run: bool = True

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
        if self.checksum_sha256_12 is not None:
            fields.append(f"sha256_12={self.checksum_sha256_12}")
        fields.append(f"dry_run={str(self.dry_run).lower()}")
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


def _redacted_book_label(path: Path) -> str:
    suffixes = "".join(path.suffixes[-2:]) if len(path.suffixes) >= 2 else path.suffix
    if not suffixes:
        suffixes = "<no extension>"
    return f"<redacted{suffixes}>"


def _looks_like_sensitive_source_path(path: Path) -> str | None:
    lowered_parts = [part.lower() for part in path.parts]
    lowered_name = path.name.lower()
    joined_parts = "/".join(lowered_parts)
    suffixes = "".join(path.suffixes).lower()
    if lowered_name == ".env" or lowered_name.startswith(".env."):
        return "source must not be an environment file"
    if lowered_name == "app.db" or "data/app" in joined_parts:
        return "source must not be an app metadata DB"
    if "backups" in lowered_parts or "backup" in lowered_parts or "backup" in lowered_name:
        return "source must not be a backup artifact or backup directory"
    if suffixes in {".bak", ".backup"}:
        return "source must not be a backup artifact or backup directory"
    return None


def _git_check_ignored(path: Path, *, repo_root: Path) -> bool:
    """Return whether git ignores path in this repository, failing closed."""
    try:
        relative = path.resolve().relative_to(repo_root.resolve())
    except ValueError:
        return False
    try:
        result = subprocess.run(
            ["git", "check-ignore", "--quiet", "--", str(relative)],
            cwd=repo_root,
            check=False,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except OSError:
        return False
    return result.returncode == 0


def _sha256_12(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()[:12]


def _repo_path(path: str | Path, *, repo_root: Path) -> Path:
    candidate = Path(path).expanduser()
    return (repo_root / candidate).resolve() if not candidate.is_absolute() else candidate.resolve()


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
    dry_run: bool = True,
) -> WriteAlphaDogfoodPlanResult:
    """Preflight a local-only write-alpha dogfood command path.

    The source must be an existing copied/disposable book outside the git working
    tree and must not be a `.env`, app metadata DB, or backup artifact. The
    runtime copy target must be under ignored `data/books/`, backups under
    ignored `data/backups/`, and the operator must explicitly acknowledge that
    the source is not a real/private/only-copy authoritative book.
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
            dry_run=dry_run,
        )

    source = Path(source_book_path).expanduser()
    safe_label = _redacted_book_label(source)

    if not disposable_copy_acknowledged:
        return WriteAlphaDogfoodPlanResult(
            status="blocked",
            safe_label=safe_label,
            reason="disposable copied-book acknowledgement is required",
            source_class="unacknowledged",
            runtime_class="not checked",
            backup_class="not checked",
            dry_run=dry_run,
        )

    if not source.exists() or not source.is_file():
        return WriteAlphaDogfoodPlanResult(
            status="blocked",
            safe_label=safe_label,
            reason="source copied/disposable book file does not exist",
            source_class="missing",
            runtime_class="not checked",
            backup_class="not checked",
            dry_run=dry_run,
        )

    source_size = source.stat().st_size
    sensitive_reason = _looks_like_sensitive_source_path(source)
    if sensitive_reason is not None:
        return WriteAlphaDogfoodPlanResult(
            status="blocked",
            safe_label=safe_label,
            reason=sensitive_reason,
            source_class="unsafe source class",
            runtime_class="not checked",
            backup_class="not checked",
            size_bytes=source_size,
            dry_run=dry_run,
        )

    if _is_inside(source, repo):
        return WriteAlphaDogfoodPlanResult(
            status="blocked",
            safe_label=safe_label,
            reason="source copied/disposable book must stay outside the git working tree",
            source_class="inside repo",
            runtime_class="not checked",
            backup_class="not checked",
            size_bytes=source_size,
            dry_run=dry_run,
        )

    runtime_candidate = _repo_path(runtime_book_path, repo_root=repo)
    backup_candidate = _repo_path(backup_dir_path, repo_root=repo)
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
            size_bytes=source_size,
            dry_run=dry_run,
        )

    if not _git_check_ignored(runtime_candidate, repo_root=repo):
        return WriteAlphaDogfoodPlanResult(
            status="blocked",
            safe_label=safe_label,
            reason="runtime copy target must be ignored by git",
            source_class="external copied/disposable",
            runtime_class="not ignored",
            backup_class="not checked",
            size_bytes=source_size,
            dry_run=dry_run,
        )

    if not backup_ok:
        return WriteAlphaDogfoodPlanResult(
            status="blocked",
            safe_label=safe_label,
            reason="backup directory must be under ignored data/backups/",
            source_class="external copied/disposable",
            runtime_class="ignored data/books",
            backup_class="unsafe",
            size_bytes=source_size,
            dry_run=dry_run,
        )

    if not _git_check_ignored(backup_candidate, repo_root=repo):
        return WriteAlphaDogfoodPlanResult(
            status="blocked",
            safe_label=safe_label,
            reason="backup directory must be ignored by git",
            source_class="external copied/disposable",
            runtime_class="ignored data/books",
            backup_class="not ignored",
            size_bytes=source_size,
            dry_run=dry_run,
        )

    return WriteAlphaDogfoodPlanResult(
        status="ready",
        safe_label=safe_label,
        reason="write-alpha copied-book preflight passed without copying or mutation",
        source_class="external copied/disposable",
        runtime_class="ignored data/books",
        backup_class="ignored data/backups",
        size_bytes=source_size,
        checksum_sha256_12=_sha256_12(source),
        dry_run=dry_run,
    )
