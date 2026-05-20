#!/usr/bin/env python3
"""Print redacted write-alpha readiness status without mutating a GnuCash book."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
API_ROOT = REPO_ROOT / "apps" / "api"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from app.config import get_settings  # noqa: E402
from app.database import get_engine  # noqa: E402
from app.write_alpha_readiness import inspect_write_alpha_readiness  # noqa: E402


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Inspect redacted write-alpha readiness without mutation."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit the redacted readiness report as JSON instead of one-line text.",
    )
    args = parser.parse_args(argv)

    readiness = inspect_write_alpha_readiness(get_settings(), get_engine())
    if args.json:
        print(json.dumps(readiness.to_dict(), indent=2, sort_keys=True))
    else:
        print(readiness.safe_summary())
    return 0 if readiness.ready else 2


if __name__ == "__main__":
    raise SystemExit(main())
