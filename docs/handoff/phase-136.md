# Phase 136 — GnuCash compatibility matrix documentation refresh

Date: 2026-05-19
Status: DONE

## Goal

Update the GnuCash compatibility matrix and fixture plan so the current compatibility state is explicit, conservative, and synthetic-only.

## Scope completed

- Updated `docs/gnucash-compatibility.md`:
  - made the matrix evidence boundary explicit: current compatibility evidence is synthetic/disposable only;
  - expanded the matrix with fixture provenance and GnuCash Desktop version evidence columns;
  - added a dedicated `GnuCash Desktop versions tested` section;
  - stated that no real GnuCash Desktop release has been validated by the automated suite yet;
  - clarified that operator-supplied `--gnucash-version` metadata strings are documentation inputs, not independent proof of Desktop-release support.
- Updated `docs/gnucash-version-fixture-plan.md`:
  - refreshed status for Phase 136;
  - added a current fixture/evidence inventory covering committed synthetic fixtures, generated compatibility fixture v1, redacted metadata collection, and Desktop-tooling probes;
  - explicitly recorded that the current Desktop-tested version list is empty;
  - kept future Desktop-generated fixture work gated on disposable provenance plus tests.
- Updated `README.md`:
  - advanced current status to Phase 0–136;
  - added a current-status link to the compatibility matrix with the synthetic-only/no-real-Desktop-support warning.
- Updated `PROJECT_STATUS.md` for Phase 136 completion.

## Non-goals / safety boundaries

- No new fixtures were generated.
- No real GnuCash Desktop versions were tested.
- No backend, frontend, schema, route, service, GnuCash adapter, fixture generator, or endpoint code changed.
- No write endpoint, write service, write lock, audit, backup, or write-mode gate changed.
- No write-alpha capability was expanded or enabled.
- `GNUCASH_WRITES_ENABLED=false` remains the default.
- No release/tag/package/publication was performed.
- No real/private GnuCash books, app DBs, backups, `.env`, tokens, keys, screenshots, exports, or private financial data were added or committed.
- Docs remain honest: pre-alpha/test copies/no production guarantee; no false compatibility claims were added.

## Verification

- `cd apps/api && pytest tests/test_gnucash_compatibility.py -q` — passed (`3 passed`).
- `cd apps/api && pytest tests/test_gnucash_compatibility_metadata.py -q` — passed (`4 passed`).
- `cd apps/api && pytest -q` — passed (`377 passed, 32 warnings`).
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — passed.
- `git diff --check` — passed.
- Sensitive tracked-file scan — passed; no committed `.env`, app DB, real GnuCash book, backup, screenshot/export, key, token, or secret artifact detected in the phase diff.

## Expected artifacts

- `docs/gnucash-compatibility.md`
- `docs/gnucash-version-fixture-plan.md`
- `README.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-136.md`

## GitHub / release state

- No release/publication gate was executed for this phase.
- No tag or GitHub release was created.
- Push `main` after all verification passes and the single Phase 136 commit is created.
