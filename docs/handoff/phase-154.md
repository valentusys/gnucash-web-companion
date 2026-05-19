# Phase 154 — GnuCash compatibility fixture path v5 blocker refresh

Date: 2026-05-19
Status: DONE — blocker recorded honestly, no Desktop-generated fixture claimed
Starting HEAD: `111688a`
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260519-214704/cycle-1-roadmap.md` (cycle 1/3, phase 3/10 only)

## Goal

Move GitHub #22 forward with safe, automated compatibility evidence that does not rely on private books or unsupported claims.

## Scope completed

- Read required project context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-153.md`;
  - roadmap phase 3 and common safety constraints from `cycle-1-roadmap.md`.
- Kept this as Phase 154 only; no neighboring roadmap phases were started.
- Re-ran the local GnuCash Desktop/CLI availability checks:
  - `gnucash` is not installed on `PATH`;
  - `gnucash-cli` is not installed on `PATH`;
  - non-mutating `apt-cache policy` shows an Ubuntu `gnucash` package candidate, but installed state is `(none)`.
- Improved `apps/api/scripts/probe_gnucash_desktop_tooling.py` so the safe probe now records:
  - `probe_version=phase-154`;
  - missing-command reasons when `gnucash` / `gnucash-cli` are absent;
  - `desktop_generated_fixture_possible_now=false`;
  - optional `--include-install-hints` package metadata via bounded, non-mutating `apt-cache policy` checks.
- Added regression coverage for the phase-154 probe metadata, missing-command reasons, optional install hints, and private-path omission.
- Added blocker evidence doc `docs/gnucash-desktop-tooling-phase-154.md`.
- Updated compatibility matrix and fixture plan to state that package availability alone is not Desktop-generated compatibility evidence and future Desktop rows require a disposable Desktop/CLI environment plus synthetic SQLite fixture and read-only validation.
- Synchronized `PROJECT_STATUS.md` and `CHANGELOG.md`.

## Verification

Targeted compatibility checks:

```bash
cd apps/api && pytest tests/test_gnucash_compatibility_metadata.py tests/test_compatibility_fixture_v1.py -q
```

Result: passed — `13 passed`.

Probe evidence command:

```bash
python apps/api/scripts/probe_gnucash_desktop_tooling.py \
  --include-install-hints \
  --output /tmp/phase-154-gnucash-tooling-probe.json
```

Safe summarized result:

- `desktop_tooling_available=false`.
- `desktop_generated_fixture_possible_now=false`.
- `gnucash`: not found on `PATH`.
- `gnucash-cli`: not found on `PATH`.
- `apt-cache policy gnucash`: candidate `1:5.14-1build1`, installed `(none)`.

Standard checks after doc/status sync:

- `cd apps/api && pytest -q` — passed.
- `cd apps/web && npm run check` — passed.
- `cd apps/web && npm run test:auth-routes` — passed.
- `cd apps/web && npm run build` — passed.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — passed.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'` — confirmed API and web remain `"false"`.
- `git diff --check` — passed.
- Sensitive tracked-file hygiene scan — passed.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- Controlled writes remain post-MVP/experimental and were not expanded or enabled.
- No GnuCash Desktop package was installed in this shared environment.
- No Desktop-generated SQLite fixture was created, committed, or claimed.
- No private book, real GnuCash file, `.env`, app DB, backup, screenshot/export, token, key, cert, private path, account name, description, memo, amount, or private financial data was committed.
- No PostgreSQL/MySQL/MariaDB/XML support, broad all-version compatibility, Desktop write support, production readiness, or security-audit claim was added.
- No package, Docker image, binary, tag, or GitHub release was published.

## Files changed

- `apps/api/scripts/probe_gnucash_desktop_tooling.py`
- `apps/api/tests/test_gnucash_compatibility_metadata.py`
- `docs/gnucash-compatibility.md`
- `docs/gnucash-version-fixture-plan.md`
- `docs/gnucash-desktop-tooling-phase-154.md`
- `docs/handoff/phase-154.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
