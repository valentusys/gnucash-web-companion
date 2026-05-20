# Phase 203 — Disposable Desktop fixture capture path

Date: 2026-05-20
Status: COMPLETE — deterministic safe capture gate for manually supplied Desktop-generated synthetic SQLite fixture candidates
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-220851/cycle-1/roadmap-cycle-1.md` (Cycle 1, Phase 2 only)

## Goal

Advance GnuCash Desktop compatibility evidence by creating a safe path to capture or document a Desktop-generated synthetic SQLite fixture without touching real/private books.

## Scope completed

- Read required context: `AGENTS.md`, `PROJECT_STATUS.md`, latest handoff `docs/handoff/phase-202.md`, and the cycle-1 roadmap file.
- Hardened `apps/api/scripts/collect_gnucash_compatibility_metadata.py` for `--fixture-origin desktop-generated-synthetic` candidates:
  - requires explicit `--gnucash-version`;
  - accepts only regular SQLite/GnuCash SQLite files;
  - requires a synthetic/disposable/test fixture marker in the filename;
  - rejects private/personal/real/production/prod/backup/secret-like filenames;
  - rejects repo `data/backups/`, repo `data/app/`, `secrets/`, `.env`, and backup/secrets path components;
  - records only redacted `candidate_acceptance` metadata on accepted candidates;
  - emits deterministic path-redacted rejection reasons and exits with code 2 for unsafe candidates.
- Updated helper tests for accepted candidate metadata, deterministic path-safe rejection, and forbidden runtime path-class rejection.
- Added `docs/gnucash-desktop-fixture-capture.md` with the manual-safe disposable Desktop fixture path, rejection examples, read-only validation guidance, and suggested GitHub #22 update text.
- Updated `docs/gnucash-compatibility.md` to record Phase 203 as capture-path/blocker evidence, not a Desktop-version compatibility row.
- Updated `docs/gnucash-version-fixture-plan.md` so the desktop-generated collector command uses the safe synthetic/disposable filename now required by the helper.
- Updated `PROJECT_STATUS.md` and this handoff.
- Added concise GitHub #22 evidence comment: `https://github.com/valentusys/gnucash-web-companion/issues/22#issuecomment-4498500834`.

## Files changed

- `apps/api/scripts/collect_gnucash_compatibility_metadata.py`
- `apps/api/tests/test_gnucash_compatibility_metadata.py`
- `docs/gnucash-desktop-fixture-capture.md`
- `docs/gnucash-compatibility.md`
- `docs/gnucash-version-fixture-plan.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-203.md`

## Verification summary

Commands/results:

```text
cd apps/api && pytest tests/test_gnucash_compatibility_metadata.py tests/test_gnucash_desktop_container_probe.py -q
# passed: 9 passed

cd apps/api && pytest tests/test_gnucash_compatibility_metadata.py tests/test_compatibility_fixture_v1.py tests/test_gnucash_compatibility.py -q
# passed: 18 passed; existing piecash/SQLAlchemy warnings only

cd apps/api && pytest -q
# passed: 473 passed; existing piecash/SQLAlchemy/FastAPI warnings only

cd apps/web && npm run check && npm run test:auth-routes && npm run build
# passed

JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config --quiet
# passed

JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
# rendered false for API and web

git diff --check
# passed

sensitive tracked-file hygiene scan
# passed
```

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains default and was verified in rendered Docker Compose config.
- No Desktop-generated fixture was created, supplied, copied into runtime storage, opened through the app, or committed.
- No broad Desktop/version/backend compatibility claim was added.
- No PostgreSQL/MySQL/MariaDB/XML support claim was added.
- The helper rejects unsafe candidate path classes before metadata collection for Desktop-generated synthetic provenance.
- Accepted helper metadata remains bounded to redacted path-class/candidate status, declared provenance/version, schema versions, selected table counts, and safe runtime context.
- No real/private book, app DB, backup, `.env`, screenshot/export, token, key, cert, raw path, account name, transaction description, split memo, amount, row value, or private financial data was committed.

## Suggested GitHub #22 update

```text
Phase 203 advanced the Desktop-generated synthetic SQLite fixture path without claiming Desktop compatibility yet. The metadata helper now deterministically accepts/rejects manually supplied desktop-generated synthetic candidates: it requires a regular SQLite/GnuCash SQLite file, explicit GnuCash Desktop version, synthetic/disposable/test filename marker, rejects private/real/prod/backup/secret-like names and repo backup/app/secrets/.env path classes, and records only redacted candidate metadata plus schema versions/table counts. Rejected candidates return path-safe reasons. No Desktop-generated fixture was produced or committed; the remaining blocker is still a disposable GUI/manual-safe GnuCash Desktop session that creates the synthetic SQLite file, followed by this helper and default-read-only API validation with `GNUCASH_WRITES_ENABLED=false`.
```

## Risks / follow-up

- Desktop-generated fixture evidence remains blocked until a disposable GUI/manual-safe Desktop session creates a synthetic SQLite fixture outside git.
- Operator-supplied `--gnucash-version` is provenance metadata, not independent proof of Desktop compatibility.
- Future accepted metadata must still be reviewed before being pasted into public GitHub issues or docs.

## Next

Do not start another roadmap phase from this session. Next work should be explicitly requested and scoped separately.
