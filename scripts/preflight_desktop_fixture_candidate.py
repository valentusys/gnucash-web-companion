#!/usr/bin/env python3
"""Fail-closed preflight for Desktop-generated synthetic fixture candidate metadata.

This helper reads only a redacted JSON metadata candidate. It never opens a
GnuCash book and never accepts private paths, account names, descriptions,
memos, amounts, copied/private scope evidence, or unsupported backends.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[1]
API_ROOT = REPO_ROOT / "apps" / "api"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from app.compatibility_matrix import (  # noqa: E402
    CandidatePreflightError,
    validate_desktop_fixture_candidate_preflight,
)


class CliError(Exception):
    """Path-redacted CLI failure."""


def _load_candidate(path: Path) -> dict[str, Any]:
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise CliError("candidate metadata file could not be read or parsed") from exc
    if not isinstance(loaded, dict):
        raise CliError("candidate metadata file must contain a JSON object")
    return loaded


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate redacted Desktop-generated synthetic fixture candidate metadata."
    )
    parser.add_argument("candidate_json", help="Path to redacted candidate metadata JSON")
    args = parser.parse_args(argv)

    try:
        result = validate_desktop_fixture_candidate_preflight(_load_candidate(Path(args.candidate_json)))
    except (CliError, CandidatePreflightError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    json.dump(result, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
