#!/usr/bin/env python3
"""Inspect or clean ignored runtime data after the app is stopped.

Output is intentionally redacted to path classes, counts, and statuses. It never
prints raw book/app/backup/lock paths, account names, memos, or amounts.
"""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
API_ROOT = REPO_ROOT / "apps" / "api"
sys.path.insert(0, str(API_ROOT))

from app.runtime_cleanup import (  # noqa: E402
    RUNTIME_CLASSES,
    STOPPED_RUNTIME_ACK,
    RuntimeCleanupError,
    cleanup_runtime,
    format_summary,
)


def _via_compose(argv: list[str]) -> int:
    forwarded = [arg for arg in argv if arg != "--via-compose"]
    command = [
        "docker",
        "compose",
        "run",
        "--rm",
        "--no-deps",
        "-v",
        f"{REPO_ROOT}:/workspace",
        "-w",
        "/workspace",
        "api",
        "python",
        "scripts/ops/runtime-cleanup.py",
        *forwarded,
    ]
    env = os.environ.copy()
    env.setdefault("JWT_SECRET", "dummy-validation-secret")
    env.setdefault("APP_ADMIN_PASSWORD", "dummy")
    return subprocess.call(command, cwd=REPO_ROOT, env=env)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Redacted stopped-runtime cleanup for ignored data artifacts")
    parser.add_argument("--ack", required=True, help=f"required exact token after docker compose down: {STOPPED_RUNTIME_ACK}")
    parser.add_argument("--execute", action="store_true", help="remove eligible stale/runtime artifacts; default is dry-run")
    parser.add_argument("--via-compose", action="store_true", help="re-run inside the API container with the repository mounted")
    parser.add_argument(
        "--class",
        dest="classes",
        action="append",
        choices=RUNTIME_CLASSES,
        help="limit to a runtime path class; may be repeated; default: all allowed classes",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(list(argv if argv is not None else sys.argv[1:]))
    if args.via_compose:
        return _via_compose(list(argv if argv is not None else sys.argv[1:]))
    classes = tuple(args.classes) if args.classes else RUNTIME_CLASSES
    try:
        summary = cleanup_runtime(
            REPO_ROOT,
            REPO_ROOT / "data",
            ack=args.ack,
            execute=args.execute,
            classes=classes,
        )
    except RuntimeCleanupError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(format_summary(summary))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
