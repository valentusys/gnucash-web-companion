#!/usr/bin/env python3
"""Fail if tracked files include private/runtime artifact classes.

This guard inspects only `git ls-files` and tracked file contents. It does not open
ignored runtime data, .env files, local books, app DBs, backups, or Hermes prompt
cache files unless they are already tracked by git.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_EXACT_NAMES = {
    ".env",
    ".envrc",
    "app.db",
}

ALLOWED_ENV_EXAMPLE_NAMES = {
    ".env.example",
    ".env.writealpha.example",
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

# Marker-style labels are intentionally specific. They catch accidental paste of
# raw local evidence packets while avoiding false positives in redaction tests and
# safety docs that mention generic words like "amount" or "memo" negatively.
FORBIDDEN_PRIVATE_EVIDENCE_MARKERS = (
    "RAW_PRIVATE_EVIDENCE_BEGIN",
    "PRIVATE_EVIDENCE_BEGIN",
    "UNREDACTED_GNUCASH_EVIDENCE",
    "PRIVATE_PATH:",
    "PRIVATE_PATH=",
    "RAW_PRIVATE_PATH:",
    "RAW_PRIVATE_PATH=",
    "ORIGINAL_GNUCASH_PATH=",
    "ONLY_COPY_GNUCASH_PATH=",
    "PRIVATE_BOOK_PATH=",
    "PRIVATE_GNUCASH_PATH=",
    "REAL_ACCOUNT_NAME=",
    "TRANSACTION_DESCRIPTION=",
    "TRANSACTION_MEMO=",
    "TRANSACTION_AMOUNT=",
)

# Human-written labels are checked separately from marker tokens so that a
# lower/mixed-case heading such as "Private path: ..." cannot bypass the raw
# evidence guard. Keep these label patterns narrow to avoid blocking negative
# prose that merely discusses privacy rules.
FORBIDDEN_PRIVATE_EVIDENCE_LABEL_PATTERNS = (
    re.compile(r"^\s*(?:raw[ _-])?private[ _-]path\s*[:=]", re.I),
    re.compile(r"^\s*(?:original|only-copy|private|real)[ _-]gnucash[ _-]path\s*[:=]", re.I),
    re.compile(r"^\s*private[ _-]book[ _-]path\s*[:=]", re.I),
    re.compile(r"^\s*real[ _-]account[ _-]name\s*[:=]", re.I),
    re.compile(r"^\s*transaction[ _-](?:description|memo|amount)\s*[:=]", re.I),
)

# Tracked hygiene runs over every tracked file, so these patterns are narrower
# than the public-status wording guard and are limited to high-risk affirmative
# posture claims that should never enter committed docs, tests, or handoffs.
FORBIDDEN_UNSAFE_AFFIRMATIVE_PATTERNS = (
    re.compile(r"\bpublic\s+write\s+beta\s+(?:is\s+)?(?:ready|available|open|enabled|supported)\b", re.I),
    re.compile(r"\bpublic\s+write\s+beta\s+(?:launch|release|rollout)\s+(?:is\s+)?(?:ready|approved|authorized)\b", re.I),
    re.compile(r"\bbroad\s+GnuCash\s+(?:Desktop\s+)?compatibility\s+(?:is\s+)?(?:ready|available|supported|claimed|proven)\b", re.I),
    re.compile(r"\bbroad\s+GnuCash\s+(?:Desktop\s+)?compatibility\s+(?:is\s+)?(?:validated|confirmed)\b", re.I),
    re.compile(r"\bonly-copy\s+(?:books?\s+)?(?:are\s+)?safe\s+(?:for\s+)?(?:writes?|mutation|write mode)\b", re.I),
    re.compile(r"\bis\s+production[- ]ready\b", re.I),
    re.compile(r"\bproduction[- ]ready\s+(release|software|deployment|build)\s+(?:is\s+)?(?:ready|published|available|supported|released)\b", re.I),
    re.compile(r"\bstable\s+(release|deployment)\s+(?:is\s+)?(?:ready|published|available|supported)\b", re.I),
    re.compile(r"\bsecurity[- ]audited\s+(release|software|deployment|build)\b", re.I),
)

NEGATING_WORDING_MARKERS = (
    "not ",
    "no ",
    "without ",
    "does not ",
    "do not ",
    "never ",
    "unclaimed",
    "not published",
    "avoid ",
    "avoiding ",
)

UNSAFE_WORDING_SCANNED_SUFFIXES = (
    ".md",
    ".mdx",
    ".rst",
    ".txt",
)

GUARD_SELF_TEST_FILES = {
    "apps/api/tests/test_tracked_hygiene.py",
}


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
        if name.startswith(".env.") and name not in ALLOWED_ENV_EXAMPLE_NAMES:
            problems.append(f"tracked forbidden env filename: {rel}")
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
        rel = path.relative_to(REPO_ROOT).as_posix()
        if rel not in GUARD_SELF_TEST_FILES:
            for marker in FORBIDDEN_CONTENT_MARKERS:
                if marker in text:
                    problems.append(f"tracked private-key marker in: {rel}")
            tokens = text.split()
            for marker in FORBIDDEN_PRIVATE_EVIDENCE_MARKERS:
                if any(token == marker or token.startswith(marker) for token in tokens):
                    problems.append(f"tracked raw private-evidence marker {marker!r} in: {rel}")
        if path.suffix.lower() not in UNSAFE_WORDING_SCANNED_SUFFIXES:
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            for pattern in FORBIDDEN_PRIVATE_EVIDENCE_LABEL_PATTERNS:
                if pattern.search(line):
                    problems.append(
                        f"tracked raw private-evidence label in {rel}:{line_number}: {line}"
                    )
                    break
        previous_line = ""
        for line_number, line in enumerate(text.splitlines(), start=1):
            lowered = line.lower()
            context = f"{previous_line} {lowered}"
            if any(marker in context for marker in NEGATING_WORDING_MARKERS):
                previous_line = lowered
                continue
            for pattern in FORBIDDEN_UNSAFE_AFFIRMATIVE_PATTERNS:
                if pattern.search(line):
                    problems.append(
                        f"tracked unsafe affirmative wording in {rel}:{line_number}: {line}"
                    )
                    break
            previous_line = lowered
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
