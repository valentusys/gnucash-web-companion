#!/usr/bin/env python3
"""Safely probe local GnuCash Desktop/CLI tooling availability.

This helper records only command availability and version output. It never scans
user directories, never opens a book, and never serializes paths beyond the
fixed executable command names being probed.
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from datetime import datetime, timezone
from typing import Any

COMMANDS = ("gnucash", "gnucash-cli")
MAX_VERSION_OUTPUT_CHARS = 500


def _safe_version_output(command: str) -> tuple[bool, str]:
    """Return whether `command --version` worked and its bounded output."""

    try:
        completed = subprocess.run(
            [command, "--version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, f"unavailable: {exc.__class__.__name__}"

    output = "\n".join(part for part in (completed.stdout.strip(), completed.stderr.strip()) if part)
    output = output[:MAX_VERSION_OUTPUT_CHARS]
    if completed.returncode == 0:
        return True, output or "available; --version returned no output"
    return False, output or f"--version exited {completed.returncode}"


def probe_tooling() -> dict[str, Any]:
    """Collect non-sensitive GnuCash Desktop/CLI availability metadata."""

    commands: dict[str, dict[str, Any]] = {}
    for command in COMMANDS:
        executable = shutil.which(command)
        record: dict[str, Any] = {
            "available": executable is not None,
            "executable_path_recorded": "<redacted>" if executable else "not found",
        }
        if executable:
            version_ok, version_output = _safe_version_output(command)
            record["version_command"] = f"{command} --version"
            record["version_command_succeeded"] = version_ok
            record["version_output"] = version_output
        commands[command] = record

    any_available = any(record["available"] for record in commands.values())
    return {
        "probe": "gnucash-desktop-tooling",
        "probe_version": "phase-111",
        "collected_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "privacy": (
            "No GnuCash book was opened. No user directories were searched. "
            "Executable paths are redacted; only command availability and bounded version output are recorded."
        ),
        "commands": commands,
        "desktop_tooling_available": any_available,
        "safe_next_step": (
            "Generate a synthetic/disposable SQLite fixture with the detected GnuCash Desktop tooling, "
            "then run collect_gnucash_compatibility_metadata.py on that disposable file."
            if any_available
            else "Install or provide GnuCash Desktop/CLI in a disposable environment before claiming Desktop-generated fixture evidence."
        ),
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Safely probe local GnuCash Desktop/CLI tooling availability without opening any books."
    )
    parser.add_argument("--output", help="Write JSON probe result to this path instead of stdout")
    return parser


def main(argv: list[str] | None = None) -> None:
    args = _parser().parse_args(argv)
    payload = json.dumps(probe_tooling(), indent=2, sort_keys=True) + "\n"
    if args.output:
        from pathlib import Path

        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(payload, encoding="utf-8")
        print(f"GnuCash tooling probe written: {output}")
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
