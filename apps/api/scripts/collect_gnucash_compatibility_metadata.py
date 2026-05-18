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
        --output /tmp/compatibility-metadata.json
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SAFE_COUNT_TABLES = ("accounts", "transactions", "splits", "commodities", "books")


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


def collect_metadata(book_path: str | Path, *, gnucash_version: str | None = None) -> dict[str, Any]:
    """Return non-sensitive compatibility metadata for a copied SQLite book."""

    path = Path(book_path)
    with sqlite3.connect(f"file:{path}?mode=ro", uri=True) as conn:
        versions = _read_versions(conn)
        table_counts = _safe_table_counts(conn)

    return {
        "format": "GnuCash SQLite",
        "book_path": "<redacted>",
        "source_policy": "copied/disposable SQL book only; original untouched",
        "contains_real_data": "unknown-to-script; do not commit book or row data",
        "gnucash_desktop_version": gnucash_version or "not recorded",
        "backend": "SQLite",
        "collected_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "versions": versions,
        "table_counts": table_counts,
        "safe_to_publish": (
            "Review before publishing. This JSON intentionally excludes paths, account names, "
            "transaction descriptions, amounts, memos, and split rows."
        ),
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
        "--output",
        help="Write JSON metadata to this path instead of printing it to stdout",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    args = _parser().parse_args(argv)
    metadata = collect_metadata(args.book, gnucash_version=args.gnucash_version)
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
