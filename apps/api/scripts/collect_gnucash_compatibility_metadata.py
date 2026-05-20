#!/usr/bin/env python3
"""Collect safe compatibility metadata from a copied GnuCash SQLite book.

This Phase 92 helper is intentionally read-only and metadata-only. It is meant
for disposable/test copies, not original personal books. It records schema/version
facts useful for compatibility evidence while redacting the input path and never
printing account names, transaction descriptions, amounts, memos, or splits.

Usage:
    python apps/api/scripts/collect_gnucash_compatibility_metadata.py \
        /tmp/copied-book.gnucash.sqlite \
        --gnucash-version "GnuCash 5.10" \
        --fixture-origin desktop-generated-synthetic \
        --output /tmp/compatibility-metadata.json
"""

from __future__ import annotations

import argparse
from importlib import metadata as importlib_metadata
import json
import platform
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SAFE_COUNT_TABLES = ("accounts", "transactions", "splits", "commodities", "books")
DISPOSABLE_NAME_MARKERS = ("synthetic", "disposable", "fixture", "test")
FORBIDDEN_NAME_MARKERS = ("private", "personal", "real", "production", "prod", "backup", "secret")
SAFE_SQLITE_SUFFIXES = (".gnucash.sqlite", ".sqlite", ".sqlite3", ".db")


class SafeCandidateError(ValueError):
    """Path-redacted candidate rejection for Desktop fixture capture."""

    def __init__(self, reasons: list[str]) -> None:
        self.reasons = reasons
        super().__init__("; ".join(reasons))


def _package_version(package_name: str) -> str:
    try:
        return importlib_metadata.version(package_name)
    except importlib_metadata.PackageNotFoundError:
        return "not installed"


def _runtime_context() -> dict[str, str]:
    """Return safe local toolchain metadata for compatibility provenance."""

    return {
        "collector_version": "phase-203",
        "os": platform.platform(),
        "python_version": sys.version.split()[0],
        "sqlite_version": sqlite3.sqlite_version,
        "piecash_version": _package_version("piecash"),
    }


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


def _is_relative_to(path: Path, base: Path) -> bool:
    try:
        path.relative_to(base)
        return True
    except ValueError:
        return False


def validate_desktop_fixture_candidate(
    book_path: str | Path,
    *,
    fixture_origin: str | None,
    gnucash_version: str | None = None,
) -> dict[str, Any]:
    """Return deterministic, path-redacted acceptance metadata for a fixture candidate."""

    path = Path(book_path).expanduser()
    resolved = path.resolve(strict=False)
    repo_root = _repo_root()
    lowered_name = path.name.lower()
    lowered_parts = [part.lower() for part in resolved.parts]
    reasons: list[str] = []

    if fixture_origin != "desktop-generated-synthetic":
        return {
            "accepted": True,
            "checked": False,
            "reason": "strict Desktop fixture candidate checks apply only to desktop-generated-synthetic inputs",
        }

    if not gnucash_version or not gnucash_version.strip():
        reasons.append("desktop-generated synthetic candidates require an explicit GnuCash Desktop version string")
    if not path.exists():
        reasons.append("candidate file does not exist")
    elif not path.is_file():
        reasons.append("candidate path is not a regular file")
    if not any(lowered_name.endswith(suffix) for suffix in SAFE_SQLITE_SUFFIXES):
        reasons.append("candidate filename must use a SQLite/GnuCash SQLite suffix")
    if not any(marker in lowered_name for marker in DISPOSABLE_NAME_MARKERS):
        reasons.append("candidate filename must indicate synthetic/disposable/test fixture provenance")
    forbidden_hits = sorted({marker for marker in FORBIDDEN_NAME_MARKERS if marker in lowered_name})
    if forbidden_hits:
        reasons.append("candidate filename contains forbidden non-disposable marker(s): " + ", ".join(forbidden_hits))
    forbidden_repo_dirs = (
        repo_root / "data" / "backups",
        repo_root / "data" / "app",
        repo_root / "secrets",
    )
    if any(_is_relative_to(resolved, forbidden_dir) for forbidden_dir in forbidden_repo_dirs):
        reasons.append("candidate path is inside a forbidden repo runtime/secrets class")
    if any(part in {"backups", "backup", "secrets", ".env"} for part in lowered_parts):
        reasons.append("candidate path contains a forbidden backups/secrets/env component")
    if path.name.startswith(".env"):
        reasons.append("candidate filename is an environment/secret-like file")

    if reasons:
        raise SafeCandidateError(reasons)

    return {
        "accepted": True,
        "checked": True,
        "fixture_origin": fixture_origin,
        "path_policy": "input path and parent directories are redacted; only safe path-class metadata is recorded",
        "path_class": "external_or_ignored_disposable_sqlite_candidate",
        "filename_policy": "synthetic/disposable/test fixture marker required",
        "forbidden_path_classes": ["repo data/backups", "repo data/app", "secrets", ".env"],
    }


def _read_versions(conn: sqlite3.Connection) -> dict[str, int]:
    rows = conn.execute(
        "select table_name, table_version from versions order by table_name"
    ).fetchall()
    return {str(name): int(version) for name, version in rows}


def _table_exists(conn: sqlite3.Connection, table_name: str) -> bool:
    row = conn.execute(
        "select 1 from sqlite_master where type = 'table' and name = ? limit 1",
        (table_name,),
    ).fetchone()
    return row is not None


def _safe_table_counts(conn: sqlite3.Connection) -> dict[str, int]:
    counts: dict[str, int] = {}
    for table_name in SAFE_COUNT_TABLES:
        if _table_exists(conn, table_name):
            counts[table_name] = int(conn.execute(f"select count(*) from {table_name}").fetchone()[0])
    return counts


def collect_metadata(
    book_path: str | Path,
    *,
    gnucash_version: str | None = None,
    fixture_origin: str | None = None,
) -> dict[str, Any]:
    """Return non-sensitive compatibility metadata for a copied SQLite book."""

    path = Path(book_path)
    candidate_acceptance = validate_desktop_fixture_candidate(
        path,
        fixture_origin=fixture_origin,
        gnucash_version=gnucash_version,
    )
    with sqlite3.connect(f"file:{path}?mode=ro", uri=True) as conn:
        versions = _read_versions(conn)
        table_counts = _safe_table_counts(conn)

    return {
        "format": "GnuCash SQLite",
        "book_path": "<redacted>",
        "source_policy": "copied/disposable SQL book only; original untouched",
        "fixture_origin": fixture_origin or "not recorded",
        "desktop_generated_synthetic_fixture": fixture_origin == "desktop-generated-synthetic",
        "candidate_acceptance": candidate_acceptance,
        "contains_real_data": "unknown-to-script; do not commit book or row data",
        "gnucash_desktop_version": gnucash_version or "not recorded",
        "backend": "SQLite",
        "collected_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "runtime_context": _runtime_context(),
        "versions": versions,
        "table_counts": table_counts,
        "safe_to_publish": (
            "Review before publishing. This JSON intentionally excludes paths, account names, "
            "transaction descriptions, amounts, memos, and split rows."
        ),
        "redaction_contract": {
            "path_policy": "input path is always recorded as <redacted>",
            "excluded_row_fields": [
                "account names",
                "account descriptions",
                "transaction descriptions",
                "split memos",
                "split amounts",
                "private paths",
            ],
            "allowed_book_facts": ["schema versions", "selected table counts", "runtime tool versions"],
        },
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Collect safe GnuCash SQLite compatibility metadata from a copied/disposable book."
    )
    parser.add_argument("book", help="Path to a copied/disposable GnuCash SQLite book")
    parser.add_argument(
        "--gnucash-version",
        help="Exact GnuCash Desktop version used to create/save the copied fixture, e.g. 'GnuCash 5.10'",
    )
    parser.add_argument(
        "--fixture-origin",
        choices=("desktop-generated-synthetic", "piecash-generated-synthetic", "copied-disposable"),
        help=(
            "Safe provenance label for the copied/disposable input. Use "
            "desktop-generated-synthetic only after a disposable GnuCash Desktop/GUI session "
            "created or saved the synthetic SQLite fixture."
        ),
    )
    parser.add_argument(
        "--output",
        help="Write JSON metadata to this path instead of printing it to stdout",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    args = _parser().parse_args(argv)
    try:
        metadata = collect_metadata(
            args.book,
            gnucash_version=args.gnucash_version,
            fixture_origin=args.fixture_origin,
        )
    except SafeCandidateError as exc:
        print(
            "Compatibility metadata rejected: "
            + json.dumps({"accepted": False, "reasons": exc.reasons}, sort_keys=True),
            file=sys.stderr,
        )
        raise SystemExit(2) from exc
    payload = json.dumps(metadata, indent=2, sort_keys=True) + "\n"
    if args.output:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
        print(f"Compatibility metadata written: {output}")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
