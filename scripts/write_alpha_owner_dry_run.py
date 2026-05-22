#!/usr/bin/env python3
"""Single dry-run-only entrypoint for owner copied-book write-alpha preparation.

This command intentionally exposes no CREATE/PATCH/DELETE mode. It delegates to
``write_alpha_copied_book_dogfood`` with ``--dry-run`` semantics, validates that
no mutation was requested or performed, and writes redacted evidence only.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(SCRIPT_DIR))

import write_alpha_copied_book_dogfood as dogfood  # noqa: E402


class OwnerDryRunFailure(Exception):
    """Raised when the dry-run-only entrypoint cannot prove no mutation."""


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run the owner copied-book dry-run-only preflight wrapper. "
            "This entrypoint has no CREATE, PATCH, or DELETE mode."
        )
    )
    parser.add_argument("--target", required=True, help="Copied/restorable book path outside this git repo.")
    parser.add_argument(
        "--backup-dir",
        default=dogfood.DEFAULT_BACKUP_DIR,
        help="Pre-step backup destination; outside git or git-ignored.",
    )
    parser.add_argument("--evidence-file", required=True, help="Destination for redacted JSON evidence.")
    parser.add_argument("--confirm-copied-disposable", action="store_true")
    parser.add_argument("--confirm-original-untouched", action="store_true")
    parser.add_argument("--confirm-outside-git", action="store_true")
    return parser.parse_args(argv)


def _dogfood_args(args: argparse.Namespace) -> argparse.Namespace:
    return argparse.Namespace(
        dry_run=True,
        create_one=False,
        target=args.target,
        backup_dir=args.backup_dir,
        evidence_file=args.evidence_file,
        create_command=None,
        confirm_copied_disposable=args.confirm_copied_disposable,
        confirm_original_untouched=args.confirm_original_untouched,
        confirm_outside_git=args.confirm_outside_git,
        confirm_create_one_mutation=False,
        phase_number=263,
        classification="synthetic",
    )


def run(args: argparse.Namespace) -> dogfood.DogfoodEvidence:
    evidence = dogfood.run(_dogfood_args(args))
    if evidence.mode != "dry-run":
        raise OwnerDryRunFailure("unexpected non-dry-run mode")
    if evidence.mutation_requested or evidence.mutation_performed:
        raise OwnerDryRunFailure("dry-run entrypoint produced mutation evidence")
    if evidence.create_command_status != "not-run":
        raise OwnerDryRunFailure("dry-run entrypoint unexpectedly ran a create command")
    return evidence


def main(argv: list[str] | None = None) -> int:
    try:
        evidence = run(parse_args(argv))
    except (dogfood.DogfoodWrapperFailure, OwnerDryRunFailure) as exc:
        print(f"FAIL: owner dry-run blocked; {exc}; paths=redacted", file=sys.stderr)
        return 2
    except OSError as exc:
        print(f"FAIL: filesystem operation failed; detail=redacted; {exc.__class__.__name__}", file=sys.stderr)
        return 1
    print(
        "PASS: owner copied-book dry-run completed; mutation_requested=false; "
        "mutation_performed=false; "
        f"preflight={evidence.preflight_status}; "
        f"backup={evidence.backup_status}; "
        f"default_disabled={evidence.disabled_reset_status}; paths=redacted"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
