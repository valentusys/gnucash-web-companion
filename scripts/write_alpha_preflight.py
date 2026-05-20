#!/usr/bin/env python3
"""Local-only preflight for copied/disposable write-alpha dogfood targets.

This command performs metadata/path/environment checks only. It never opens a
GnuCash book with piecash, never copies it, never writes to it, and never emits
raw filesystem paths in normal output.
"""

from __future__ import annotations

import argparse
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Literal

Status = Literal["ready", "blocked"]

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_BACKUP_DIR = "data/backups/write-alpha-dogfood"
PRODUCTION_HINTS = {
    "gnucash",
    "finance",
    "finances",
    "accounting",
    "production",
    "prod",
    "original",
    "main",
    "primary",
    "live",
    "documents",
}
DISPOSABLE_HINTS = {
    "copy",
    "copied",
    "disposable",
    "test",
    "tmp",
    "scratch",
    "dogfood",
    "synthetic",
}


@dataclass(frozen=True)
class PreflightResult:
    status: Status
    reason: str
    target_label: str
    target_class: str
    backup_class: str
    writes_env: str
    app_env: str
    warnings: tuple[str, ...] = ()
    size_bytes: int | None = None

    def safe_summary(self) -> str:
        fields = [
            f"status={self.status}",
            f"target={self.target_label}",
            f"reason={self.reason}",
            f"target_class={self.target_class}",
            f"backup_class={self.backup_class}",
            f"GNUCASH_WRITES_ENABLED={self.writes_env}",
            f"APP_ENV={self.app_env}",
        ]
        if self.size_bytes is not None:
            fields.append(f"size_bytes={self.size_bytes}")
        if self.warnings:
            fields.append("warnings=" + ",".join(self.warnings))
        fields.append("mutation=none")
        fields.append("paths=redacted")
        return "; ".join(fields)


def _is_inside(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
    except ValueError:
        return False
    return True


def _redacted_label(path: Path | None) -> str:
    if path is None:
        return "<not configured>"
    suffixes = "".join(path.suffixes[-2:]) if len(path.suffixes) >= 2 else path.suffix
    return f"<redacted{suffixes or '<no-extension>'}>"


def _git_ignored(path: Path, *, repo_root: Path) -> bool:
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


def _resolve_input(path: str | Path, *, repo_root: Path) -> Path:
    candidate = Path(path).expanduser()
    return (repo_root / candidate).resolve() if not candidate.is_absolute() else candidate.resolve()


def _backup_class(backup_dir: str | Path, *, repo_root: Path) -> tuple[bool, str, str]:
    backup_path = _resolve_input(backup_dir, repo_root=repo_root)
    if not _is_inside(backup_path, repo_root):
        return True, "external", "backup destination is outside git working tree"
    if _git_ignored(backup_path, repo_root=repo_root):
        return True, "ignored", "backup destination is ignored by git"
    return False, "unsafe", "backup destination must be outside git or ignored by git"


def _env_status(value: str | None, *, expected: str) -> str:
    if value is None:
        return "unset"
    normalized = value.strip()
    return expected if normalized.lower() == expected.lower() else "unexpected"


def _production_warnings(path: Path) -> tuple[str, ...]:
    lowered_name = path.name.lower()
    lowered_parent = path.parent.name.lower()
    joined = f"{lowered_parent} {lowered_name}"
    has_production_hint = any(hint in joined for hint in PRODUCTION_HINTS)
    has_disposable_hint = any(hint in lowered_name for hint in DISPOSABLE_HINTS)
    if has_production_hint and not has_disposable_hint:
        return ("target-name-looks-original-or-production",)
    return ()


def _safe_block(
    reason: str,
    *,
    target: Path | None,
    target_class: str = "not checked",
    backup_class: str = "not checked",
    warnings: Iterable[str] = (),
    size_bytes: int | None = None,
) -> PreflightResult:
    return PreflightResult(
        status="blocked",
        reason=reason,
        target_label=_redacted_label(target),
        target_class=target_class,
        backup_class=backup_class,
        writes_env=_env_status(os.environ.get("GNUCASH_WRITES_ENABLED"), expected="true"),
        app_env=_env_status(os.environ.get("APP_ENV"), expected="test"),
        warnings=tuple(warnings),
        size_bytes=size_bytes,
    )


def run_preflight(
    target_path: str | Path | None,
    *,
    backup_dir: str | Path = DEFAULT_BACKUP_DIR,
    repo_root: str | Path = REPO_ROOT,
) -> PreflightResult:
    """Check whether a target path is safe enough for copied/disposable write-alpha dogfood.

    The function checks only filesystem metadata, git path class, and environment
    variables. It does not open, copy, parse, or mutate the target file.
    """
    repo = Path(repo_root).expanduser().resolve()

    if target_path is None or str(target_path).strip() == "":
        return _safe_block("explicit target path is required", target=None)

    target = Path(target_path).expanduser()
    target_label = _redacted_label(target)

    if not target.exists():
        return _safe_block(
            "target file does not exist",
            target=target,
            target_class="missing",
        )
    if not target.is_file():
        return _safe_block(
            "target must be a regular file",
            target=target,
            target_class="not file",
        )
    if not os.access(target, os.R_OK):
        return _safe_block(
            "target file is not readable",
            target=target,
            target_class="unreadable",
        )

    resolved_target = target.resolve()
    size_bytes = resolved_target.stat().st_size
    warnings = _production_warnings(resolved_target)

    if _is_inside(resolved_target, repo):
        return _safe_block(
            "target must be outside the git working tree",
            target=target,
            target_class="inside repo",
            warnings=warnings,
            size_bytes=size_bytes,
        )

    backup_ok, backup_class, backup_reason = _backup_class(backup_dir, repo_root=repo)
    if not backup_ok:
        return _safe_block(
            backup_reason,
            target=target,
            target_class="external",
            backup_class=backup_class,
            warnings=warnings,
            size_bytes=size_bytes,
        )

    writes_status = _env_status(os.environ.get("GNUCASH_WRITES_ENABLED"), expected="true")
    app_env_status = _env_status(os.environ.get("APP_ENV"), expected="test")
    if writes_status != "true":
        return PreflightResult(
            status="blocked",
            reason="GNUCASH_WRITES_ENABLED must be explicitly true for write-alpha dogfood",
            target_label=target_label,
            target_class="external",
            backup_class=backup_class,
            writes_env=writes_status,
            app_env=app_env_status,
            warnings=warnings,
            size_bytes=size_bytes,
        )
    if app_env_status != "test":
        return PreflightResult(
            status="blocked",
            reason="APP_ENV must be test for write-alpha dogfood",
            target_label=target_label,
            target_class="external",
            backup_class=backup_class,
            writes_env=writes_status,
            app_env=app_env_status,
            warnings=warnings,
            size_bytes=size_bytes,
        )

    return PreflightResult(
        status="ready",
        reason="preflight passed without opening, copying, or mutating the target",
        target_label=target_label,
        target_class="external",
        backup_class=backup_class,
        writes_env=writes_status,
        app_env=app_env_status,
        warnings=warnings,
        size_bytes=size_bytes,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Preflight one copied/disposable write-alpha target without opening the book, "
            "copying it, mutating it, or printing raw paths."
        )
    )
    parser.add_argument("target", help="Explicit path to a copied/disposable target outside this git repo")
    parser.add_argument(
        "--backup-dir",
        default=DEFAULT_BACKUP_DIR,
        help=(
            "Backup destination to validate. It must be outside this git repo or ignored by git "
            f"(default: {DEFAULT_BACKUP_DIR})."
        ),
    )
    args = parser.parse_args()

    result = run_preflight(args.target, backup_dir=args.backup_dir, repo_root=REPO_ROOT)
    print(result.safe_summary())
    return 0 if result.status == "ready" else 2


if __name__ == "__main__":
    raise SystemExit(main())
