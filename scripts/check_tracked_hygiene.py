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
    ".sqlite-shm",
    ".sqlite-wal",
    ".db",
    ".db-shm",
    ".db-wal",
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
    "PRIVATE_LOCAL_PATH:",
    "PRIVATE_LOCAL_PATH=",
    "PRIVATE_SOURCE_PATH:",
    "PRIVATE_SOURCE_PATH=",
    "PRIVATE_TARGET_PATH:",
    "PRIVATE_TARGET_PATH=",
    "PRIVATE_EVIDENCE_PATH:",
    "PRIVATE_EVIDENCE_PATH=",
    "RAW_PRIVATE_PATH:",
    "RAW_PRIVATE_PATH=",
    "ORIGINAL_GNUCASH_PATH=",
    "ONLY_COPY_GNUCASH_PATH=",
    "ORIGINAL_BOOK_PATH=",
    "ONLY_COPY_BOOK_PATH=",
    "WORKING_BOOK_PATH=",
    "LOCAL_BOOK_PATH=",
    "PRIVATE_BOOK_PATH=",
    "PRIVATE_GNUCASH_PATH=",
    "ACCOUNT_NAME=",
    "ACCOUNT_NAME:",
    "PRIVATE_ACCOUNT_NAME=",
    "PRIVATE_ACCOUNT_NAME:",
    "ACCOUNT_DESCRIPTION=",
    "ACCOUNT_DESCRIPTION:",
    "REAL_ACCOUNT_DESCRIPTION=",
    "REAL_ACCOUNT_DESCRIPTION:",
    "REAL_ACCOUNT_NAME=",
    "REAL_ACCOUNT_NAME:",
    "ACCOUNT_BALANCE=",
    "ACCOUNT_BALANCE:",
    "BALANCE=",
    "BALANCE:",
    "TRANSACTION_DESCRIPTION=",
    "TRANSACTION_DESCRIPTION:",
    "PRIVATE_TRANSACTION_DESCRIPTION=",
    "PRIVATE_TRANSACTION_DESCRIPTION:",
    "TRANSACTION_MEMO=",
    "TRANSACTION_MEMO:",
    "TRANSACTION_AMOUNT=",
    "TRANSACTION_AMOUNT:",
)

# Human-written labels are checked separately from marker tokens so that a
# lower/mixed-case heading such as "Private path: ..." cannot bypass the raw
# evidence guard. Keep these label patterns narrow to avoid blocking negative
# prose that merely discusses privacy rules.
FORBIDDEN_PRIVATE_EVIDENCE_LABEL_PATTERNS = (
    re.compile(r"^\s*(?:[-*+]\s+|>\s*)?(?:raw[ _-])?private[ _-]evidence\s*[:=]", re.I),
    re.compile(r"^\s*(?:[-*+]\s+|>\s*)?(?:unredacted[ _-])?gnucash[ _-]evidence\s*[:=]", re.I),
    re.compile(r"^\s*(?:[-*+]\s+|>\s*)?(?:raw[ _-])?private[ _-]path\s*[:=]", re.I),
    re.compile(r"^\s*(?:[-*+]\s+|>\s*)?(?:raw[ _-])?private[ _-](?:file[ _-])?path\s*[:=]", re.I),
    re.compile(r"^\s*(?:[-*+]\s+|>\s*)?(?:original|only[ _-]copy|private|real)[ _-]gnucash[ _-]path\s*[:=]", re.I),
    re.compile(r"^\s*(?:[-*+]\s+|>\s*)?(?:original|only[ _-]copy|working|local|private|real)[ _-]book[ _-]path\s*[:=]", re.I),
    re.compile(r"^\s*(?:[-*+]\s+|>\s*)?gnucash[ _-]path\s*[:=]", re.I),
    re.compile(r"^\s*(?:[-*+]\s+|>\s*)?(?:book|source|target|backup|fixture)[ _-]path\s*[:=]", re.I),
    re.compile(r"^\s*(?:[-*+]\s+|>\s*)?(?:evidence|report|output|log)[ _-]path\s*[:=]", re.I),
    re.compile(r"^\s*(?:[-*+]\s+|>\s*)?private[ _-]book[ _-]path\s*[:=]", re.I),
    re.compile(r"^\s*(?:[-*+]\s+|>\s*)?account\s*[:=]", re.I),
    re.compile(r"^\s*(?:[-*+]\s+|>\s*)?real[ _-]account[ _-]name\s*[:=]", re.I),
    re.compile(r"^\s*(?:[-*+]\s+|>\s*)?account[ _-]name\s*[:=]", re.I),
    re.compile(r"^\s*(?:[-*+]\s+|>\s*)?(?:real|private|raw)?[ _-]*account[ _-]description\s*[:=]", re.I),
    re.compile(r"^\s*(?:[-*+]\s+|>\s*)?(?:transaction[ _-])?(?:memo|amount)\s*[:=]", re.I),
    re.compile(r"^\s*(?:[-*+]\s+|>\s*)?transaction[ _-](?:description|memo|amount)\s*[:=]", re.I),
    re.compile(r"^\s*(?:[-*+]\s+|>\s*)?(?:account[ _-])?balance\s*[:=]", re.I),
)

# Tracked hygiene runs over every tracked file, so these patterns are narrower
# than the public-status wording guard and are limited to high-risk affirmative
# posture claims that should never enter committed docs, tests, or handoffs.
FORBIDDEN_UNSAFE_AFFIRMATIVE_PATTERNS = (
    re.compile(r"\bpublic\s+writes?\s+(?:is\s+|are\s+)?(?:ready|available|open|enabled|supported)\b", re.I),
    re.compile(r"\bpublic\s+write[-\s]+mode\s+(?:is\s+)?(?:ready|available|open|enabled|supported)\b", re.I),
    re.compile(r"\bpublic\s+write[-\s]+beta\s+(?:is\s+)?(?:ready|available|open|enabled|supported)\b", re.I),
    re.compile(r"\bpublic\s+write[-\s]+beta\s+(?:is\s+)?(?:approved|authorized|published|released)\b", re.I),
    re.compile(r"\bpublic\s+write[-\s]+beta\s+(?:has\s+)?(?:shipped|launched|rolled\s+out)\b", re.I),
    re.compile(r"\bpublic\s+write[-\s]+beta\s+(?:can|may)\s+(?:be\s+)?(?:used|enabled|opened|rolled\s+out)\b", re.I),
    re.compile(r"\b(?:ready\s+to|can|may|will|should)\s+(?:release|publish|ship|launch|roll\s+out|open|enable)\s+(?:the\s+)?(?:public\s+writes?|public\s+write[-\s]+mode|public\s+write[-\s]+beta|write[-\s]+beta(?:\s+(?:release|rollout|launch))?|(?:owner[-\s]+write[-\s]+beta|owner[-\s]?writebeta)(?:\s+(?:release|rollout|launch))?)\b", re.I),
    re.compile(r"\b(?:release|publish|ship|launch|roll\s+out|open|enable)\s+(?:the\s+)?(?:public\s+writes?|public\s+write[-\s]+mode|public\s+write[-\s]+beta|write[-\s]+beta(?:\s+(?:release|rollout|launch))?|(?:owner[-\s]+write[-\s]+beta|owner[-\s]?writebeta)(?:\s+(?:release|rollout|launch))?)\b", re.I),
    re.compile(r"\bpublic\s+write[-\s]+beta\s+(?:is\s+)?(?:recommended|acceptable|approved)\s+for\s+(?:use|users|public\s+use|real/private|private|real|original|only-copy)\b", re.I),
    re.compile(r"\bpublic\s+write[-\s]+beta\s+(?:launch|release|rollout)\s+(?:is\s+)?(?:ready|approved|authorized)\b", re.I),
    re.compile(r"\bwrite[-\s]+beta\s+(?:is\s+)?(?:ready|available|open|enabled|supported)\b", re.I),
    re.compile(r"\bwrite[-\s]+beta\s+(?:is\s+)?(?:approved|authorized|published|released)\b", re.I),
    re.compile(r"\bwrite[-\s]+beta\s+(?:has\s+)?(?:shipped|launched|rolled\s+out)\b", re.I),
    re.compile(r"\bwrite[-\s]+beta\s+(?:can|may)\s+(?:be\s+)?(?:used|enabled|opened|rolled\s+out)\b", re.I),
    re.compile(r"\bwrite[-\s]+beta\s+(?:is\s+)?(?:recommended|acceptable|approved)\s+for\s+(?:use|users|public\s+use|real/private|private|real|original|only-copy)\b", re.I),
    re.compile(r"\bwrite[-\s]+beta\s+(?:is\s+)?(?:safe|supported|approved|recommended|acceptable)\s+for\s+(?:real/private|private|real|original|only-copy)\s+books?\b", re.I),
    re.compile(r"\bwrite[-\s]+beta\s+(?:launch|release|rollout)\s+(?:is\s+)?(?:ready|approved|authorized|published|released)\b", re.I),
    re.compile(r"\bwrite[-\s]+beta\s+(?:is\s+)?(?:stable|production[- ]ready|production\s+ready|security[- ]audited|production[- ]grade)\b", re.I),
    re.compile(r"\bwrite[-\s]+beta\s+(?:is\s+)?(?:ga|general\s+availability|production[- ]safe|production\s+safe|field[- ]tested)\b", re.I),
    re.compile(r"\bwrite[-\s]+beta\s+(?:ga|general\s+availability)\s+(?:is\s+)?(?:ready|approved|authorized|published|released|available)\b", re.I),
    re.compile(r"\bwrite[-\s]+beta\s+(?:release|build|deployment)\s+(?:is\s+)?(?:stable|production[- ]ready|security[- ]audited)\b", re.I),
    re.compile(r"\bwrite[-\s]+mode\s+(?:is\s+)?(?:stable|production[- ]ready|security[- ]audited)\b", re.I),
    re.compile(r"\b(owner[- ]?)?writebeta\s+(?:is\s+)?(?:ready|available|open|enabled|supported)\b", re.I),
    re.compile(r"\b(owner[- ]?)?writebeta\s+(?:is\s+)?(?:public|stable|production[- ]ready|security[- ]audited|approved|authorized|published|released)\b", re.I),
    re.compile(r"\b(owner[- ]?)?writebeta\s+(?:is\s+)?(?:ga|general\s+availability|production[- ]safe|production\s+safe|field[- ]tested)\b", re.I),
    re.compile(r"\b(owner[- ]?)?writebeta\s+(?:has\s+)?(?:shipped|launched|rolled\s+out)\b", re.I),
    re.compile(r"\b(owner[- ]?)?writebeta\s+(?:launch|release|rollout)\s+(?:is\s+)?(?:ready|approved|authorized|published|released)\b", re.I),
    re.compile(r"\bowner[-\s]+write[-\s]+beta\s+(?:is\s+)?(?:ready|available|open|enabled|supported)\b", re.I),
    re.compile(r"\bowner[-\s]+write[-\s]+beta\s+(?:is\s+)?(?:public|stable|production[- ]ready|production\s+ready|security[- ]audited|approved|authorized|published|released)\b", re.I),
    re.compile(r"\bowner[-\s]+write[-\s]+beta\s+(?:is\s+)?(?:ga|general\s+availability|production[- ]safe|production\s+safe|field[- ]tested)\b", re.I),
    re.compile(r"\bowner[-\s]+write[-\s]+beta\s+(?:is\s+)?(?:safe|supported|approved|recommended|acceptable)\s+for\s+(?:real/private|private|real|original|only-copy)\s+books?\b", re.I),
    re.compile(r"\bowner[-\s]+write[-\s]+beta\s+(?:has\s+)?(?:shipped|launched|rolled\s+out)\b", re.I),
    re.compile(r"\bowner[-\s]+write[-\s]+beta\s+(?:launch|release|rollout)\s+(?:is\s+)?(?:ready|approved|authorized|published|released)\b", re.I),
    re.compile(r"\bpublic\s+write[-\s]+beta\b.*\b(?:real/private|private|real|original|only-copy)\s+books?\b", re.I),
    re.compile(r"\bbroad\s+GnuCash\s+(?:Desktop\s+)?compatibility\s+(?:is\s+)?(?:ready|available|supported|claimed|proven)\b", re.I),
    re.compile(r"\bbroad\s+GnuCash\s+(?:Desktop\s+)?compatibility\s+(?:is\s+)?(?:validated|verified|confirmed)\b", re.I),
    re.compile(r"\bbroad\s+GnuCash\s+(?:Desktop\s+)?compatibility\s+(?:is\s+)?(?:complete|comprehensive|general\s+availability|ga)\b", re.I),
    re.compile(r"\b(?:all|any|every)\s+GnuCash\s+(?:Desktop\s+)?versions?\s+(?:(?:is|are)\s+)?(?:supported|compatible|validated|confirmed)\b", re.I),
    re.compile(r"\b(?:all|any|every)\s+GnuCash\s+(?:SQL\s+)?backends?\s+(?:are\s+)?(?:supported|compatible|validated|confirmed)\b", re.I),
    re.compile(r"\ball\s+SQL\s+backends?\s+(?:are\s+)?(?:supported|compatible|validated|confirmed)\b", re.I),
    re.compile(r"\b(?:fully|guaranteed)\s+compatible\s+with\s+GnuCash\s+(?:Desktop\s+)?(?:versions?|releases?|books?|SQL\s+books?)\b", re.I),
    re.compile(r"\bproduction[- ]ready\s+compatibility\b", re.I),
    re.compile(r"\b(?:validated|verified|tested)\s+(?:against|across|on)\s+(?:all|any|every)\s+GnuCash\s+(?:Desktop\s+)?(?:versions?|releases?|books?|SQL\s+books?|SQL\s+backends?|backends?)\b", re.I),
    re.compile(r"\bcompatible\s+with\s+(?:all|any|every)\s+GnuCash\s+(?:Desktop\s+)?versions?\b", re.I),
    re.compile(r"\bworks\s+with\s+(?:all|any|every)\s+GnuCash\s+(?:Desktop\s+)?versions?\b", re.I),
    re.compile(r"\bGnuCash\s+Desktop\s+\d+(?:\.\d+){1,3}\s+(?:compatibility\s+)?(?:is\s+)?(?:supported|compatible|validated|verified|confirmed)\b", re.I),
    re.compile(r"\b(?:supports|validated|verified|confirmed)\s+GnuCash\s+Desktop\s+\d+(?:\.\d+){1,3}\b", re.I),
    re.compile(r"\bPostgreSQL/MySQL/MariaDB\s+(?:GnuCash\s+)?(?:SQL\s+)?backends?\s+(?:are\s+)?(?:supported|compatible|validated|confirmed)\b", re.I),
    re.compile(r"\b(?:real/private|private|real|only-copy)\s+(?:book\s+)?write[- ]safety\s+(?:is\s+)?(?:proven|verified|validated|confirmed|ready|safe)\b", re.I),
    re.compile(r"\b(?:real/private|private|real|original|only-copy)\s+(?:book\s+)?safety\s+(?:is\s+)?(?:proven|verified|validated|confirmed|ready|safe)\b", re.I),
    re.compile(r"\b(?:real/private|private|real|original|only-copy)\s+books?\s+(?:are\s+)?safe\s+(?:for\s+)?(?:writes?|mutation|write mode)\b", re.I),
    re.compile(r"\b(?:real/private|private|real|original|only-copy)\s+(?:book\s+)?writes?\s+(?:are\s+)?safe\b", re.I),
    re.compile(r"\bonly-copy\s+(?:books?\s+)?(?:are\s+)?safe\s+(?:for\s+)?(?:writes?|mutation|write mode)\b", re.I),
    re.compile(r"\bsafe\s+to\s+use\s+with\s+(?:real/private|private|real|original|only-copy)\s+books?\b", re.I),
    re.compile(r"\bis\s+production[- ]ready\b", re.I),
    re.compile(r"\bis\s+production\s+ready\b", re.I),
    re.compile(r"\bproduction[- ]ready\s+(release|software|deployment|build)\s+(?:is\s+)?(?:ready|published|available|supported|released)\b", re.I),
    re.compile(r"\bstable\s+(release|deployment)\s+(?:is\s+)?(?:ready|published|available|supported)\b", re.I),
    re.compile(r"\bsecurity[- ]audited\s+(release|software|deployment|build)\b", re.I),
)
FORBIDDEN_PRIVATE_BOOK_PATH_PATTERNS = (
    re.compile(
        r"(?:^|[\s`'\"(=])(?:/home/[^\s`'\")]+|/Users/[^\s`'\")]+|[A-Za-z]:\\[^\s`'\")]+)"
        r"\.(?:gnucash|gnucash\.sqlite|sqlite|sqlite3)\b",
        re.I,
    ),
)

NEGATING_WORDING_MARKERS = (
    "not ",
    "no ",
    "without ",
    "does not ",
    "do not ",
    "must not",
    "would not mean",
    "never ",
    "unclaimed",
    "blocker",
    "forbidden",
    "prevents",
    "not published",
    "unpublished",
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
            lowered_line = line.lower()
            if "never a real" in lowered_line or "not a real" in lowered_line:
                continue
            if re.match(
                r"^\s*(?:[-*+]\s+|>\s*)?(?:book|gnucash)[ _-]path\s*[:=]\s*<redacted>\s*$",
                line,
                re.I,
            ):
                continue
            for pattern in FORBIDDEN_PRIVATE_EVIDENCE_LABEL_PATTERNS:
                if pattern.search(line):
                    problems.append(
                        f"tracked raw private-evidence label in {rel}:{line_number}: {line}"
                    )
                    break
            for pattern in FORBIDDEN_PRIVATE_BOOK_PATH_PATTERNS:
                if pattern.search(line):
                    problems.append(
                        f"tracked private book path-like value in {rel}:{line_number}: {line}"
                    )
                    break
        previous_line = ""
        negative_context_lines = 0
        for line_number, line in enumerate(text.splitlines(), start=1):
            lowered = line.lower()
            current_line_is_negative = any(marker in lowered for marker in NEGATING_WORDING_MARKERS)
            wrapped_negative_context = (
                bool(re.match(r"^\s*(?:[-*+]\s+|>\s*)", line))
                or line[:1].isspace()
                or line[:1].islower()
            ) and any(marker in previous_line for marker in NEGATING_WORDING_MARKERS)
            if negative_context_lines > 0:
                if re.match(r"^\s*(?:[-*+]\s+|>\s*)", line) or not line.strip():
                    negative_context_lines -= 1
                    previous_line = lowered
                    continue
                negative_context_lines = 0
            if current_line_is_negative or wrapped_negative_context:
                if lowered.rstrip().endswith(":"):
                    negative_context_lines = 8
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
