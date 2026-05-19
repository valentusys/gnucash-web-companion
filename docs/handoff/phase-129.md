# Phase 129 — Write-alpha recovery documentation and maintainer review gate

Date: 2026-05-19
Status: DONE

## Goal

Close the write-alpha documentation gap before any future real-user write consideration by adding a concrete recovery procedure and a maintainer review checklist while keeping write mode disabled by default and without changing product code.

## Scope completed

- Added `docs/write-alpha-recovery-procedure.md` with maintainer/operator steps for experimental write-alpha incidents on synthetic/disposable books only:
  - immediate containment and returning to `GNUCASH_WRITES_ENABLED=false`;
  - locating a pre-write backup for a disposable book id;
  - stale lock inspection and book-specific lock cleanup while the app is stopped;
  - restore commands from backup;
  - read-only integrity checks after restore;
  - damaged-book triage without committing private/runtime artifacts.
- Added `docs/write-alpha-maintainer-checklist.md` with a checkable review gate covering:
  - default-disabled config;
  - `APP_ENV=test` enabled-route gate;
  - disposable fixture/test-data requirement;
  - no sensitive tracked files;
  - frontend write UI hidden-by-default expectation;
  - lifecycle evidence for validation, lock, backup, audit, unlock, and read-only reopen checks;
  - recovery documentation and verification commands.
- Updated README controlled-write warning to clearly state experimental, disabled-by-default, test-environment-gated, synthetic/disposable-first, and not production-safe positioning.
- Updated `docs/v0.2-controlled-writes.md` readiness gate and remaining-gaps language for Phase 129.
- Updated `CHANGELOG.md` and `PROJECT_STATUS.md` through Phase 129.

## Non-goals / safety boundaries

- No product code changes.
- No config changes and no default write enablement; `GNUCASH_WRITES_ENABLED=false` remains the default.
- No weakening of the `APP_ENV=test` write-alpha gate.
- No real/private GnuCash books used, searched for, opened, copied, or committed.
- No synthetic/disposable fixture write tests were added or modified in this docs-only phase.
- No PATCH/DELETE/import/scheduled/account-write expansion.
- No tag, GitHub release, package, upload, or Phase 132 publication action.
- No production-readiness, audited-security, or real-book write-safety claim.
- No app DB, runtime SQLite DB, backups, `.env`, secrets, tokens, credentials, certs, keys, screenshots, CSV/media/private exports, private paths, or real/private financial data committed.

## Verification

- `cd apps/api && pytest -q` — passed (`366 passed, 29 warnings`).
- `cd apps/web && npm run check` — passed (`svelte-check found 0 errors and 0 warnings`).
- `cd apps/web && npm run build` — passed.
- `git diff --cached --check` — passed.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — passed as an extra safety/config check.
- Sensitive tracked-file scan (`git ls-files | grep -E '(^|/)(\.env$|secrets?$|credentials?$)|data/books/.*\.(sqlite|sqlite3|gnucash|db)$|data/backups/.|.*\.(pem|key|crt|p12)$'`) — passed/no matches.
- Manual markdown review — passed: recovery doc contains restore/integrity/lock/damaged-book steps and checklist is checkable.

## Expected artifacts

- `docs/write-alpha-recovery-procedure.md`
- `docs/write-alpha-maintainer-checklist.md`
- `README.md`
- `docs/v0.2-controlled-writes.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-129.md`

## GitHub / release state

- No tag or GitHub release was created.
- Phase 132 publication remains pending separate explicit authorization.
- This phase does not authorize real-book write use; recovery/checklist docs are gates for future synthetic/disposable write-alpha review only.
