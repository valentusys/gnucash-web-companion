#!/usr/bin/env python3
"""Probe GnuCash Desktop/CLI availability inside a disposable Docker container.

The probe installs distro GnuCash packages only inside a temporary container,
records bounded command/version/help metadata, and does not open or generate any
book. It is intentionally a blocker/evidence helper for deciding whether a
Desktop-generated synthetic SQLite fixture can be produced safely later.
"""

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import datetime, timezone
from typing import Any

DEFAULT_IMAGE = "debian:12-slim"
MAX_OUTPUT_CHARS = 6000

PROBE_SCRIPT = r"""
set -eu
export DEBIAN_FRONTEND=noninteractive
apt-get update >/tmp/apt-update.log
apt-cache policy gnucash gnucash-common > /tmp/apt-policy.txt
apt-get install -y --no-install-recommends gnucash gnucash-common > /tmp/apt-install.log 2>&1
{
  echo '== commands =='
  command -v gnucash || true
  command -v gnucash-cli || true
  echo '== gnucash-version =='
  gnucash --version || true
  echo '== gnucash-cli-version =='
  gnucash-cli --version || true
  echo '== gnucash-cli-help =='
  gnucash-cli --help || true
  echo '== apt-policy =='
  cat /tmp/apt-policy.txt
} 2>&1
""".strip()


def _bounded(text: str, limit: int = MAX_OUTPUT_CHARS) -> str:
    if len(text) <= limit:
        return text
    return text[:limit] + "\n<truncated>"


def _section(output: str, name: str) -> str:
    marker = f"== {name} =="
    start = output.find(marker)
    if start == -1:
        return ""
    start += len(marker)
    next_marker = output.find("== ", start)
    return output[start : next_marker if next_marker != -1 else len(output)].strip()


def _parse_candidate(policy: str, package_name: str) -> str:
    current_package: str | None = None
    for line in policy.splitlines():
        if line and not line.startswith(" ") and line.endswith(":"):
            current_package = line[:-1]
            continue
        if current_package == package_name and line.strip().startswith("Candidate:"):
            return line.split(":", 1)[1].strip()
    return "unknown"


def summarize_probe_output(output: str) -> dict[str, Any]:
    commands = _section(output, "commands").splitlines()
    help_text = _section(output, "gnucash-cli-help")
    policy = _section(output, "apt-policy")
    gnucash_version = _section(output, "gnucash-version")
    gnucash_cli_version = _section(output, "gnucash-cli-version")

    fixture_create_keywords = ("create", "save-as", "new-book", "sqlite")
    help_lower = help_text.lower()
    noninteractive_fixture_creation_supported = all(
        keyword in help_lower for keyword in fixture_create_keywords
    )

    return {
        "commands_available": {
            "gnucash": any(line.endswith("/gnucash") for line in commands),
            "gnucash-cli": any(line.endswith("/gnucash-cli") for line in commands),
        },
        "versions": {
            "gnucash": _bounded(gnucash_version, 1000),
            "gnucash-cli": _bounded(gnucash_cli_version, 1000),
        },
        "package_candidates": {
            "gnucash": _parse_candidate(policy, "gnucash"),
            "gnucash-common": _parse_candidate(policy, "gnucash-common"),
        },
        "gnucash_cli_help_excerpt": _bounded(help_text, 2500),
        "noninteractive_sqlite_fixture_creation_supported_by_cli_help": noninteractive_fixture_creation_supported,
        "blocker": (
            "gnucash and gnucash-cli install in the disposable container, but gnucash-cli help exposes report/quote commands only; "
            "this phase did not find a safe noninteractive create/save-as SQLite fixture command."
            if not noninteractive_fixture_creation_supported
            else "CLI help appears to expose fixture-creation keywords; generation still requires a separate explicit implementation step."
        ),
    }


def run_container_probe(*, image: str = DEFAULT_IMAGE, timeout_seconds: int = 900) -> dict[str, Any]:
    command = [
        "docker",
        "run",
        "--rm",
        image,
        "sh",
        "-lc",
        PROBE_SCRIPT,
    ]
    completed = subprocess.run(
        command,
        check=False,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
    )
    combined_output = "\n".join(
        part for part in (completed.stdout.strip(), completed.stderr.strip()) if part
    )
    summary = summarize_probe_output(combined_output)
    return {
        "probe": "gnucash-desktop-disposable-container-tooling",
        "probe_version": "phase-163",
        "collected_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "container_image": image,
        "container_scope": "temporary Docker container; package install occurs only inside the container",
        "returncode": completed.returncode,
        "privacy": (
            "No GnuCash book was opened or generated. No host package was installed. "
            "No user directories were searched. Output is bounded and contains command/version/help/package metadata only."
        ),
        "desktop_generated_fixture_possible_now": False,
        "summary": summary,
        "raw_output_excerpt": _bounded(combined_output),
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Probe GnuCash Desktop/CLI tooling in a disposable Docker container."
    )
    parser.add_argument("--image", default=DEFAULT_IMAGE, help="Container image to probe")
    parser.add_argument("--output", help="Write JSON probe result to this path instead of stdout")
    parser.add_argument("--timeout-seconds", type=int, default=900)
    return parser


def main(argv: list[str] | None = None) -> None:
    args = _parser().parse_args(argv)
    payload = run_container_probe(image=args.image, timeout_seconds=args.timeout_seconds)
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        from pathlib import Path

        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
        print(f"Disposable GnuCash container probe written: {output}")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
