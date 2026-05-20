# Phase 204 — Compatibility matrix regression from fixture metadata

Date: 2026-05-20
Status: COMPLETE — compatibility matrix now has automated metadata classification and wording guards
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-220851/cycle-1/roadmap-cycle-1.md` (Cycle 1, Phase 3 only)

## Goal

Turn the Phase 203 fixture/provenance result into automated read-only compatibility regression coverage and honest matrix docs.

## Scope completed

- Read required context: `AGENTS.md`, `PROJECT_STATUS.md`, latest handoff `docs/handoff/phase-203.md`, and the cycle-1 roadmap file.
- Added `apps/api/app/compatibility_matrix.py` to classify redacted collector metadata into explicit matrix categories:
  - tested synthetic/disposable fixture evidence;
  - blocked/manual Desktop fixture work;
  - unclaimed backend/format.
- Added `apps/api/tests/test_compatibility_matrix.py` covering:
  - Desktop-generated synthetic metadata remains blocked/manual until explicit read-only validation is recorded;
  - explicit validation is required before a Desktop-generated synthetic row can be treated as tested synthetic evidence;
  - non-SQLite metadata stays an unclaimed backend even if metadata is present;
  - compatibility docs keep separate tested/blocked/unclaimed sections;
  - docs/changelog avoid broad-support phrases that would imply all-version/all-backend/production/real-book guarantees.
- Reorganized `docs/gnucash-compatibility.md` so the matrix clearly separates tested synthetic fixtures, blocked/manual fixture work, and unclaimed backends/formats.
- Updated `docs/gnucash-version-fixture-plan.md` with the Phase 204 matrix-regression guard.
- Updated `CHANGELOG.md` Unreleased note and `PROJECT_STATUS.md`.

## Files changed

- `apps/api/app/compatibility_matrix.py`
- `apps/api/tests/test_compatibility_matrix.py`
- `docs/gnucash-compatibility.md`
- `docs/gnucash-version-fixture-plan.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-204.md`

## Verification summary

Commands/results:

```text
cd apps/api && pytest tests/test_compatibility_matrix.py tests/test_gnucash_compatibility.py tests/test_gnucash_compatibility_metadata.py tests/test_compatibility_fixture_v1.py -q
# passed: 23 passed; existing piecash/SQLAlchemy warnings only

cd apps/api && pytest -q
# passed: 478 passed; existing piecash/SQLAlchemy/FastAPI warnings only

cd apps/web && npm run check && npm run test:auth-routes && npm run build
# passed

JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config --quiet
# passed

JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
# rendered false for API and web

touched markdown link check
# passed

git diff --check
# passed

sensitive tracked-file hygiene scan
# passed
```

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains default.
- No fixture binary was created or committed.
- No Desktop-generated fixture was produced, supplied, copied into runtime storage, or claimed as tested.
- PostgreSQL/MySQL/MariaDB and XML remain explicitly unclaimed.
- No real/private book, app DB, backup, `.env`, screenshot/export, token, key, cert, raw path, account name, transaction description, memo, amount, row value, or private financial data was committed.

## Risks / follow-up

- Desktop-generated fixture evidence remains blocked until an isolated disposable GUI/manual-safe Desktop session creates a synthetic SQLite fixture outside git and read-only validation passes with `GNUCASH_WRITES_ENABLED=false`.
- The new helper is classification/display-copy support, not a public API route and not external DB implementation.
- Future contributors must still review metadata JSON before using it in docs/issues.

## Next

Do not start another roadmap phase from this session. Next work should be explicitly requested and scoped separately.
