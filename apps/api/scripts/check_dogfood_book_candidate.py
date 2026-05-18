#!/usr/bin/env python3
"""Safely preflight a copied personal GnuCash SQL book for dogfood.

Usage:
    python apps/api/scripts/check_dogfood_book_candidate.py /outside/repo/copy.gnucash.sqlite

The output intentionally includes only the candidate filename, never the full
path, so it can be pasted into phase evidence or GitHub issues without leaking
private filesystem details.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
API_ROOT = Path(__file__).resolve().parents[1]
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from app.dogfood_preflight import check_copied_book_candidate  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Preflight a copied personal GnuCash SQL book without leaking private paths."
    )
    parser.add_argument("candidate", help="Path to a copied personal GnuCash SQL book outside git")
    args = parser.parse_args()

    result = check_copied_book_candidate(args.candidate, repo_root=REPO_ROOT)
    print(result.safe_summary())
    return 0 if result.status == "ready" else 2


if __name__ == "__main__":
    raise SystemExit(main())
