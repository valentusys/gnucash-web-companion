# Phase 163 — Disposable GnuCash Desktop tooling probe

Status: BLOCKED for Desktop-generated synthetic SQLite fixture evidence.

This phase advances GitHub #22 by moving the Desktop compatibility check into a disposable container instead of relying only on host `PATH` probes. It does not create, open, or commit any GnuCash book.

## Scope

Roadmap phase: cycle 2/3, phase 2/10 from `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-resume-20260520-003549/cycle-2-roadmap.md`.

Goal: obtain Desktop-generated synthetic SQLite fixture evidence from a disposable environment, or record a reproducible blocker with exact prerequisites.

Result: blocker, not compatibility evidence.

## Disposable probe command

Run from repository root:

```bash
python apps/api/scripts/probe_gnucash_desktop_disposable_container.py \
  --output /tmp/phase-163-gnucash-container-probe.json
```

The helper runs a temporary Docker container from `debian:12-slim`, installs `gnucash` and `gnucash-common` only inside that container, captures bounded command/version/help/package metadata, and exits. It does not mount host books, scan private directories, open a book, generate a book, install host packages, or write a fixture into the repository.

Local evidence file outside git:

```text
/home/val/.hermes/logs/gnucash-web-companion/phase-163/disposable-container-probe.json
```

## Probe result

- Container image: `debian:12-slim`.
- Package candidates inside the container:
  - `gnucash`: `1:4.13-1`.
  - `gnucash-common`: `1:4.13-1`.
- Installed commands inside the disposable container:
  - `gnucash`: available.
  - `gnucash-cli`: available.
- `gnucash-cli --version`: `GnuCash 4.13`.
- `gnucash --version`: required a graphical UI in this container and did not provide a clean non-GUI version-only path.
- `gnucash-cli --help`: exposed report generation and price quote commands, but not a safe noninteractive `create`/`save-as`/SQLite fixture-generation command.
- `desktop_generated_fixture_possible_now`: `false`.

## Blocker

The disposable container proves that Debian 12 can install GnuCash 4.13 tooling, but this phase did not find a safe noninteractive command to create and save a new synthetic SQLite book from scratch.

Creating a Desktop-generated fixture still needs one of these explicit prerequisites:

1. A documented GUI automation path in a disposable VM/container with display isolation, using only synthetic fixture data from `docs/gnucash-version-fixture-plan.md`; or
2. A confirmed noninteractive GnuCash command/script interface that can create a SQLite book from scratch without opening private books; or
3. An operator-provided disposable Desktop environment that manually creates the synthetic SQLite fixture outside git, followed by redacted metadata collection and read-only service validation.

Until one of those prerequisites is satisfied, the compatibility matrix must not claim GnuCash Desktop 4.13 support or broad Desktop-version support.

## Safety

- No host package was installed.
- No GnuCash book was opened or generated.
- No private directory was searched.
- No account names, descriptions, amounts, memos, private paths, `.env`, app DB, backups, screenshots, exports, tokens, keys, or certs were recorded.
- `GNUCASH_WRITES_ENABLED=false` remains the default; no write capability changed.
- No SQLite fixture binary was committed.

## Verification

Targeted checks:

```bash
cd apps/api && pytest tests/test_gnucash_desktop_container_probe.py -q
python apps/api/scripts/probe_gnucash_desktop_disposable_container.py --output /home/val/.hermes/logs/gnucash-web-companion/phase-163/disposable-container-probe.json
```

Release/standard checks are recorded in `docs/handoff/phase-163.md`.
