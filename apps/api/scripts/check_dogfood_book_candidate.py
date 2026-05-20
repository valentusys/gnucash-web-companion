#!/usr/bin/env python3
"""Safely preflight copied/disposable GnuCash SQL books for dogfood.

Usage:
    python apps/api/scripts/check_dogfood_book_candidate.py /outside/repo/copy.gnucash.sqlite
    python apps/api/scripts/check_dogfood_book_candidate.py --write-alpha-plan \
        --confirm-disposable-copy /outside/repo/copy.gnucash.sqlite

The output intentionally includes only the candidate filename and path classes,
never the full path, so it can be pasted into phase evidence or GitHub issues
without leaking private filesystem details.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
API_ROOT = Path(__file__).resolve().parents[1]
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from app.dogfood_preflight import (  # noqa: E402
    check_copied_book_candidate,
    check_write_alpha_dogfood_plan,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Preflight a copied/disposable GnuCash SQL book without leaking private paths."
    )
    parser.add_argument("candidate", help="Path to a copied/disposable GnuCash SQL book outside git")
    parser.add_argument(
        "--write-alpha-plan",
        action="store_true",
        help="Validate the local-only write-alpha copied-book command path without copying or writing.",
    )
    parser.add_argument(
        "--confirm-disposable-copy",
        action="store_true",
        help="Acknowledge the candidate is not a real/private/only-copy authoritative book.",
    )
    parser.add_argument(
        "--runtime-book",
        default="data/books/write-alpha-dogfood.gnucash.sqlite",
        help="Repo-relative ignored runtime copy target for write-alpha dogfood design.",
    )
    parser.add_argument(
        "--backup-dir",
        default="data/backups/write-alpha-dogfood",
        help="Repo-relative ignored backup directory for write-alpha dogfood design.",
    )
    args = parser.parse_args()

    if args.write_alpha_plan:
        result = check_write_alpha_dogfood_plan(
            args.candidate,
            repo_root=REPO_ROOT,
            disposable_copy_acknowledged=args.confirm_disposable_copy,
            runtime_book_path=args.runtime_book,
            backup_dir_path=args.backup_dir,
        )
    else:
        result = check_copied_book_candidate(args.candidate, repo_root=REPO_ROOT)

    print(result.safe_summary())
    return 0 if result.status == "ready" else 2


if __name__ == "__main__":
    raise SystemExit(main())
