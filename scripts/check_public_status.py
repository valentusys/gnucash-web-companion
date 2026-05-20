#!/usr/bin/env python3
"""Guard public release/status docs against stale current-posture drift.

The check intentionally reads only tracked public documentation/configuration files.
It does not inspect .env, runtime books, app DBs, backups, or ignored data paths.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

CURRENT_COMPLETED_PHASE = "Phase 213"
CURRENT_RELEASE_BASELINE_PHASE = "Phase 211"
CURRENT_READONLY_RELEASE = "v0.1.7-readonly"
CURRENT_WRITE_ALPHA_RELEASE = "v0.2.4-writealpha"
WRITE_DEFAULT = "GNUCASH_WRITES_ENABLED=false"
APP_ENV_GATE = "APP_ENV=test"

PUBLIC_STATUS_FILES = [
    Path("README.md"),
    Path("README.ru.md"),
    Path("PROJECT_STATUS.md"),
    Path("CHANGELOG.md"),
    Path("docs/ROADMAP.md"),
    Path("docs/release/v0.2.4-writealpha-notes.md"),
    Path("docs/release/v0.2.4-writealpha-checklist.md"),
    Path("docs/release/v0.2.4-writealpha-final-gate.md"),
    Path("docs/release/v0.2.4-writealpha-publication-evidence.md"),
]

CONFIG_FILES = [
    Path(".env.example"),
    Path("docker-compose.yml"),
]

# Historical mentions are allowed in changelog/history, but not as current posture.
STALE_CURRENT_PATTERNS = [
    re.compile(r"Completed through Phase 172\b"),
    re.compile(r"Current public write-alpha pre-release:\s*`v0\.2\.0-writealpha`"),
    re.compile(r"Current published write-alpha pre-release:\s*`v0\.2\.0-writealpha`"),
    re.compile(r"current public experimental write-alpha GitHub pre-release after Phase 132", re.I),
]

UNSAFE_AFFIRMATIVE_PATTERNS = [
    re.compile(r"\bis production[- ]ready\b", re.I),
    re.compile(r"\bproduction[- ]ready\s+(release|software|deployment|build)\b", re.I),
    re.compile(r"\bsecurity[- ]audited\s+(release|software|deployment|build)\b", re.I),
    re.compile(r"\bstable\s+(release|production|write mode|deployment)\b", re.I),
    re.compile(r"\bsafe\s+for\s+real/private\b", re.I),
    re.compile(r"\bsafe\s+production\s+write\s+mode\b", re.I),
]


def read_public_text(path: Path) -> str:
    full_path = REPO_ROOT / path
    if not full_path.is_file():
        raise AssertionError(f"missing required public status file: {path}")
    return full_path.read_text(encoding="utf-8")


def require_contains(path: Path, text: str, needles: list[str]) -> None:
    missing = [needle for needle in needles if needle not in text]
    if missing:
        raise AssertionError(f"{path}: missing required current-posture text: {missing}")


def reject_patterns(path: Path, text: str, patterns: list[re.Pattern[str]]) -> None:
    for line_number, line in enumerate(text.splitlines(), start=1):
        if patterns is UNSAFE_AFFIRMATIVE_PATTERNS:
            lowered = line.lower()
            if any(marker in lowered for marker in ("not ", "no ", "without", "does not", "do not")):
                continue
        for pattern in patterns:
            if pattern.search(line):
                raise AssertionError(
                    f"{path}:{line_number}: forbidden current-posture/status claim matched {pattern.pattern!r}: {line}"
                )


def assert_unreleased_section_is_honest(changelog: str) -> None:
    match = re.search(r"^## \[Unreleased\]\n(?P<body>.*?)(?=^## \[)", changelog, re.S | re.M)
    if not match:
        raise AssertionError("CHANGELOG.md: missing [Unreleased] section")
    body = match.group("body")
    if "v0.2.5" in body:
        raise AssertionError("CHANGELOG.md: Unreleased must not claim the next release version")
    affirmative_publication = re.search(r"\b(published|publication created|released as)\b", body, re.I)
    if affirmative_publication and "No release was published" not in body:
        raise AssertionError("CHANGELOG.md: Unreleased must not claim a new release/publication")


def main() -> int:
    errors: list[str] = []
    texts: dict[Path, str] = {}

    try:
        for path in PUBLIC_STATUS_FILES + CONFIG_FILES:
            texts[path] = read_public_text(path)
    except AssertionError as exc:
        errors.append(str(exc))

    checks = {
        Path("README.md"): [
            "Phase 0–213 are complete",
            CURRENT_READONLY_RELEASE,
            CURRENT_WRITE_ALPHA_RELEASE,
            WRITE_DEFAULT,
            CURRENT_RELEASE_BASELINE_PHASE,
        ],
        Path("README.ru.md"): [
            "Фазы 0–213 завершены",
            CURRENT_READONLY_RELEASE,
            CURRENT_WRITE_ALPHA_RELEASE,
            WRITE_DEFAULT,
            CURRENT_RELEASE_BASELINE_PHASE,
        ],
        Path("PROJECT_STATUS.md"): [
            "Completed through Phase 213",
            CURRENT_READONLY_RELEASE,
            CURRENT_WRITE_ALPHA_RELEASE,
            WRITE_DEFAULT,
            APP_ENV_GATE,
        ],
        Path("CHANGELOG.md"): [
            CURRENT_COMPLETED_PHASE,
            CURRENT_READONLY_RELEASE,
            CURRENT_WRITE_ALPHA_RELEASE,
            WRITE_DEFAULT,
        ],
        Path("docs/ROADMAP.md"): [
            "Completed through Phase 213",
            CURRENT_READONLY_RELEASE,
            CURRENT_WRITE_ALPHA_RELEASE,
            WRITE_DEFAULT,
            CURRENT_RELEASE_BASELINE_PHASE,
        ],
        Path("docs/release/v0.2.4-writealpha-notes.md"): [
            CURRENT_WRITE_ALPHA_RELEASE,
            CURRENT_RELEASE_BASELINE_PHASE,
            WRITE_DEFAULT,
            APP_ENV_GATE,
        ],
        Path("docs/release/v0.2.4-writealpha-checklist.md"): [
            CURRENT_WRITE_ALPHA_RELEASE,
            CURRENT_RELEASE_BASELINE_PHASE,
            WRITE_DEFAULT,
        ],
        Path("docs/release/v0.2.4-writealpha-final-gate.md"): [
            CURRENT_WRITE_ALPHA_RELEASE,
            CURRENT_RELEASE_BASELINE_PHASE,
            WRITE_DEFAULT,
        ],
        Path("docs/release/v0.2.4-writealpha-publication-evidence.md"): [
            CURRENT_WRITE_ALPHA_RELEASE,
            CURRENT_RELEASE_BASELINE_PHASE,
            WRITE_DEFAULT,
        ],
        Path(".env.example"): [WRITE_DEFAULT],
        Path("docker-compose.yml"): ["GNUCASH_WRITES_ENABLED=${GNUCASH_WRITES_ENABLED:-false}"],
    }

    for path, needles in checks.items():
        if path in texts:
            try:
                require_contains(path, texts[path], needles)
            except AssertionError as exc:
                errors.append(str(exc))

    for path in PUBLIC_STATUS_FILES:
        if path in texts:
            try:
                reject_patterns(path, texts[path], STALE_CURRENT_PATTERNS)
                reject_patterns(path, texts[path], UNSAFE_AFFIRMATIVE_PATTERNS)
            except AssertionError as exc:
                errors.append(str(exc))

    if Path("CHANGELOG.md") in texts:
        try:
            assert_unreleased_section_is_honest(texts[Path("CHANGELOG.md")])
        except AssertionError as exc:
            errors.append(str(exc))

    if errors:
        for error in errors:
            print(f"public-status-guard: {error}", file=sys.stderr)
        return 1

    print("public-status-guard: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
