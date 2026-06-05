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
    re.compile(r"Completed through Phase 275\b"),
    re.compile(r"Completed through Phase 276\b"),
    re.compile(r"Completed through Phase 277\b"),
    re.compile(r"Completed through Phase 278\b"),
    re.compile(r"Completed through Phase 279\b"),
    re.compile(r"Completed through Phase 280\b"),
    re.compile(r"Completed through Phase 281\b"),
    re.compile(r"Completed through Phase 282\b"),
    re.compile(r"Completed through Phase 283\b"),
    re.compile(r"Completed through Phase 284\b"),
    re.compile(r"Completed through Phase 285\b"),
    re.compile(r"Completed through Phase 286\b"),
    re.compile(r"Completed through Phase 287\b"),
    re.compile(r"Completed through Phase 288\b"),
    re.compile(r"Completed through Phase 289\b"),
    re.compile(r"Completed through Phase 290\b"),
    re.compile(r"Completed through Phase 291\b"),
    re.compile(r"Completed through Phase 292\b"),
    re.compile(r"Completed through Phase 293\b"),
    re.compile(r"Completed through Phase 294\b"),
    re.compile(r"Completed through Phase 295\b"),
    re.compile(r"Completed through Phase 296\b"),
    re.compile(r"Completed through Phase 297\b"),
    re.compile(r"Completed through Phase 298\b"),
    re.compile(r"Completed through Phase 299\b"),
    re.compile(r"Completed through Phase 300\b"),
    re.compile(r"Completed through Phase 301\b"),
    re.compile(r"Completed through Phase 302\b"),
    re.compile(r"Completed through Phase 303\b"),
    re.compile(r"Completed through Phase 304\b"),
    re.compile(r"Completed through Phase 305\b"),
    re.compile(r"Completed through Phase 306\b"),
    re.compile(r"Completed through Phase 307\b"),
    re.compile(r"Completed through Phase 308\b"),
    re.compile(r"Completed through Phase 309\b"),
    re.compile(r"Completed through Phase 310\b"),
    re.compile(r"Completed through Phase 311\b"),
    re.compile(r"Completed through Phase 312\b"),
    re.compile(r"Completed through Phase 313\b"),
    re.compile(r"Completed through Phase 314\b"),
    re.compile(r"Completed through Phase 315\b"),
    re.compile(r"Completed through Phase 316\b"),
    re.compile(r"Completed through Phase 317\b"),
    re.compile(r"Completed through Phase 318\b"),
    re.compile(r"Completed through Phase 319\b"),
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
    re.compile(r"Phase 0[–-]275 are complete"),
    re.compile(r"Phase 0[–-]276 are complete"),
    re.compile(r"Phase 0[–-]277 are complete"),
    re.compile(r"Phase 0[–-]278 are complete"),
    re.compile(r"Phase 0[–-]279 are complete"),
    re.compile(r"Phase 0[–-]280 are complete"),
    re.compile(r"Phase 0[–-]281 are complete"),
    re.compile(r"Phase 0[–-]282 are complete"),
    re.compile(r"Phase 0[–-]283 are complete"),
    re.compile(r"Phase 0[–-]284 are complete"),
    re.compile(r"Phase 0[–-]285 are complete"),
    re.compile(r"Phase 0[–-]286 are complete"),
    re.compile(r"Phase 0[–-]287 are complete"),
    re.compile(r"Phase 0[–-]288 are complete"),
    re.compile(r"Phase 0[–-]289 are complete"),
    re.compile(r"Phase 0[–-]290 are complete"),
    re.compile(r"Phase 0[–-]291 are complete"),
    re.compile(r"Phase 0[–-]292 are complete"),
    re.compile(r"Phase 0[–-]293 are complete"),
    re.compile(r"Phase 0[–-]294 are complete"),
    re.compile(r"Phase 0[–-]295 are complete"),
    re.compile(r"Phase 0[–-]296 are complete"),
    re.compile(r"Phase 0[–-]297 are complete"),
    re.compile(r"Phase 0[–-]298 are complete"),
    re.compile(r"Phase 0[–-]299 are complete"),
    re.compile(r"Phase 0[–-]300 are complete"),
    re.compile(r"Phase 0[–-]301 are complete"),
    re.compile(r"Phase 0[–-]302 are complete"),
    re.compile(r"Phase 0[–-]303 are complete"),
    re.compile(r"Phase 0[–-]304 are complete"),
    re.compile(r"Phase 0[–-]305 are complete"),
    re.compile(r"Phase 0[–-]306 are complete"),
    re.compile(r"Phase 0[–-]307 are complete"),
    re.compile(r"Phase 0[–-]308 are complete"),
    re.compile(r"Phase 0[–-]309 are complete"),
    re.compile(r"Phase 0[–-]310 are complete"),
    re.compile(r"Phase 0[–-]311 are complete"),
    re.compile(r"Phase 0[–-]312 are complete"),
    re.compile(r"Phase 0[–-]313 are complete"),
    re.compile(r"Phase 0[–-]314 are complete"),
    re.compile(r"Phase 0[–-]315 are complete"),
    re.compile(r"Phase 0[–-]316 are complete"),
    re.compile(r"Phase 0[–-]317 are complete"),
    re.compile(r"Phase 0[–-]318 are complete"),
    re.compile(r"Phase 0[–-]319 are complete"),
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
    re.compile(r"Фазы 0[–-]275 завершены"),
    re.compile(r"Фазы 0[–-]276 завершены"),
    re.compile(r"Фазы 0[–-]277 завершены"),
    re.compile(r"Фазы 0[–-]278 завершены"),
    re.compile(r"Фазы 0[–-]279 завершены"),
    re.compile(r"Фазы 0[–-]280 завершены"),
    re.compile(r"Фазы 0[–-]281 завершены"),
    re.compile(r"Фазы 0[–-]282 завершены"),
    re.compile(r"Фазы 0[–-]283 завершены"),
    re.compile(r"Фазы 0[–-]284 завершены"),
    re.compile(r"Фазы 0[–-]285 завершены"),
    re.compile(r"Фазы 0[–-]286 завершены"),
    re.compile(r"Фазы 0[–-]287 завершены"),
    re.compile(r"Фазы 0[–-]288 завершены"),
    re.compile(r"Фазы 0[–-]289 завершены"),
    re.compile(r"Фазы 0[–-]290 завершены"),
    re.compile(r"Фазы 0[–-]291 завершены"),
    re.compile(r"Фазы 0[–-]292 завершены"),
    re.compile(r"Фазы 0[–-]293 завершены"),
    re.compile(r"Фазы 0[–-]294 завершены"),
    re.compile(r"Фазы 0[–-]295 завершены"),
    re.compile(r"Фазы 0[–-]296 завершены"),
    re.compile(r"Фазы 0[–-]297 завершены"),
    re.compile(r"Фазы 0[–-]298 завершены"),
    re.compile(r"Фазы 0[–-]299 завершены"),
    re.compile(r"Фазы 0[–-]300 завершены"),
    re.compile(r"Фазы 0[–-]301 завершены"),
    re.compile(r"Фазы 0[–-]302 завершены"),
    re.compile(r"Фазы 0[–-]303 завершены"),
    re.compile(r"Фазы 0[–-]304 завершены"),
    re.compile(r"Фазы 0[–-]305 завершены"),
    re.compile(r"Фазы 0[–-]306 завершены"),
    re.compile(r"Фазы 0[–-]307 завершены"),
    re.compile(r"Фазы 0[–-]308 завершены"),
    re.compile(r"Фазы 0[–-]309 завершены"),
    re.compile(r"Фазы 0[–-]310 завершены"),
    re.compile(r"Фазы 0[–-]311 завершены"),
    re.compile(r"Фазы 0[–-]312 завершены"),
    re.compile(r"Фазы 0[–-]313 завершены"),
    re.compile(r"Фазы 0[–-]314 завершены"),
    re.compile(r"Фазы 0[–-]315 завершены"),
    re.compile(r"Фазы 0[–-]316 завершены"),
    re.compile(r"Фазы 0[–-]317 завершены"),
    re.compile(r"Фазы 0[–-]318 завершены"),
    re.compile(r"Фазы 0[–-]319 завершены"),
    re.compile(r"Current public write-alpha pre-release:\s*`v0\.2\.0-writealpha`"),
    re.compile(r"Current published write-alpha pre-release:\s*`v0\.2\.0-writealpha`"),
    re.compile(r"current public experimental write-alpha GitHub pre-release after Phase 132", re.I),
    re.compile(r"current public experimental write-alpha GitHub pre-release after Phase 211", re.I),
]
RECENT_STALE_CURRENT_PATTERNS = _generated_stale_current_patterns()

UNSAFE_AFFIRMATIVE_PATTERNS = [
    re.compile(r"\bpublic\s+write[-\s]+beta\s+(?:is\s+)?(?:ready|available|open|enabled|supported)\b", re.I),
    re.compile(r"\bpublic\s+write[-\s]+beta\s+(?:is\s+)?(?:approved|authorized|published|released)\b", re.I),
    re.compile(r"\bpublic\s+write[-\s]+beta\s+(?:launch|release|rollout)\s+(?:is\s+)?(?:ready|approved|authorized)\b", re.I),
    re.compile(r"\bwrite[-\s]+beta\s+(?:is\s+)?(?:ready|available|open|enabled|supported)\b", re.I),
    re.compile(r"\bwrite[-\s]+beta\s+(?:is\s+)?(?:approved|authorized|published|released)\b", re.I),
    re.compile(r"\bwrite[-\s]+beta\s+(?:is\s+)?(?:stable|production[- ]ready|security[- ]audited)\b", re.I),
    re.compile(r"\bwrite[-\s]+beta\s+(?:release|build|deployment)\s+(?:is\s+)?(?:stable|production[- ]ready|security[- ]audited)\b", re.I),
    re.compile(r"\b(owner[- ]?)?writebeta\s+(?:is\s+)?(?:public|stable|production[- ]ready|security[- ]audited)\b", re.I),
    re.compile(r"\b(owner[- ]?)?writebeta\s+(?:is\s+)?(?:approved|authorized|published|released)\b", re.I),
    re.compile(r"\bis production[- ]ready\b", re.I),
    re.compile(r"\bproduction[- ]ready\s+(release|software|deployment|build)\b", re.I),
    re.compile(r"\bsecurity[- ]audited\s+(release|software|deployment|build)\b", re.I),
    re.compile(r"\bstable\s+(release|production|write mode|deployment)\b", re.I),
    re.compile(r"\bsafe\s+for\s+real/private\b", re.I),
    re.compile(r"\bsafe\s+production\s+write\s+mode\b", re.I),
    re.compile(r"\bbroad\s+GnuCash\s+(?:Desktop\s+)?compatibility\s+(?:is\s+)?(?:ready|available|supported|claimed|proven|validated|confirmed)\b", re.I),
    re.compile(r"\ball\s+GnuCash\s+(?:versions|backends)\s+(?:are\s+)?(?:supported|compatible|write[- ]compatible)\b", re.I),
    re.compile(r"\b(?:real/private|private|real|only-copy)\s+(?:book\s+)?write[- ]safety\s+(?:is\s+)?(?:proven|verified|ready|safe)\b", re.I),
    re.compile(r"\bonly-copy\s+(?:books?\s+)?(?:are\s+)?safe\s+(?:for\s+)?(?:writes?|mutation|write mode)\b", re.I),
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
    "avoiding",
    "avoid ",
    "deny ",
    "denies ",
    "denied ",
)


def reject_patterns(path: Path, text: str, patterns: list[re.Pattern[str]]) -> None:
    previous_line = ""
    for line_number, line in enumerate(text.splitlines(), start=1):
        if patterns is UNSAFE_AFFIRMATIVE_PATTERNS:
            lowered = line.lower()
            current_line_is_negative = any(marker in lowered for marker in NEGATION_MARKERS)
            wrapped_negative_context = (
                line[:1].isspace()
                or previous_line.rstrip().endswith((",", " or", " and", " no"))
            ) and any(marker in previous_line for marker in NEGATION_MARKERS)
            if current_line_is_negative or wrapped_negative_context:
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
