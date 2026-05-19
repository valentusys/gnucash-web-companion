# Phase 127 — GnuCash Desktop compatibility evidence

Date: 2026-05-19
Status: DONE

## Goal

Refresh GnuCash Desktop compatibility evidence for GitHub #22, or honestly document the exact blocker if Desktop tooling is unavailable.

## Scope completed

- Checked local Desktop tooling availability:
  - `gnucash --version` — unavailable (`gnucash: command not found`).
  - `gnucash-cli --version` — unavailable (`gnucash-cli: command not found`).
  - `python apps/api/scripts/probe_gnucash_desktop_tooling.py --output /tmp/phase-127-gnucash-tooling-probe.json` reported `desktop_tooling_available=false`.
- Did not create a Desktop-generated synthetic book because this environment has no GnuCash Desktop/CLI tooling.
- Updated `docs/gnucash-compatibility.md` with a Phase 127 matrix row that records the blocker instead of claiming Desktop-generated compatibility evidence.
- Updated `docs/gnucash-version-fixture-plan.md` with Phase 127 local evidence and a manual procedure for generating a synthetic Desktop-created SQLite fixture in a disposable environment.
- Added regression coverage in `apps/api/tests/test_compatibility_fixture_v1.py` proving missing Desktop tooling is represented as a safe blocker, not Desktop-generated evidence, and does not serialize private paths.
- Updated `CHANGELOG.md` and `PROJECT_STATUS.md`.
- Updated GitHub #22 with blocker/manual-procedure evidence and kept it open.

## Non-goals / safety boundaries

- No GnuCash Desktop install in CI or this environment.
- No real/private GnuCash books used, searched for, opened, copied, generated from, or committed.
- No new binary fixture committed.
- No write-path changes.
- `GNUCASH_WRITES_ENABLED=false` remains the default.
- `APP_ENV=test` write gate was not changed or weakened.
- No app DB, backups, `.env`, secrets, tokens, credentials, certs, keys, screenshots, CSV/media/private exports, private paths, account names, transaction descriptions, memos, amounts, SQL dumps, tags, GitHub releases, packages, or uploads committed.

## Verification

- `cd apps/api && pytest tests/test_compatibility_fixture_v1.py -q` — passed.
- `cd apps/api && pytest -q` — passed.
- `cd apps/web && npm run check` — passed.
- `cd apps/web && npm run build` — passed.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — passed (extra safety check).
- `git diff --check` — passed.
- Sensitive tracked-file scan (`git ls-files | grep -E '(^|/)(\.env$|secrets?$|credentials?$)|data/books/.*\.(sqlite|sqlite3|gnucash|db)$|data/backups/.|.*\.(pem|key|crt|p12)$'`) — passed/no matches.

## GitHub / issue state

- GitHub #22 was updated with Phase 127 evidence: local Desktop tooling remains unavailable, no Desktop-generated fixture was produced, and the issue remains open pending a disposable environment with GnuCash Desktop/CLI.
- No tag or GitHub release was created.

## Expected artifacts

- `apps/api/tests/test_compatibility_fixture_v1.py`
- `docs/gnucash-compatibility.md`
- `docs/gnucash-version-fixture-plan.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-127.md`
