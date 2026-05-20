# Phase 197 — Disposable GnuCash Desktop fixture compatibility evidence

Status: BLOCKED for Desktop-generated synthetic SQLite fixture evidence; blocker narrowed to a disposable GUI/manual-safe creation step.

This phase advances GitHub #22 without installing host packages, opening private books, committing a binary fixture, or broadening compatibility claims.

## Goal

Produce safe Desktop-generated synthetic SQLite fixture evidence if the tooling path is confirmed, or record an executable blocker with the exact next command/tooling requirement.

## What was run

A disposable Debian 12 container tooling probe was run:

```bash
python apps/api/scripts/probe_gnucash_desktop_disposable_container.py \
  --output /tmp/phase-197-container-probe.json \
  --timeout-seconds 900
```

Bounded result from the redacted JSON:

```text
returncode=0
probe_version=phase-163
container_image=debian:12-slim
commands_available.gnucash=true
commands_available.gnucash-cli=true
gnucash-cli version=GnuCash 4.13
noninteractive_sqlite_fixture_creation_supported_by_cli_help=false
```

The probe installs `gnucash` and `gnucash-common` only inside a temporary Docker container and records bounded command/version/help/package metadata. It does not mount host books, scan user directories, open a book, generate a fixture, install host packages, commit outputs, or record private paths.

## Result

No Desktop-generated synthetic SQLite fixture was produced in this phase.

Reason: the disposable container can install GnuCash 4.13 tooling, but `gnucash-cli --help` exposes report/quote commands only; it does not expose a safe noninteractive create/save-as SQLite fixture path. A GUI/manual-safe creation path is therefore still required before the project can claim a Desktop-generated fixture row.

## Exact next command/tooling requirement

The next executable step is to run GnuCash Desktop in a disposable GUI environment, create a synthetic SQLite book there, then run the redacted metadata collector and read-only API smoke against the disposable output.

Minimum tooling required:

- disposable VM or container with isolated display, not the host desktop session;
- GnuCash Desktop package installed only inside that disposable environment;
- no mounted private home directories or private books;
- synthetic accounts/transactions only;
- output copied to an ignored/disposable path such as `/tmp/gnucash-desktop-synthetic.gnucash.sqlite` or ignored `data/books/` runtime storage;
- `GNUCASH_WRITES_ENABLED=false` for web/API validation.

Exact command skeleton for the currently proven package/tooling base:

```bash
docker run --rm -it \
  --name gwc-gnucash-desktop-fixture \
  --network none \
  -v /tmp/gwc-gnucash-desktop-fixture:/workspace \
  debian:12-slim \
  sh -lc 'apt-get update && apt-get install -y --no-install-recommends gnucash gnucash-common xauth xvfb && echo "Start an isolated display/GUI, create a synthetic SQLite book, save it under /workspace, then exit."'
```

Because this session did not establish a safe noninteractive GUI automation flow, the GUI creation itself remains a manual-safe/disposable step. After the synthetic SQLite output exists, the metadata and read-only validation commands are:

```bash
python apps/api/scripts/collect_gnucash_compatibility_metadata.py \
  /tmp/gwc-gnucash-desktop-fixture/desktop-synthetic.gnucash.sqlite \
  --gnucash-version "GnuCash 4.13" \
  --fixture-origin desktop-generated-synthetic \
  --output /tmp/phase-197-desktop-synthetic-metadata.json

# Copy only the synthetic output to ignored runtime storage, then validate with writes disabled.
GNUCASH_WRITES_ENABLED=false SMOKE_ADMIN_PASSWORD=<dummy-local-password> \
  scripts/smoke/read-only-api-smoke.py
```

## Metadata collector hardening

`apps/api/scripts/collect_gnucash_compatibility_metadata.py` now records an explicit `fixture_origin` and `desktop_generated_synthetic_fixture` boolean. Its runtime context is marked `collector_version=phase-197`, and the JSON includes a redaction contract naming excluded row fields.

Tests cover that the collector output excludes:

- private input paths;
- account names and descriptions;
- transaction descriptions;
- split memos;
- split amounts;
- private commodity names.

Only schema versions, selected table counts, declared provenance/version strings, and runtime tool versions are allowed.

## Compatibility boundary

This phase is blocker evidence, not Desktop-generated compatibility evidence.

Do not claim:

- GnuCash Desktop 4.13 GUI compatibility;
- all-version GnuCash Desktop support;
- PostgreSQL/MySQL/MariaDB support;
- XML support;
- production-readiness or real/private-book safety.

The current positive fact is only: disposable Debian 12 can install GnuCash/GnuCash CLI 4.13, and the metadata collector is ready to safely describe a future Desktop-generated synthetic SQLite fixture after one is created in a disposable GUI/manual-safe environment.

## Safety

- No host packages were installed.
- No private directories/books were mounted or opened.
- No binary fixture, screenshot, export, app DB, backup, `.env`, token, key, cert, raw account name, memo, amount, or private path was committed.
- `GNUCASH_WRITES_ENABLED=false` remains the validation default.
- No release or tag was published.
