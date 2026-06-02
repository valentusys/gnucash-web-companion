#!/usr/bin/env python3
"""Safely probe local GnuCash Desktop/CLI tooling availability.

This helper records only command availability and version output. It never scans
user directories, never opens a book, and never serializes paths beyond the
fixed executable command names being probed. Optional install hints only query
non-mutating package-manager metadata for known GnuCash package names.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from typing import Any

COMMANDS = ("gnucash", "gnucash-cli")
APT_PACKAGES = ("gnucash", "gnucash-common")
MAX_VERSION_OUTPUT_CHARS = 500
MAX_PACKAGE_POLICY_CHARS = 1200
PATH_RE = re.compile(r"([A-Za-z]:\\[^\s]*|/[^\s]+|\\\\[^\s]+)")
AMOUNT_RE = re.compile(r"(?i)(amount\s*)\d+[.,]\d{2}")
GNUCASH_VERSION_RE = re.compile(r"(?i)\bGnuCash\s+\d+(?:\.\d+)+\b")
PRIVATE_LABEL_RES = (
    ("ACCOUNT", re.compile(r"(?i)\baccount\s+.+?(?=\s+memo\b|\s+description\b|\s+amount\b|$)")),
    ("MEMO", re.compile(r"(?i)\bmemo\s+.+?(?=\s+account\b|\s+description\b|\s+amount\b|$)")),
    ("DESCRIPTION", re.compile(r"(?i)\bdescription\s+.+?(?=\s+account\b|\s+memo\b|\s+amount\b|$)")),
)


def _redact_probe_text(value: str) -> str:
    value = PATH_RE.sub("[REDACTED_PATH]", value)
    for label, pattern in PRIVATE_LABEL_RES:
        value = pattern.sub(f"[REDACTED_{label}]", value)
    value = AMOUNT_RE.sub("[REDACTED_AMOUNT]", value)
    return value


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
    if len(output) > MAX_VERSION_OUTPUT_CHARS:
        return False, "overlong version output rejected"
    redacted_output = _redact_probe_text(output)
    if completed.returncode == 0:
        if redacted_output != output:
            return False, "unsafe/private-looking version output rejected"
        if not GNUCASH_VERSION_RE.search(output):
            return False, "ambiguous version output rejected"
        return True, output or "available; --version returned no output"
    output = redacted_output[:MAX_VERSION_OUTPUT_CHARS]
    return False, output or f"--version exited {completed.returncode}"


def _apt_policy_for(package_name: str) -> dict[str, Any]:
    """Return bounded, non-mutating apt-cache candidate metadata for a package."""

    record: dict[str, Any] = {
        "query": f"apt-cache policy {package_name}",
        "candidate": "unknown",
        "raw_policy_excerpt": "",
    }
    try:
        completed = subprocess.run(
            ["apt-cache", "policy", package_name],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        record["status"] = f"unavailable: {exc.__class__.__name__}"
        return record

    output = "\n".join(part for part in (completed.stdout.strip(), completed.stderr.strip()) if part)
    output = output[:MAX_PACKAGE_POLICY_CHARS]
    record["status"] = "ok" if completed.returncode == 0 else f"exited {completed.returncode}"
    record["raw_policy_excerpt"] = output
    for line in output.splitlines():
        stripped = line.strip()
        if stripped.startswith("Candidate:"):
            record["candidate"] = stripped.split(":", 1)[1].strip()
            break
    return record


def _install_hints() -> dict[str, Any]:
    """Return safe package availability hints without installing anything."""

    if shutil.which("apt-cache") is None:
        return {
            "checked": False,
            "package_manager": "apt-cache",
            "reason": "apt-cache not found on PATH",
            "packages": {},
        }
    return {
        "checked": True,
        "package_manager": "apt-cache",
        "privacy": "Package metadata only; no install performed, no files or books opened.",
        "packages": {package_name: _apt_policy_for(package_name) for package_name in APT_PACKAGES},
    }


def probe_tooling(*, include_install_hints: bool = False) -> dict[str, Any]:
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
        else:
            record["missing_reason"] = f"{command} not found on PATH"
        commands[command] = record

    any_available = any(record["available"] for record in commands.values())
    payload: dict[str, Any] = {
        "probe": "gnucash-desktop-tooling",
        "probe_version": "phase-154",
        "collected_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "privacy": (
            "No GnuCash book was opened. No user directories were searched. "
            "Executable paths are redacted; only command availability and bounded version output are recorded."
        ),
        "commands": commands,
        "desktop_tooling_available": any_available,
        "desktop_generated_fixture_possible_now": False,
        "safe_next_step": (
            "Generate a synthetic/disposable SQLite fixture with the detected GnuCash Desktop tooling, "
            "then run collect_gnucash_compatibility_metadata.py and read-only integration checks on that disposable file."
            if any_available
            else "Install or provide GnuCash Desktop/CLI in a disposable environment before claiming Desktop-generated fixture evidence."
        ),
    }
    if include_install_hints:
        payload["install_hints"] = _install_hints()
    return payload


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Safely probe local GnuCash Desktop/CLI tooling availability without opening any books."
    )
    parser.add_argument("--output", help="Write JSON probe result to this path instead of stdout")
    parser.add_argument(
        "--include-install-hints",
        action="store_true",
        help="Also run non-mutating apt-cache policy checks for known GnuCash packages.",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    args = _parser().parse_args(argv)
    payload = json.dumps(
        probe_tooling(include_install_hints=args.include_install_hints), indent=2, sort_keys=True
    ) + "\n"
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
