#!/usr/bin/env python3
"""Build a redacted compatibility-matrix row from collected metadata JSON.

This helper reads only previously collected metadata. It never opens a GnuCash
book and never emits raw input paths, account names, descriptions, memos, or
amounts. The output is a conservative display row: Desktop-generated metadata
becomes tested evidence only when the caller supplies an explicit read-only
validation flag.
"""
from __future__ import annotations

import argparse
from dataclasses import asdict
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
API_ROOT = REPO_ROOT / "apps" / "api"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from app.compatibility_matrix import build_matrix_row_from_metadata  # noqa: E402


class CliError(Exception):
    """Path-redacted CLI error with a deterministic exit code."""


def _load_metadata(path: Path) -> dict[str, Any]:
    try:
        raw = path.read_text(encoding="utf-8")
        loaded = json.loads(raw)
    except (OSError, json.JSONDecodeError) as exc:
        raise CliError("metadata file could not be read or parsed") from exc
    if not isinstance(loaded, dict):
        raise CliError("metadata file must contain a JSON object")
    return loaded


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Emit a redacted conservative compatibility-matrix row from metadata JSON."
    )
    parser.add_argument("metadata_json", help="Path to redacted collector metadata JSON")
    parser.add_argument(
        "--read-only-validation-passed",
        action="store_true",
        help=(
            "Mark Desktop-generated synthetic metadata as read-only validated. "
            "Use only after the separate default-read-only validation gate passed."
        ),
    )
    args = parser.parse_args(argv)

    try:
        metadata = _load_metadata(Path(args.metadata_json))
    except CliError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    row = build_matrix_row_from_metadata(
        metadata,
        read_only_validation_passed=args.read_only_validation_passed,
    )
    json.dump(asdict(row), sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
