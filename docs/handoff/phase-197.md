# Phase 197 — Disposable GnuCash Desktop fixture compatibility evidence

Date: 2026-05-20
Status: COMPLETE — blocker narrowed, collector hardening tested, docs/status updated, committed/pushed
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-112544/cycle-3-roadmap.md` (Phase 6 only)

## Goal

Advance GitHub #22 by obtaining safe Desktop-generated synthetic SQLite fixture evidence if the tooling path is confirmed, or by recording an honest executable blocker without making broad compatibility claims.

## Scope completed

- Read required context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-196.md`;
  - roadmap file named by the phase contract;
  - compatibility docs, Desktop/tooling probe scripts, metadata collector, and related tests.
- Ran the disposable container tooling probe:
  - `debian:12-slim` temporary container;
  - GnuCash/GnuCash CLI 4.13 available inside the container;
  - no safe noninteractive create/save-as SQLite fixture command exposed by `gnucash-cli --help`.
- Did not create a Desktop-generated fixture because the safe noninteractive path is still absent and no isolated GUI/manual-safe creation path was established in this phase.
- Added `docs/gnucash-desktop-tooling-phase-197.md` with the bounded evidence, exact next tooling requirement, safety boundary, and no-broad-claim guidance.
- Hardened `apps/api/scripts/collect_gnucash_compatibility_metadata.py`:
  - `collector_version=phase-197`;
  - explicit `--fixture-origin` choices;
  - `desktop_generated_synthetic_fixture` boolean;
  - redaction contract naming excluded row fields and allowed book facts.
- Expanded metadata collector tests to prove output excludes private paths, account names/descriptions, transaction descriptions, split memos, split amounts, and other row values.
- Updated compatibility docs narrowly:
  - `docs/gnucash-compatibility.md` adds Phase 197 as blocker evidence, not Desktop support;
  - `docs/gnucash-version-fixture-plan.md` adds the exact disposable GUI/manual-safe next requirement and phase-197 collector invocation;
  - `PROJECT_STATUS.md` records Phase 197 completion and the no-broad-claim boundary.

## Files changed

- `PROJECT_STATUS.md`
- `apps/api/scripts/collect_gnucash_compatibility_metadata.py`
- `apps/api/tests/test_gnucash_compatibility_metadata.py`
- `docs/gnucash-compatibility.md`
- `docs/gnucash-desktop-tooling-phase-197.md`
- `docs/gnucash-version-fixture-plan.md`
- `docs/handoff/phase-197.md`

No product runtime behavior, write route, write default, Docker runtime default, frontend UI, release, or tag was changed.

## Container/tooling evidence

Command:

```bash
python apps/api/scripts/probe_gnucash_desktop_disposable_container.py \
  --output /tmp/phase-197-container-probe.json \
  --timeout-seconds 900
```

Result summary:

```text
returncode=0
probe_version=phase-163
commands_available.gnucash=true
commands_available.gnucash-cli=true
gnucash-cli version=GnuCash 4.13
noninteractive_sqlite_fixture_creation_supported_by_cli_help=false
blocker=gnucash-cli help exposes report/quote commands only; no safe noninteractive create/save-as SQLite fixture command found
```

The JSON output stayed in `/tmp` and was not committed.

## Metadata collector smoke

Command:

```bash
python apps/api/scripts/collect_gnucash_compatibility_metadata.py \
  apps/api/tests/fixtures/test-book.gnucash.sqlite \
  --fixture-origin piecash-generated-synthetic \
  --output /tmp/phase-197-metadata-smoke.json
```

Result summary:

```text
book_path=<redacted>
collector_version=phase-197
fixture_origin=piecash-generated-synthetic
desktop_generated=False
versions=Gnucash 3000000, Gnucash-Resave 19920
table_counts_keys=accounts, books, commodities, splits, transactions
```

This was collector validation against an existing committed synthetic fixture only. It is not Desktop-generated evidence.

## Verification summary

Commands/results:

```bash
cd apps/api && pytest tests/test_gnucash_compatibility_metadata.py tests/test_gnucash_desktop_container_probe.py -q
# 7 passed

python apps/api/scripts/probe_gnucash_desktop_disposable_container.py --output /tmp/phase-197-container-probe.json --timeout-seconds 900
# returncode 0; GnuCash CLI 4.13 available; noninteractive SQLite fixture creation not supported by help output

python apps/api/scripts/collect_gnucash_compatibility_metadata.py apps/api/tests/fixtures/test-book.gnucash.sqlite --fixture-origin piecash-generated-synthetic --output /tmp/phase-197-metadata-smoke.json
# collector_version=phase-197; path redacted; schema/table-count metadata only

cd apps/api && pytest tests/test_gnucash_compatibility_metadata.py tests/test_gnucash_desktop_container_probe.py tests/test_compatibility_fixture_v1.py tests/test_health.py tests/test_transaction_writes.py -q
# passed

JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
# rendered default remains false for API and web

git diff --check
# passed

# sensitive tracked-file hygiene scan from phase execution playbook
# passed
```

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- No host packages were installed.
- No private directories/books were mounted, searched, opened, copied, or committed.
- No Desktop-generated SQLite fixture was produced or claimed.
- No binary fixture, app DB, backup, `.env`, token, key, cert, screenshot, export, raw account name, transaction description, memo, amount, private path, or private financial data was committed.
- No PostgreSQL/MySQL/MariaDB/XML support claim was added.
- No all-version or broad GnuCash Desktop compatibility claim was added.
- No release, tag, package, Docker image, production-readiness claim, or security-audit claim was added.

## Risks / follow-up

- GitHub #22 remains open: the remaining blocker is fixture creation itself, not metadata collection.
- The exact next requirement is an isolated disposable GUI/manual-safe GnuCash Desktop session that creates/saves a synthetic SQLite fixture outside git, then runs:
  - phase-197 metadata collector with `--fixture-origin desktop-generated-synthetic`;
  - read-only API smoke with `GNUCASH_WRITES_ENABLED=false`.
- Until that synthetic Desktop-created fixture exists and is read-only-smoked, the compatibility matrix must continue to say that no real GnuCash Desktop version is validated by the automated suite.

## Next

Do not start another roadmap phase from this session. Next work should be explicitly requested and scoped separately.
