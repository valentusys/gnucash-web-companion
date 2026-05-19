# Phase 154 — GnuCash Desktop tooling blocker refresh

Date: 2026-05-19
Status: BLOCKED for Desktop-generated fixture evidence

## Scope

This phase advances GitHub #22 only within the safe compatibility-evidence boundary from the cycle 1 roadmap phase 3:

- no private book scanning;
- no real/private GnuCash file use;
- no PostgreSQL/MySQL/MariaDB/XML compatibility claim;
- no Desktop write-support claim;
- `GNUCASH_WRITES_ENABLED=false` remains the default.

## Local probe result

Command run from the repository root:

```bash
python apps/api/scripts/probe_gnucash_desktop_tooling.py \
  --include-install-hints \
  --output /tmp/phase-154-gnucash-tooling-probe.json
```

Safe summarized result:

- `gnucash`: not found on `PATH`.
- `gnucash-cli`: not found on `PATH`.
- `desktop_tooling_available=false`.
- `desktop_generated_fixture_possible_now=false`.
- Non-mutating package metadata only: `apt-cache policy gnucash` reports candidate `1:5.14-1build1` and installed `(none)` in this environment.
- No GnuCash book was opened.
- No user directories were searched.
- No executable paths, private paths, row data, account names, descriptions, memos, amounts, screenshots, exports, app DBs, backups, `.env`, secrets, tokens, keys, or certs were collected.

The generated JSON was kept under `/tmp` and not committed because it is runtime evidence, not a required source artifact.

## Why no Desktop-generated fixture was added

The current environment does not have `gnucash` or `gnucash-cli` installed. Although Ubuntu package metadata shows an install candidate, this phase did not install a GUI/Desktop accounting package into the shared runner or claim that package installation alone creates a reproducible Desktop-generated synthetic SQLite book. The safe next step remains a disposable VM/container or CI job where GnuCash Desktop/CLI is intentionally installed and used only for a synthetic fixture.

## Reproducible next step

In a disposable environment only:

```bash
gnucash --version || gnucash-cli --version
# Create a new synthetic SQLite book from scratch using docs/gnucash-version-fixture-plan.md.
python apps/api/scripts/collect_gnucash_compatibility_metadata.py \
  /tmp/gnucash-desktop-fixture.gnucash.sqlite \
  --gnucash-version "GnuCash X.Y" \
  --output /tmp/gnucash-desktop-fixture-metadata.json
cd apps/api && pytest tests/test_compatibility_fixture_v1.py tests/test_gnucash_compatibility_metadata.py -q
```

Only after that synthetic Desktop-created SQLite book exists and read-only service checks pass may the compatibility matrix add a real Desktop-version evidence row.
