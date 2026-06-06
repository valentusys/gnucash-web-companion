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
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.check_write_safety_defaults import _check as check_write_safety_files

CURRENT_COMPLETED_PHASE = "Phase 830"
CURRENT_RELEASE_BASELINE_PHASE = "Phase 261"
CURRENT_READONLY_RELEASE = "v0.5.0-public-readonly-beta"
CURRENT_WRITE_ALPHA_RELEASE = "v0.2.8-writealpha"
WRITE_DEFAULT = "GNUCASH_WRITES_ENABLED=false"
APP_ENV_GATE = "APP_ENV=test"


def _completed_phase_number() -> int:
    match = re.search(r"\bPhase\s+(\d+)\b", CURRENT_COMPLETED_PHASE)
    if not match:
        raise ValueError(f"invalid CURRENT_COMPLETED_PHASE: {CURRENT_COMPLETED_PHASE!r}")
    return int(match.group(1))


def _generated_stale_current_patterns(start_phase: int = 320) -> list[re.Pattern[str]]:
    """Generate stale public-current posture patterns up to the current phase.

    The public-status guard advances frequently. Generated patterns prevent the
    stale baseline guard from silently stopping at an older phase range while
    current docs have moved forward.
    """

    current_phase = _completed_phase_number()
    if start_phase >= current_phase:
        return []

    patterns: list[re.Pattern[str]] = []
    for phase in range(start_phase, current_phase):
        patterns.extend(
            [
                re.compile(
                    rf"Completed through Phase {phase}\b"
                    rf"(?!(?: was| were) (?:the )?(?:prior|previous|historical)\b)"
                ),
                re.compile(rf"Phase 0[–-]{phase} are complete"),
                re.compile(rf"Фазы 0[–-]{phase} завершены"),
            ]
        )
    return patterns


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
    Path("docs/release/v0.2.10-writealpha-no-release-verdict.md"),
]

CONFIG_FILES = [
    Path(".env.example"),
    Path("docker-compose.yml"),
]
CURRENT_BASELINE_STATUS_FILES = [
    Path("README.md"),
    Path("README.ru.md"),
    Path("docs/ROADMAP.md"),
]
COMPATIBILITY_STATUS_FILES = [
    Path("docs/gnucash-compatibility.md"),
]
DEFAULT_WRITE_SAFETY_GUARD_FILES = (
    Path(".env.example"),
    Path("docker-compose.yml"),
    Path("docs/write-alpha/owner-writebeta-operating-guide.md"),
)

# Historical mentions are allowed in changelog/history, but not as current posture.
def _legacy_stale_current_patterns() -> list[re.Pattern[str]]:
    """Return pre-generated stale public-current posture patterns.

    Older phase baselines are kept in a compact generator so the guard stays
    reviewable while preserving the legacy ranges that were intentionally
    checked before the newer auto-generated phase window starts.
    """

    patterns: list[re.Pattern[str]] = [
        re.compile(r"Completed through Phase 172\b"),
    ]
    for phase in range(228, 320):
        patterns.extend(
            [
                re.compile(rf"Completed through Phase {phase}\b"),
                re.compile(rf"Phase 0[–-]{phase} are complete"),
                re.compile(rf"Фазы 0[–-]{phase} завершены"),
            ]
        )
    patterns.extend(
        [
            re.compile(r"Current public write-alpha pre-release:\s*`v0\.2\.0-writealpha`"),
            re.compile(r"Current published write-alpha pre-release:\s*`v0\.2\.0-writealpha`"),
            re.compile(r"current public experimental write-alpha GitHub pre-release after Phase 132", re.I),
            re.compile(r"current public experimental write-alpha GitHub pre-release after Phase 211", re.I),
        ]
    )
    return patterns


STALE_CURRENT_PATTERNS = _legacy_stale_current_patterns()
RECENT_STALE_CURRENT_PATTERNS = _generated_stale_current_patterns()

UNSAFE_AFFIRMATIVE_PATTERNS = [
    re.compile(r"\bpublic\s+writes?\s+(?:is\s+|are\s+)?(?:ready|available|open|enabled|supported)\b", re.I),
    re.compile(r"\bpublic\s+write[-\s]+mode\s+(?:is\s+)?(?:ready|available|open|enabled|supported)\b", re.I),
    re.compile(r"\bpublic\s+write[-\s]+beta\s+(?:is\s+)?(?:ready|available|open|enabled|supported)\b", re.I),
    re.compile(r"\bpublic\s+write[-\s]+beta\s+(?:is\s+)?(?:approved|authorized|published|released)\b", re.I),
    re.compile(r"\bpublic\s+write[-\s]+beta\s+(?:has\s+)?(?:shipped|launched|rolled\s+out)\b", re.I),
    re.compile(r"\bpublic\s+write[-\s]+beta\s+(?:can|may)\s+(?:be\s+)?(?:used|enabled|opened|rolled\s+out)\b", re.I),
    re.compile(r"\b(?:ready\s+to|can|may|will|should)\s+(?:release|publish|ship|launch|roll\s+out|open|enable)\s+(?:the\s+)?(?:public\s+writes?|public\s+write[-\s]+mode|public\s+write[-\s]+beta|write[-\s]+beta(?:\s+(?:release|rollout|launch))?|owner[-\s]?writebeta(?:\s+(?:release|rollout|launch))?)\b", re.I),
    re.compile(r"\b(?:release|publish|ship|launch|roll\s+out|open|enable)\s+(?:the\s+)?(?:public\s+writes?|public\s+write[-\s]+mode|public\s+write[-\s]+beta|write[-\s]+beta(?:\s+(?:release|rollout|launch))?|owner[-\s]?writebeta(?:\s+(?:release|rollout|launch))?)\b", re.I),
    re.compile(r"\bpublic\s+write[-\s]+beta\s+(?:is\s+)?(?:recommended|acceptable|approved)\s+for\s+(?:use|users|public\s+use|real/private|private|real|original|only-copy)\b", re.I),
    re.compile(r"\bpublic\s+write[-\s]+beta\s+(?:launch|release|rollout)\s+(?:is\s+)?(?:ready|approved|authorized)\b", re.I),
    re.compile(r"\bwrite[-\s]+beta\s+(?:is\s+)?(?:ready|available|open|enabled|supported)\b", re.I),
    re.compile(r"\bwrite[-\s]+beta\s+(?:is\s+)?(?:approved|authorized|published|released)\b", re.I),
    re.compile(r"\bwrite[-\s]+beta\s+(?:has\s+)?(?:shipped|launched|rolled\s+out)\b", re.I),
    re.compile(r"\bwrite[-\s]+beta\s+(?:can|may)\s+(?:be\s+)?(?:used|enabled|opened|rolled\s+out)\b", re.I),
    re.compile(r"\bwrite[-\s]+beta\s+(?:is\s+)?(?:recommended|acceptable|approved)\s+for\s+(?:use|users|public\s+use|real/private|private|real|original|only-copy)\b", re.I),
    re.compile(r"\bwrite[-\s]+beta\s+(?:launch|release|rollout)\s+(?:is\s+)?(?:ready|approved|authorized|published|released)\b", re.I),
    re.compile(r"\bwrite[-\s]+beta\s+(?:is\s+)?(?:stable|production[- ]ready|security[- ]audited|production[- ]grade)\b", re.I),
    re.compile(r"\bwrite[-\s]+beta\s+(?:release|build|deployment)\s+(?:is\s+)?(?:stable|production[- ]ready|security[- ]audited)\b", re.I),
    re.compile(r"\bwrite[-\s]+mode\s+(?:is\s+)?(?:stable|production[- ]ready|security[- ]audited)\b", re.I),
    re.compile(r"\b(owner[- ]?)?writebeta\s+(?:is\s+)?(?:ready|available|open|enabled|supported)\b", re.I),
    re.compile(r"\b(owner[- ]?)?writebeta\s+(?:is\s+)?(?:public|stable|production[- ]ready|security[- ]audited)\b", re.I),
    re.compile(r"\b(owner[- ]?)?writebeta\s+(?:is\s+)?(?:approved|authorized|published|released)\b", re.I),
    re.compile(r"\b(owner[- ]?)?writebeta\s+(?:has\s+)?(?:shipped|launched|rolled\s+out)\b", re.I),
    re.compile(r"\b(owner[- ]?)?writebeta\s+(?:launch|release|rollout)\s+(?:is\s+)?(?:ready|approved|authorized|published|released)\b", re.I),
    re.compile(r"\bpublic\s+write[-\s]+beta\b.*\b(?:real/private|private|real|original|only-copy)\s+books?\b", re.I),
    re.compile(r"\bis production[- ]ready\b", re.I),
    re.compile(r"\bproduction[- ]ready\s+(release|software|deployment|build)\b", re.I),
    re.compile(r"\bsecurity[- ]audited\s+(release|software|deployment|build)\b", re.I),
    re.compile(r"\bstable\s+(release|production|write mode|deployment)\b", re.I),
    re.compile(r"\bsafe\s+for\s+real/private\b", re.I),
    re.compile(r"\bsafe\s+production\s+write\s+mode\b", re.I),
    re.compile(r"\bbroad\s+GnuCash\s+(?:Desktop\s+)?compatibility\s+(?:is\s+)?(?:ready|available|supported|claimed|proven|validated|confirmed)\b", re.I),
    re.compile(r"\ball\s+GnuCash\s+(?:versions|backends)\s+(?:are\s+)?(?:supported|compatible|write[- ]compatible)\b", re.I),
    re.compile(r"\bany\s+GnuCash\s+(?:versions|backends)\s+(?:are\s+)?(?:supported|compatible|write[- ]compatible)\b", re.I),
    re.compile(r"\ball\s+SQL\s+backends?\s+(?:are\s+)?(?:supported|compatible|validated|confirmed)\b", re.I),
    re.compile(r"\b(?:fully|guaranteed)\s+compatible\s+with\s+GnuCash\s+(?:Desktop\s+)?(?:versions?|releases?|books?|SQL\s+books?)\b", re.I),
    re.compile(r"\bproduction[- ]ready\s+compatibility\b", re.I),
    re.compile(r"\b(?:validated|verified|tested)\s+(?:against|across|on)\s+(?:all|any)\s+GnuCash\s+(?:Desktop\s+)?(?:versions?|releases?|books?|SQL\s+books?|backends?)\b", re.I),
    re.compile(r"\bworks\s+with\s+(?:all|any)\s+GnuCash\s+(?:Desktop\s+)?versions?\b", re.I),
    re.compile(r"\b(?:real/private|private|real|only-copy)\s+(?:book\s+)?write[- ]safety\s+(?:is\s+)?(?:proven|verified|ready|safe)\b", re.I),
    re.compile(r"\b(?:real/private|private|real|original|only-copy)\s+books?\s+(?:are\s+)?safe\s+(?:for\s+)?(?:writes?|mutation|write mode)\b", re.I),
    re.compile(r"\b(?:real/private|private|real|original|only-copy)\s+(?:book\s+)?writes?\s+(?:are\s+)?safe\b", re.I),
    re.compile(r"\bonly-copy\s+(?:books?\s+)?(?:are\s+)?safe\s+(?:for\s+)?(?:writes?|mutation|write mode)\b", re.I),
    re.compile(r"\bsafe\s+to\s+use\s+with\s+(?:real/private|private|real|original|only-copy)\s+books?\b", re.I),
]

COMPATIBILITY_REQUIRED_FRAGMENTS = [
    "Issue #22 is closed for narrow Desktop-generated synthetic SQLite fixture evidence only",
    "Compatibility evidence is based on synthetic/disposable fixtures only",
    "PostgreSQL/MySQL/MariaDB GnuCash backends are unclaimed",
    "No broad GnuCash Desktop version support is claimed",
]
COMPATIBILITY_UNSAFE_CLAIM_PATTERNS = [
    re.compile(r"\bGnuCash\s+Desktop\s+\d+(?:\.\d+){1,3}\s+(?:is\s+)?supported\b", re.I),
    re.compile(r"\bsupports\s+GnuCash\s+Desktop\s+\d+(?:\.\d+){1,3}\b", re.I),
    re.compile(r"\bDesktop-version\s+support\b", re.I),
    re.compile(r"\bPostgreSQL/MySQL/MariaDB\s+supported\b", re.I),
    re.compile(r"\ball\s+SQL\s+backends\s+(?:are\s+)?supported\b", re.I),
]


def check_compatibility_status_claims(path: Path, text: str) -> None:
    """Guard #22 compatibility docs against broad Desktop/backend support drift."""

    normalized_text = " ".join(text.split())
    missing = [needle for needle in COMPATIBILITY_REQUIRED_FRAGMENTS if needle not in normalized_text]
    if missing:
        raise AssertionError(f"{path}: missing required current-posture text: {missing}")
    previous_line = ""
    for line_number, line in enumerate(text.splitlines(), start=1):
        lowered = line.lower()
        if any(marker in lowered for marker in ("not ", "no ", "without", "does not", "do not", "unclaimed")):
            previous_line = lowered
            continue
        for pattern in COMPATIBILITY_UNSAFE_CLAIM_PATTERNS:
            if pattern.search(line):
                raise AssertionError(
                    f"{path}:{line_number}: forbidden compatibility claim matched {pattern.pattern!r}: {line}"
                )
        previous_line = line.lower()


def read_public_text(path: Path) -> str:
    full_path = REPO_ROOT / path
    if not full_path.is_file():
        raise AssertionError(f"missing required public status file: {path}")
    return full_path.read_text(encoding="utf-8")


def require_contains(path: Path, text: str, needles: list[str]) -> None:
    missing = [needle for needle in needles if needle not in text]
    if missing:
        raise AssertionError(f"{path}: missing required current-posture text: {missing}")


NEGATION_MARKERS = (
    "not ",
    "no ",
    "without",
    "does not",
    "do not",
    "must not",
    "would not mean",
    "avoiding",
    "avoid ",
    "deny ",
    "denies ",
    "denied ",
    "blocker",
    "forbidden",
    "prevents",
    "unpublished",
)


def reject_patterns(path: Path, text: str, patterns: list[re.Pattern[str]]) -> None:
    previous_line = ""
    negative_context_lines = 0
    for line_number, line in enumerate(text.splitlines(), start=1):
        if patterns is UNSAFE_AFFIRMATIVE_PATTERNS:
            lowered = line.lower()
            current_line_is_negative = any(marker in lowered for marker in NEGATION_MARKERS)
            wrapped_negative_context = (
                line[:1].isspace()
                or line[:1].islower()
                or previous_line.rstrip().endswith((",", " or", " and", " no"))
            ) and any(marker in previous_line for marker in NEGATION_MARKERS)
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
    if "v0.2.8" in body and "current public releases remain" not in body.lower():
        raise AssertionError("CHANGELOG.md: Unreleased must mention the current release version only as unchanged current-release posture")
    if "v0.2.5" in body and "Phase 231" not in body:
        raise AssertionError("CHANGELOG.md: v0.2.5 references in Unreleased must be tied to the Phase 231 publication")


def check_default_write_safety() -> list[str]:
    """Run the dedicated committed-default write-safety guard for public status."""

    env_example, compose, gate_doc = (REPO_ROOT / path for path in DEFAULT_WRITE_SAFETY_GUARD_FILES)
    return check_write_safety_files(env_example, compose, gate_doc)


def main() -> int:
    errors: list[str] = []
    texts: dict[Path, str] = {}

    try:
        for path in PUBLIC_STATUS_FILES + CONFIG_FILES + COMPATIBILITY_STATUS_FILES:
            texts[path] = read_public_text(path)
    except AssertionError as exc:
        errors.append(str(exc))

    checks = {
        Path("README.md"): [
            "Phase 0–830 are complete",
            CURRENT_READONLY_RELEASE,
            CURRENT_WRITE_ALPHA_RELEASE,
            WRITE_DEFAULT,
            CURRENT_RELEASE_BASELINE_PHASE,
        ],
        Path("README.ru.md"): [
            "Фазы 0–830 завершены",
            CURRENT_READONLY_RELEASE,
            CURRENT_WRITE_ALPHA_RELEASE,
            WRITE_DEFAULT,
            CURRENT_RELEASE_BASELINE_PHASE,
        ],
        Path("PROJECT_STATUS.md"): [
            "Completed through Phase 830",
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
            "Completed through Phase 830",
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
                if path in CURRENT_BASELINE_STATUS_FILES:
                    reject_patterns(path, texts[path], RECENT_STALE_CURRENT_PATTERNS)
                reject_patterns(path, texts[path], UNSAFE_AFFIRMATIVE_PATTERNS)
            except AssertionError as exc:
                errors.append(str(exc))

    for path in COMPATIBILITY_STATUS_FILES:
        if path in texts:
            try:
                check_compatibility_status_claims(path, texts[path])
            except AssertionError as exc:
                errors.append(str(exc))

    if Path("CHANGELOG.md") in texts:
        try:
            assert_unreleased_section_is_honest(texts[Path("CHANGELOG.md")])
        except AssertionError as exc:
            errors.append(str(exc))

    try:
        errors.extend(check_default_write_safety())
    except Exception as exc:  # noqa: BLE001 - status guard reports path-redacted safety helper failures
        errors.append(str(exc))

    if errors:
        for error in errors:
            print(f"public-status-guard: {error}", file=sys.stderr)
        return 1

    print("public-status-guard: ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
