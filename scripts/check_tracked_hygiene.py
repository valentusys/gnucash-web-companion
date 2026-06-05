#!/usr/bin/env python3
"""Fail if tracked files include private/runtime artifact classes.

This guard inspects only `git ls-files` and tracked file contents. It does not open
ignored runtime data, .env files, local books, app DBs, backups, or Hermes prompt
cache files unless they are already tracked by git.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_EXACT_NAMES = {
    ".env",
    "app.db",
}

FORBIDDEN_SUFFIXES = {
    ".bak",
    ".backup",
    ".gnucash",
    ".gnucash.sqlite",
    ".sqlite",
    ".sqlite3",
    ".db",
    ".csv",
    ".dump",
    ".ofx",
    ".qif",
    ".sql",
    ".tgz",
    ".tar",
    ".gz",
    ".zip",
    ".pem",
    ".key",
    ".p12",
    ".pfx",
    ".crt",
    ".cer",
}

FORBIDDEN_PATH_PARTS = {
    ".hermes",
    "secrets",
    "backups",
}

FORBIDDEN_SCREENSHOT_SUFFIXES = {
    ".gif",
    ".jpeg",
    ".jpg",
    ".png",
    ".webp",
}

ALLOWED_IMAGE_PREFIXES = (
    "docs/images/",
)

FORBIDDEN_PREFIXES = (
    "data/books/",
    "data/backups/",
    "data/app/",
)

PRIVATE_KEY_PREFIX = "-----BEGIN "
PRIVATE_KEY_SUFFIX = " PRIVATE KEY-----"
FORBIDDEN_CONTENT_MARKERS = (
    f"{PRIVATE_KEY_PREFIX}{PRIVATE_KEY_SUFFIX.lstrip()}",
    f"{PRIVATE_KEY_PREFIX}OPENSSH{PRIVATE_KEY_SUFFIX}",
    f"{PRIVATE_KEY_PREFIX}RSA{PRIVATE_KEY_SUFFIX}",
    f"{PRIVATE_KEY_PREFIX}EC{PRIVATE_KEY_SUFFIX}",
)


def tracked_files() -> list[Path]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=REPO_ROOT,
        check=True,
        stdout=subprocess.PIPE,
    )
    return [REPO_ROOT / item.decode() for item in result.stdout.split(b"\0") if item]


def path_violations(paths: list[Path]) -> list[str]:
    problems: list[str] = []
    for path in paths:
        rel = path.relative_to(REPO_ROOT).as_posix()
        lowered_parts = {part.lower() for part in Path(rel).parts}
        name = path.name.lower()
        suffixes = {suffix.lower() for suffix in path.suffixes}
        compound_suffix = "".join(path.suffixes).lower()
        if rel == "data/app/.gitkeep":
            continue
        if rel.startswith("apps/api/tests/fixtures/test-book") and (
            compound_suffix in {".gnucash.sqlite", ".sqlite"}
        ):
            # Historical synthetic test fixtures are intentionally tracked.
            continue
        if name in FORBIDDEN_EXACT_NAMES:
            problems.append(f"tracked forbidden filename: {rel}")
        if suffixes & FORBIDDEN_SUFFIXES or compound_suffix in FORBIDDEN_SUFFIXES:
            problems.append(f"tracked forbidden suffix: {rel}")
        if suffixes & FORBIDDEN_SCREENSHOT_SUFFIXES and not rel.startswith(ALLOWED_IMAGE_PREFIXES):
            problems.append(f"tracked possible screenshot/image artifact: {rel}")
        if lowered_parts & FORBIDDEN_PATH_PARTS:
            problems.append(f"tracked forbidden path component: {rel}")
        if rel.startswith(FORBIDDEN_PREFIXES):
            problems.append(f"tracked forbidden runtime path: {rel}")
    return problems


def content_violations(paths: list[Path]) -> list[str]:
    problems: list[str] = []
    for path in paths:
        if not path.is_file():
            continue
        try:
            data = path.read_bytes()
        except OSError as exc:
            problems.append(f"cannot read tracked file {path.relative_to(REPO_ROOT).as_posix()}: {exc.__class__.__name__}")
            continue
        if b"\0" in data:
            continue
        text = data.decode("utf-8", errors="ignore")
        for marker in FORBIDDEN_CONTENT_MARKERS:
            if marker in text:
                problems.append(f"tracked private-key marker in: {path.relative_to(REPO_ROOT).as_posix()}")
    return problems


def main() -> int:
    paths = tracked_files()
    problems = path_violations(paths) + content_violations(paths)
    if problems:
        print("Tracked hygiene check failed:", file=sys.stderr)
        for problem in problems:
            print(f"- {problem}", file=sys.stderr)
        return 1
    print(f"Tracked hygiene check passed ({len(paths)} tracked paths inspected).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
