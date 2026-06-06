#!/usr/bin/env python3
"""Pragmatic raw-Markdown readability guard for public/status docs.

The guard is intentionally scoped. It checks only selected public/status files and
current worker handoff docs so historical Markdown does not create noisy churn.
It never reads ignored runtime data, private books, app DBs, backups, exports, or
secrets.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
MAX_UNSTRUCTURED_LINE = 140

PUBLIC_STATUS_DOCS = (
    Path("README.md"),
    Path("README.ru.md"),
    Path("PROJECT_STATUS.md"),
    Path("CHANGELOG.md"),
)
DEFAULT_DOCS = PUBLIC_STATUS_DOCS + (
    Path("docs/gnucash-compatibility.md"),
    Path("docs/write-alpha/issue-36-remaining-gates.md"),
    Path("docs/write-alpha/controlled-write-readiness-dashboard.md"),
    Path("docs/write-alpha/evidence-matrix.md"),
    Path("docs/release/owner-writebeta-owner-approval-boundary.md"),
    Path("docs/release/v0.4-owner-writebeta-readiness-unreleased.md"),
    Path("docs/release/v0.4-owner-writebeta-no-release-decision.md"),
    Path("docs/release/v0.5.0-public-readonly-beta-notes.md"),
    Path("docs/release/v0.5.0-public-readonly-beta-final-gate.md"),
    Path("docs/release/v0.5.0-public-readonly-beta-publication-evidence.md"),
    Path("docs/development/markdown-readability.md"),
    Path("docs/handoff/overnight-2026-06-02-worker-17.md"),
    Path("docs/handoff/issue36-owner-writebeta-remaining-gates-audit-r5.md"),
    Path("docs/handoff/issue36-owner-writebeta-remaining-gates-audit-r6.md"),
    Path("docs/handoff/issue36-owner-writebeta-remaining-gates-audit-r7.md"),
    Path("docs/handoff/issue36-owner-writebeta-remaining-gates-audit-r8.md"),
    Path("docs/handoff/issue36-owner-writebeta-remaining-gates-audit-r9.md"),
    Path("docs/handoff/issue36-owner-writebeta-remaining-gates-audit-r10.md"),
    Path("docs/handoff/issue36-owner-writebeta-remaining-gates-audit-r11.md"),
)

# Avoid noisy historical whole-file reflow: public/status archives are long by
# design. The guard enforces current top navigation/readability plus the current
# handoff package, while tests cover fail-closed behavior for arbitrary docs.
LONG_LINE_SCAN_LIMITS = {
    Path("CHANGELOG.md"): 105,
    Path("PROJECT_STATUS.md"): 120,
    Path("docs/gnucash-compatibility.md"): 55,
}

STATUS_SAFETY_SIGNALS = (
    "public read-only beta",
    "read-only beta",
    "read-only",
    "writes disabled",
    "write disabled",
    "gnuCash_writes_enabled=false".lower(),
    "GNUCASH_WRITES_ENABLED=false".lower(),
    "not production",
    "no production",
    "не опубликован",
    "безопасным дефолтом",
)
ISSUE_MARKERS = (
    "issues/22",
    "issues/28",
    "issues/36",
    "#22",
    "#28",
    "#36",
)
SAFETY_GUIDANCE_MARKERS = (
    "safety warnings",
    "must not weaken safety claims",
    "preserve exact safety wording",
    "GNUCASH_WRITES_ENABLED=false",
    "real/private/original/only-copy",
    "not production-ready",
)


def _rel(path: Path) -> str:
    return path.as_posix()


def _top_window(text: str, limit: int = 40) -> str:
    return "\n".join(text.splitlines()[:limit]).lower()


def _is_allowlisted_long_line(line: str, in_code_fence: bool) -> bool:
    stripped = line.strip()
    if in_code_fence:
        return True
    if not stripped:
        return True
    if stripped.startswith(("http://", "https://")):
        return True
    if stripped.startswith("|") and stripped.endswith("|"):
        return True
    if stripped.startswith(("```", "~~~")):
        return True
    if stripped.startswith(("- https://", "* https://")):
        return True
    if "https://" in stripped and len(stripped.split()) <= 4:
        return True
    if stripped.startswith(("gh ", "git ", "docker ", "python3 ", "pytest ")):
        return True
    return False


def _long_line_problems(rel: str, text: str) -> list[str]:
    problems: list[str] = []
    in_code_fence = False
    limit = LONG_LINE_SCAN_LIMITS.get(Path(rel))
    for lineno, line in enumerate(text.splitlines(), start=1):
        if limit is not None and lineno > limit:
            break
        stripped = line.lstrip()
        fence = stripped.startswith("```") or stripped.startswith("~~~")
        if len(line) > MAX_UNSTRUCTURED_LINE and not _is_allowlisted_long_line(line, in_code_fence):
            problems.append(
                f"{rel}:{lineno}: long unstructured line ({len(line)} chars > {MAX_UNSTRUCTURED_LINE})"
            )
        if fence:
            in_code_fence = not in_code_fence
    return problems


def check_documents(docs: dict[str, str]) -> list[str]:
    """Return fail-closed readability problems for repo-relative Markdown docs."""
    problems: list[str] = []
    for rel, text in sorted(docs.items()):
        path = Path(rel)
        top = _top_window(text)
        lowered = text.lower()

        if path in PUBLIC_STATUS_DOCS and not any(signal in top for signal in STATUS_SAFETY_SIGNALS):
            problems.append(f"{rel}: missing top status/safety signal")

        if path == Path("PROJECT_STATUS.md"):
            missing = [marker for marker in ("#22", "#28", "#36") if marker not in text and f"issues/{marker[1:]}" not in text]
            if missing:
                problems.append(f"{rel}: missing issue navigation ({', '.join(missing)})")

        if rel.startswith("docs/handoff/overnight-"):
            has_issue = any(marker in text for marker in ISSUE_MARKERS)
            has_handoff_nav = "docs/handoff/" in text or "handoff" in top
            if not (has_issue and has_handoff_nav):
                problems.append(f"{rel}: missing issue or handoff navigation")

        if path == Path("docs/gnucash-compatibility.md"):
            top_required = (
                "Issue #22 is closed for narrow Desktop-generated synthetic SQLite fixture evidence only",
                "Desktop-generated synthetic SQLite fixture",
                "synthetic/disposable fixtures only",
                "PostgreSQL/MySQL/MariaDB GnuCash backends are unclaimed",
            )
            normalized_top = " ".join(top.split()).lower()
            if not all(marker.lower() in normalized_top for marker in top_required):
                problems.append(f"{rel}: missing #22 Desktop fixture closure navigation")

        if path == Path("docs/development/markdown-readability.md"):
            if not all(marker.lower() in lowered for marker in SAFETY_GUIDANCE_MARKERS):
                problems.append(f"{rel}: missing guidance that safety warnings must be preserved")
            status_template_markers = (
                "Current status block template",
                "Handoff readability checklist",
                "GNUCASH_WRITES_ENABLED=false by default",
                "APP_ENV=test gated",
                "no public write beta",
                "no real/private/original/only-copy book",
                "exact next safe package",
            )
            if not all(marker.lower() in lowered for marker in status_template_markers):
                problems.append(f"{rel}: missing current-status/handoff readability template")

        problems.extend(_long_line_problems(rel, text))
    return problems


def _default_docs() -> dict[str, str]:
    docs: dict[str, str] = {}
    for rel_path in DEFAULT_DOCS:
        full_path = REPO_ROOT / rel_path
        if full_path.exists():
            docs[_rel(rel_path)] = full_path.read_text(encoding="utf-8")
    return docs


def main() -> int:
    docs = _default_docs()
    problems = check_documents(docs)
    if problems:
        print("markdown-readability-guard: failed", file=sys.stderr)
        for problem in problems:
            print(f"- {problem}", file=sys.stderr)
        return 1
    print(f"markdown-readability-guard: ok ({len(docs)} docs checked)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
