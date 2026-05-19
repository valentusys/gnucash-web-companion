# Phase 163 — Disposable GnuCash Desktop compatibility fixture path

Date: 2026-05-20
Status: DONE — BLOCKED for Desktop-generated fixture evidence, with reproducible disposable-container blocker artifact
Starting HEAD: `bdb6aa3`
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-resume-20260520-003549/cycle-2-roadmap.md` (cycle 2/3, phase 2/10 only)

## Goal

Advance GitHub #22 with practical Desktop compatibility evidence: either produce a Desktop-generated synthetic SQLite fixture in a disposable environment, or record a reproducible blocker without false compatibility claims.

## Scope completed

- Read required context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-162.md`;
  - roadmap phase 2 and safety constraints from `cycle-2-roadmap.md`.
- Kept this as Phase 163 only; no neighboring roadmap phases were started.
- Added `apps/api/scripts/probe_gnucash_desktop_disposable_container.py`:
  - runs a temporary `debian:12-slim` Docker container;
  - installs `gnucash`/`gnucash-common` only inside that container;
  - records bounded command/version/help/package metadata;
  - does not mount host books, open/generate books, scan private directories, install host packages, or write fixture binaries into the repo.
- Added regression tests in `apps/api/tests/test_gnucash_desktop_container_probe.py` for:
  - container package/tooling metadata parsing;
  - no Desktop-generated fixture claim when CLI help lacks a safe create/save-as SQLite path;
  - bounded/redacted evidence shape.
- Ran the disposable probe and stored local evidence outside git at:
  - `/home/val/.hermes/logs/gnucash-web-companion/phase-163/disposable-container-probe.json`.
- Recorded blocker/evidence in `docs/gnucash-desktop-tooling-phase-163.md`.
- Updated compatibility docs:
  - `docs/gnucash-compatibility.md`;
  - `docs/gnucash-version-fixture-plan.md`.
- Synchronized `CHANGELOG.md`, `PROJECT_STATUS.md`, and this handoff.

## Disposable-container evidence

Command:

```bash
python apps/api/scripts/probe_gnucash_desktop_disposable_container.py \
  --output /home/val/.hermes/logs/gnucash-web-companion/phase-163/disposable-container-probe.json
```

Result: command completed with return code `0`.

Key evidence:

- Container image: `debian:12-slim`.
- Package candidates inside the container:
  - `gnucash`: `1:4.13-1`.
  - `gnucash-common`: `1:4.13-1`.
- Commands available inside the disposable container:
  - `gnucash`: true.
  - `gnucash-cli`: true.
- `gnucash-cli --version`: `GnuCash 4.13`.
- `gnucash-cli --help`: report generation and price quote commands only; no safe noninteractive create/save-as SQLite fixture command was identified.
- `desktop_generated_fixture_possible_now`: false.

## Blocker result

A Desktop-generated synthetic SQLite fixture was not produced.

Reason: the disposable Debian 12 container can install GnuCash 4.13 tooling, but this phase did not find a safe noninteractive command to create and save a new synthetic SQLite book from scratch. Using GUI automation or manual fixture creation needs a separate explicitly documented disposable environment path.

Required future prerequisites before a Desktop-generated compatibility row can be claimed:

1. disposable GUI/VM/container path with display isolation and only synthetic fixture data; or
2. confirmed noninteractive GnuCash command/script interface for creating a SQLite book from scratch; or
3. operator-created synthetic SQLite fixture outside git from a disposable Desktop environment, followed by redacted metadata collection and read-only service validation.

## Verification

```bash
cd apps/api && pytest tests/test_gnucash_desktop_container_probe.py -q
cd apps/api && pytest tests/test_gnucash_desktop_container_probe.py tests/test_gnucash_compatibility_metadata.py tests/test_compatibility_fixture_v1.py -q
python -m py_compile apps/api/scripts/probe_gnucash_desktop_disposable_container.py
docs grep for overbroad compatibility claims
cd apps/api && pytest -q
cd apps/web && npm run check && npm run test:auth-routes && npm run build
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
git diff --check
# sensitive tracked-file hygiene scan
```

Results:

- Targeted new probe tests passed: `2 passed`.
- Targeted compatibility/probe suite passed: `15 passed, 21 warnings`.
- Probe script compiled successfully.
- Docs grep found no broad all-version/PostgreSQL/MySQL/MariaDB/XML/production/security claims in changed compatibility docs.
- Backend full suite passed: `388 passed, 32 warnings`.
- Frontend `npm run check` passed with `0 errors and 0 warnings`.
- Frontend auth-route checks passed.
- Frontend production build passed.
- Docker Compose config validation passed.
- Rendered Compose config kept `GNUCASH_WRITES_ENABLED: "false"` for API and web.
- `git diff --check` passed.
- Sensitive tracked-file hygiene scan passed.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- No production writes were enabled.
- No host package was installed.
- No GnuCash book was opened or generated.
- No Desktop-generated fixture, SQLite fixture binary, raw CSV, screenshot, backup, `.env`, app DB, token, key, cert, or private data was committed.
- No broad Desktop-version, all-version, PostgreSQL, MySQL, MariaDB, XML, production-readiness, security-audit, or real-book compatibility claim was added.

## Files changed

- `apps/api/scripts/probe_gnucash_desktop_disposable_container.py`
- `apps/api/tests/test_gnucash_desktop_container_probe.py`
- `docs/gnucash-desktop-tooling-phase-163.md`
- `docs/gnucash-compatibility.md`
- `docs/gnucash-version-fixture-plan.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-163.md`
