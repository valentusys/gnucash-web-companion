#!/usr/bin/env python3
"""Operator CLI for safe app metadata SQLite recovery bundles."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
API_ROOT = REPO_ROOT / "apps" / "api"
UPGRADE_SMOKE_SCRIPT = REPO_ROOT / "scripts" / "smoke" / "synthetic-upgrade-smoke.sh"
if str(API_ROOT) not in sys.path:
    sys.path.insert(0, str(API_ROOT))

from app.services.app_metadata_recovery import (  # noqa: E402
    AppMetadataRecoveryError,
    backup_app_metadata,
    public_json,
    redacted_error_payload,
    restore_rehearsal,
    verify_bundle,
)


def _add_json_flag(parser: argparse.ArgumentParser, *, suppress_default: bool = False) -> None:
    default = argparse.SUPPRESS if suppress_default else False
    parser.add_argument(
        "--json",
        action="store_true",
        dest="json_output",
        default=default,
        help="emit deterministic redacted JSON",
    )


def _port_arg(value: str) -> int:
    try:
        port = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("port must be numeric") from exc
    if not (1 <= port <= 65535):
        raise argparse.ArgumentTypeError("port must be between 1 and 65535")
    return port


def run_upgrade_rehearsal(
    *,
    repo: Path,
    previous_ref: str,
    current_ref: str,
    workdir: Path,
    port: int,
    keep_workdir: bool,
) -> int:
    """Delegate to the synthetic upgrade smoke script after argparse validation."""

    command = [
        "bash",
        str(UPGRADE_SMOKE_SCRIPT),
        "--repo",
        str(repo),
        "--previous-ref",
        previous_ref,
        "--current-ref",
        current_ref,
        "--workdir",
        str(workdir),
        "--port",
        str(port),
    ]
    if keep_workdir:
        command.append("--keep-workdir")
    return subprocess.run(command, cwd=REPO_ROOT, check=False).returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Back up, verify, and restore-rehearse app metadata SQLite only."
    )
    _add_json_flag(parser)
    subparsers = parser.add_subparsers(dest="command", required=True)

    backup = subparsers.add_parser("backup", help="create an offline app metadata backup bundle")
    _add_json_flag(backup, suppress_default=True)
    backup.add_argument("--source", required=True, help="source app metadata SQLite DB")
    backup.add_argument("--bundle", required=True, help="new output backup bundle directory")
    backup.add_argument(
        "--runtime-stopped",
        action="store_true",
        help="acknowledge the app runtime is stopped/offline for this DB",
    )

    verify = subparsers.add_parser("verify", help="verify an app metadata backup bundle")
    _add_json_flag(verify, suppress_default=True)
    verify.add_argument("--bundle", required=True, help="backup bundle directory")

    restore = subparsers.add_parser(
        "restore-rehearsal",
        help="restore a verified bundle into a new explicit DB path outside the repo",
    )
    _add_json_flag(restore, suppress_default=True)
    restore.add_argument("--bundle", required=True, help="backup bundle directory")
    restore.add_argument(
        "--destination-db",
        required=True,
        help="new destination DB path; must not exist and must be outside the repo",
    )

    upgrade = subparsers.add_parser(
        "upgrade-rehearsal",
        help="run the synthetic fresh-clone upgrade rehearsal smoke",
    )
    upgrade.add_argument(
        "--repo",
        required=True,
        help="repository path or URL to clone for the rehearsal",
    )
    upgrade.add_argument(
        "--previous-ref",
        default="v0.5.0-public-readonly-beta",
        help="supported read-only predecessor ref (default: v0.5.0-public-readonly-beta)",
    )
    upgrade.add_argument(
        "--current-ref",
        default="HEAD",
        help="candidate ref to test after baseline startup (default: HEAD)",
    )
    upgrade.add_argument(
        "--workdir",
        required=True,
        help="existing parent directory for the temporary clone",
    )
    upgrade.add_argument(
        "--port",
        required=True,
        type=_port_arg,
        help="host port for the temporary Caddy proxy",
    )
    upgrade.add_argument(
        "--keep-workdir",
        action="store_true",
        help="keep the temporary clone after the run",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        if args.command == "backup":
            result = backup_app_metadata(
                source_db=Path(args.source),
                bundle_dir=Path(args.bundle),
                runtime_stopped=bool(args.runtime_stopped),
                repo_root=REPO_ROOT,
            )
        elif args.command == "verify":
            result = verify_bundle(bundle_dir=Path(args.bundle), repo_root=REPO_ROOT)
        elif args.command == "restore-rehearsal":
            result = restore_rehearsal(
                bundle_dir=Path(args.bundle),
                destination_db=Path(args.destination_db),
                repo_root=REPO_ROOT,
            )
        elif args.command == "upgrade-rehearsal":
            return run_upgrade_rehearsal(
                repo=Path(args.repo),
                previous_ref=args.previous_ref,
                current_ref=args.current_ref,
                workdir=Path(args.workdir),
                port=int(args.port),
                keep_workdir=bool(args.keep_workdir),
            )
        else:  # pragma: no cover - argparse enforces command choices
            parser.error("unknown command")
        if args.json_output:
            print(public_json(result.to_public_dict()))
        else:
            print(f"{result.operation}: ok")
        return 0
    except AppMetadataRecoveryError as exc:
        if args.json_output:
            print(public_json(redacted_error_payload(exc)), file=sys.stderr)
        else:
            print(f"error: {exc.code}", file=sys.stderr)
        return exc.exit_code
    except Exception:  # pragma: no cover - last-resort redaction boundary
        if args.json_output:
            print(public_json({"status": "error", "safe_code": "internal_error", "exit_code": 1}), file=sys.stderr)
        else:
            print("error: internal_error", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
