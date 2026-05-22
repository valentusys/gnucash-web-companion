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

CURRENT_COMPLETED_PHASE = "Phase 275"
CURRENT_RELEASE_BASELINE_PHASE = "Phase 261"
CURRENT_READONLY_RELEASE = "v0.1.7-readonly"
CURRENT_WRITE_ALPHA_RELEASE = "v0.2.8-writealpha"
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
    Path("docs/release/v0.2.5-writealpha-notes.md"),
    Path("docs/release/v0.2.5-writealpha-checklist.md"),
    Path("docs/release/v0.2.5-writealpha-final-gate.md"),
    Path("docs/release/v0.2.5-writealpha-no-release-verdict.md"),
    Path("docs/release/v0.2.5-writealpha-blocker-closure.md"),
    Path("docs/release/v0.2.5-writealpha-publication-evidence.md"),
    Path("docs/release/v0.2.6-writealpha-notes.md"),
    Path("docs/release/v0.2.6-writealpha-checklist.md"),
    Path("docs/release/v0.2.6-writealpha-final-gate.md"),
    Path("docs/release/v0.2.6-writealpha-publication-evidence.md"),
    Path("docs/release/v0.2.7-writealpha-notes.md"),
    Path("docs/release/v0.2.7-writealpha-checklist.md"),
    Path("docs/release/v0.2.7-writealpha-final-gate.md"),
    Path("docs/release/v0.2.7-writealpha-publication-evidence.md"),
    Path("docs/release/v0.2.8-writealpha-notes.md"),
    Path("docs/release/v0.2.8-writealpha-checklist.md"),
    Path("docs/release/v0.2.8-writealpha-final-gate.md"),
    Path("docs/release/v0.2.8-writealpha-publication-evidence.md"),
    Path("docs/release/v0.2.9-writealpha-no-release-verdict.md"),
]

CONFIG_FILES = [
    Path(".env.example"),
    Path("docker-compose.yml"),
]

# Historical mentions are allowed in changelog/history, but not as current posture.
STALE_CURRENT_PATTERNS = [
    re.compile(r"Completed through Phase 172\b"),
    re.compile(r"Completed through Phase 228\b"),
    re.compile(r"Completed through Phase 229\b"),
    re.compile(r"Completed through Phase 230\b"),
    re.compile(r"Completed through Phase 231\b"),
    re.compile(r"Completed through Phase 232\b"),
    re.compile(r"Completed through Phase 233\b"),
    re.compile(r"Completed through Phase 234\b"),
    re.compile(r"Completed through Phase 235\b"),
    re.compile(r"Completed through Phase 236\b"),
    re.compile(r"Completed through Phase 237\b"),
    re.compile(r"Completed through Phase 238\b"),
    re.compile(r"Completed through Phase 239\b"),
    re.compile(r"Completed through Phase 240\b"),
    re.compile(r"Completed through Phase 241\b"),
    re.compile(r"Completed through Phase 242\b"),
    re.compile(r"Completed through Phase 243\b"),
    re.compile(r"Completed through Phase 244\b"),
    re.compile(r"Completed through Phase 245\b"),
    re.compile(r"Completed through Phase 246\b"),
    re.compile(r"Completed through Phase 247\b"),
    re.compile(r"Completed through Phase 248\b"),
    re.compile(r"Completed through Phase 249\b"),
    re.compile(r"Completed through Phase 250\b"),
    re.compile(r"Completed through Phase 251\b"),
    re.compile(r"Completed through Phase 252\b"),
    re.compile(r"Completed through Phase 253\b"),
    re.compile(r"Completed through Phase 254\b"),
    re.compile(r"Completed through Phase 255\b"),
    re.compile(r"Completed through Phase 256\b"),
    re.compile(r"Completed through Phase 257\b"),
    re.compile(r"Completed through Phase 258\b"),
    re.compile(r"Completed through Phase 259\b"),
    re.compile(r"Completed through Phase 260\b"),
    re.compile(r"Completed through Phase 261\b"),
    re.compile(r"Completed through Phase 262\b"),
    re.compile(r"Completed through Phase 263\b"),
    re.compile(r"Completed through Phase 264\b"),
    re.compile(r"Completed through Phase 265\b"),
    re.compile(r"Completed through Phase 266\b"),
    re.compile(r"Completed through Phase 267\b"),
    re.compile(r"Completed through Phase 268\b"),
    re.compile(r"Completed through Phase 269\b"),
    re.compile(r"Completed through Phase 270\b"),
    re.compile(r"Completed through Phase 271\b"),
    re.compile(r"Completed through Phase 272\b"),
    re.compile(r"Completed through Phase 273\b"),
    re.compile(r"Completed through Phase 274\b"),
    re.compile(r"Phase 0[–-]228 are complete"),
    re.compile(r"Phase 0[–-]229 are complete"),
    re.compile(r"Phase 0[–-]230 are complete"),
    re.compile(r"Phase 0[–-]231 are complete"),
    re.compile(r"Phase 0[–-]232 are complete"),
    re.compile(r"Phase 0[–-]233 are complete"),
    re.compile(r"Phase 0[–-]234 are complete"),
    re.compile(r"Phase 0[–-]235 are complete"),
    re.compile(r"Phase 0[–-]236 are complete"),
    re.compile(r"Phase 0[–-]237 are complete"),
    re.compile(r"Phase 0[–-]238 are complete"),
    re.compile(r"Phase 0[–-]239 are complete"),
    re.compile(r"Phase 0[–-]240 are complete"),
    re.compile(r"Phase 0[–-]241 are complete"),
    re.compile(r"Phase 0[–-]242 are complete"),
    re.compile(r"Phase 0[–-]243 are complete"),
    re.compile(r"Phase 0[–-]244 are complete"),
    re.compile(r"Phase 0[–-]245 are complete"),
    re.compile(r"Phase 0[–-]246 are complete"),
    re.compile(r"Phase 0[–-]247 are complete"),
    re.compile(r"Phase 0[–-]248 are complete"),
    re.compile(r"Phase 0[–-]249 are complete"),
    re.compile(r"Phase 0[–-]250 are complete"),
    re.compile(r"Phase 0[–-]251 are complete"),
    re.compile(r"Phase 0[–-]252 are complete"),
    re.compile(r"Phase 0[–-]253 are complete"),
    re.compile(r"Phase 0[–-]254 are complete"),
    re.compile(r"Phase 0[–-]255 are complete"),
    re.compile(r"Phase 0[–-]256 are complete"),
    re.compile(r"Phase 0[–-]257 are complete"),
    re.compile(r"Phase 0[–-]258 are complete"),
    re.compile(r"Phase 0[–-]259 are complete"),
    re.compile(r"Phase 0[–-]260 are complete"),
    re.compile(r"Phase 0[–-]261 are complete"),
    re.compile(r"Phase 0[–-]262 are complete"),
    re.compile(r"Phase 0[–-]263 are complete"),
    re.compile(r"Phase 0[–-]264 are complete"),
    re.compile(r"Phase 0[–-]265 are complete"),
    re.compile(r"Phase 0[–-]266 are complete"),
    re.compile(r"Phase 0[–-]267 are complete"),
    re.compile(r"Phase 0[–-]268 are complete"),
    re.compile(r"Phase 0[–-]269 are complete"),
    re.compile(r"Phase 0[–-]270 are complete"),
    re.compile(r"Phase 0[–-]271 are complete"),
    re.compile(r"Phase 0[–-]272 are complete"),
    re.compile(r"Phase 0[–-]273 are complete"),
    re.compile(r"Phase 0[–-]274 are complete"),
    re.compile(r"Фазы 0[–-]228 завершены"),
    re.compile(r"Фазы 0[–-]229 завершены"),
    re.compile(r"Фазы 0[–-]230 завершены"),
    re.compile(r"Фазы 0[–-]231 завершены"),
    re.compile(r"Фазы 0[–-]232 завершены"),
    re.compile(r"Фазы 0[–-]233 завершены"),
    re.compile(r"Фазы 0[–-]234 завершены"),
    re.compile(r"Фазы 0[–-]235 завершены"),
    re.compile(r"Фазы 0[–-]236 завершены"),
    re.compile(r"Фазы 0[–-]237 завершены"),
    re.compile(r"Фазы 0[–-]238 завершены"),
    re.compile(r"Фазы 0[–-]239 завершены"),
    re.compile(r"Фазы 0[–-]240 завершены"),
    re.compile(r"Фазы 0[–-]241 завершены"),
    re.compile(r"Фазы 0[–-]242 завершены"),
    re.compile(r"Фазы 0[–-]243 завершены"),
    re.compile(r"Фазы 0[–-]244 завершены"),
    re.compile(r"Фазы 0[–-]245 завершены"),
    re.compile(r"Фазы 0[–-]246 завершены"),
    re.compile(r"Фазы 0[–-]247 завершены"),
    re.compile(r"Фазы 0[–-]248 завершены"),
    re.compile(r"Фазы 0[–-]249 завершены"),
    re.compile(r"Фазы 0[–-]250 завершены"),
    re.compile(r"Фазы 0[–-]251 завершены"),
    re.compile(r"Фазы 0[–-]252 завершены"),
    re.compile(r"Фазы 0[–-]253 завершены"),
    re.compile(r"Фазы 0[–-]254 завершены"),
    re.compile(r"Фазы 0[–-]255 завершены"),
    re.compile(r"Фазы 0[–-]256 завершены"),
    re.compile(r"Фазы 0[–-]257 завершены"),
    re.compile(r"Фазы 0[–-]258 завершены"),
    re.compile(r"Фазы 0[–-]259 завершены"),
    re.compile(r"Фазы 0[–-]260 завершены"),
    re.compile(r"Фазы 0[–-]261 завершены"),
    re.compile(r"Фазы 0[–-]262 завершены"),
    re.compile(r"Фазы 0[–-]263 завершены"),
    re.compile(r"Фазы 0[–-]264 завершены"),
    re.compile(r"Фазы 0[–-]265 завершены"),
    re.compile(r"Фазы 0[–-]266 завершены"),
    re.compile(r"Фазы 0[–-]267 завершены"),
    re.compile(r"Фазы 0[–-]268 завершены"),
    re.compile(r"Фазы 0[–-]269 завершены"),
    re.compile(r"Фазы 0[–-]270 завершены"),
    re.compile(r"Фазы 0[–-]271 завершены"),
    re.compile(r"Фазы 0[–-]272 завершены"),
    re.compile(r"Фазы 0[–-]273 завершены"),
    re.compile(r"Фазы 0[–-]274 завершены"),
    re.compile(r"Current public write-alpha pre-release:\s*`v0\.2\.0-writealpha`"),
    re.compile(r"Current published write-alpha pre-release:\s*`v0\.2\.0-writealpha`"),
    re.compile(r"current public experimental write-alpha GitHub pre-release after Phase 132", re.I),
    re.compile(r"current public experimental write-alpha GitHub pre-release after Phase 211", re.I),
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
    previous_line = ""
    for line_number, line in enumerate(text.splitlines(), start=1):
        if patterns is UNSAFE_AFFIRMATIVE_PATTERNS:
            lowered = line.lower()
            context = f"{previous_line} {lowered}"
            if any(marker in context for marker in ("not ", "no ", "without", "does not", "do not")):
                previous_line = lowered
                continue
        for pattern in patterns:
            if pattern.search(line):
                raise AssertionError(
                    f"{path}:{line_number}: forbidden current-posture/status claim matched {pattern.pattern!r}: {line}"
                )
        previous_line = line.lower()


def assert_unreleased_section_is_honest(changelog: str) -> None:
    match = re.search(r"^## \[Unreleased\]\n(?P<body>.*?)(?=^## \[)", changelog, re.S | re.M)
    if not match:
        raise AssertionError("CHANGELOG.md: missing [Unreleased] section")
    body = match.group("body")
    if "v0.2.8" in body:
        raise AssertionError("CHANGELOG.md: Unreleased must not mention the current release version")
    if "v0.2.5" in body and "Phase 231" not in body:
        raise AssertionError("CHANGELOG.md: v0.2.5 references in Unreleased must be tied to the Phase 231 publication")


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
            "Phase 0–275 are complete",
            CURRENT_READONLY_RELEASE,
            CURRENT_WRITE_ALPHA_RELEASE,
            WRITE_DEFAULT,
            CURRENT_RELEASE_BASELINE_PHASE,
        ],
        Path("README.ru.md"): [
            "Фазы 0–275 завершены",
            CURRENT_READONLY_RELEASE,
            CURRENT_WRITE_ALPHA_RELEASE,
            WRITE_DEFAULT,
            CURRENT_RELEASE_BASELINE_PHASE,
        ],
        Path("PROJECT_STATUS.md"): [
            "Completed through Phase 275",
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
            "Completed through Phase 275",
            CURRENT_READONLY_RELEASE,
            CURRENT_WRITE_ALPHA_RELEASE,
            WRITE_DEFAULT,
            CURRENT_RELEASE_BASELINE_PHASE,
        ],
        Path("docs/release/v0.2.4-writealpha-notes.md"): [
            "v0.2.4-writealpha",
            "Phase 211",
            WRITE_DEFAULT,
            APP_ENV_GATE,
        ],
        Path("docs/release/v0.2.4-writealpha-checklist.md"): [
            "v0.2.4-writealpha",
            "Phase 211",
            WRITE_DEFAULT,
        ],
        Path("docs/release/v0.2.4-writealpha-final-gate.md"): [
            "v0.2.4-writealpha",
            "Phase 211",
            WRITE_DEFAULT,
        ],
        Path("docs/release/v0.2.4-writealpha-publication-evidence.md"): [
            "v0.2.4-writealpha",
            "Phase 211",
            WRITE_DEFAULT,
        ],
        Path("docs/release/v0.2.5-writealpha-notes.md"): [
            "PUBLISHED AS GITHUB PRE-RELEASE",
            "v0.2.5-writealpha",
            WRITE_DEFAULT,
            APP_ENV_GATE,
        ],
        Path("docs/release/v0.2.5-writealpha-checklist.md"): [
            "PASS — publish as GitHub pre-release",
            "v0.2.5-writealpha",
            WRITE_DEFAULT,
        ],
        Path("docs/release/v0.2.5-writealpha-final-gate.md"): [
            "PASS — publish after exact release-commit CI",
            "v0.2.5-writealpha",
            WRITE_DEFAULT,
            APP_ENV_GATE,
        ],
        Path("docs/release/v0.2.5-writealpha-no-release-verdict.md"): [
            "SUPERSEDED BY v0.2.5-writealpha PUBLICATION",
            "v0.2.5-writealpha",
            WRITE_DEFAULT,
            APP_ENV_GATE,
        ],
        Path("docs/release/v0.2.5-writealpha-blocker-closure.md"): [
            "superseded by Phase 231 publication",
            "v0.2.5-writealpha",
            WRITE_DEFAULT,
            APP_ENV_GATE,
        ],
        Path("docs/release/v0.2.5-writealpha-publication-evidence.md"): [
            "v0.2.5-writealpha",
            "Phase 231",
            WRITE_DEFAULT,
            APP_ENV_GATE,
        ],
        Path("docs/release/v0.2.6-writealpha-notes.md"): [
            "PUBLISHED AS GITHUB PRE-RELEASE",
            "v0.2.6-writealpha",
            WRITE_DEFAULT,
            APP_ENV_GATE,
            "No real/private or only-copy write safety is claimed",
        ],
        Path("docs/release/v0.2.6-writealpha-checklist.md"): [
            "PASS — publish as GitHub pre-release",
            "v0.2.6-writealpha",
            WRITE_DEFAULT,
            "PM authorization for publication",
        ],
        Path("docs/release/v0.2.6-writealpha-final-gate.md"): [
            "PASS — publish after exact release-commit CI",
            "v0.2.6-writealpha",
            WRITE_DEFAULT,
            APP_ENV_GATE,
            "PM decision: `AUTHORIZE_RELEASE`",
        ],
        Path("docs/release/v0.2.6-writealpha-publication-evidence.md"): [
            "v0.2.6-writealpha",
            "Phase 241",
            WRITE_DEFAULT,
            APP_ENV_GATE,
        ],
        Path("docs/release/v0.2.7-writealpha-notes.md"): [
            "PUBLISHED AS GITHUB PRE-RELEASE",
            "v0.2.7-writealpha",
            WRITE_DEFAULT,
            APP_ENV_GATE,
            "No real/private or only-copy write safety is claimed",
        ],
        Path("docs/release/v0.2.7-writealpha-checklist.md"): [
            "PASS — publish as GitHub pre-release",
            "v0.2.7-writealpha",
            WRITE_DEFAULT,
            "Phase 247",
        ],
        Path("docs/release/v0.2.7-writealpha-final-gate.md"): [
            "PASS — publish after exact release-commit CI",
            "v0.2.7-writealpha",
            WRITE_DEFAULT,
            APP_ENV_GATE,
            "PM decision: `AUTHORIZE_RELEASE`",
        ],
        Path("docs/release/v0.2.7-writealpha-publication-evidence.md"): [
            "v0.2.7-writealpha",
            "Phase 251",
            WRITE_DEFAULT,
            APP_ENV_GATE,
        ],
        Path("docs/release/v0.2.8-writealpha-notes.md"): [
            "PUBLISHED AS GITHUB PRE-RELEASE",
            "v0.2.8-writealpha",
            WRITE_DEFAULT,
            APP_ENV_GATE,
            "No real/private or only-copy write safety is claimed",
        ],
        Path("docs/release/v0.2.8-writealpha-checklist.md"): [
            "PASS — publish as GitHub pre-release",
            "v0.2.8-writealpha",
            WRITE_DEFAULT,
            "Phase 258",
        ],
        Path("docs/release/v0.2.8-writealpha-final-gate.md"): [
            "PASS — publish after exact release-commit CI",
            "v0.2.8-writealpha",
            WRITE_DEFAULT,
            APP_ENV_GATE,
            "PM decision: `AUTHORIZE_RELEASE`",
        ],
        Path("docs/release/v0.2.8-writealpha-publication-evidence.md"): [
            CURRENT_WRITE_ALPHA_RELEASE,
            CURRENT_RELEASE_BASELINE_PHASE,
            WRITE_DEFAULT,
            APP_ENV_GATE,
        ],
        Path("docs/release/v0.2.9-writealpha-no-release-verdict.md"): [
            "NO-RELEASE",
            "v0.2.9-writealpha",
            WRITE_DEFAULT,
            APP_ENV_GATE,
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
