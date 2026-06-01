# Autonomous long cycle 3 — #13 safe storage diagnostics

## PM scope

Complete Issue #13 book-management safety for already-mounted local copied/test SQLite GnuCash books while preserving the public/default read-only product model.

## Non-goals

- No upload workflow.
- No file browser.
- No deletion of GnuCash files.
- No accounting data writes.
- No account, transaction, memo, amount, or private evidence reads.
- No release publication.

## Completed implementation

- Added `invalid_gnucash_schema` storage diagnostic for configured local SQLite files that exist but do not contain core GnuCash SQLite schema marker tables.
- Kept diagnostics bounded to read-only SQLite `sqlite_master` table-name inspection.
- Blocked read-only data routes for `invalid_gnucash_schema` before the GnuCash service layer opens the file.
- Preserved admin-only app-metadata management for already-mounted local copied/test SQLite GnuCash books:
  - register a schema-validated local SQLite GnuCash-looking target;
  - list registered accessible books;
  - set/change the default metadata book;
  - remove a book from the app registry without deleting the underlying file.
- Kept non-admin management blocked and private paths redacted.
- Updated operator guidance so it no longer claims default/registry management is unavailable now that admin metadata actions exist.
- Updated README, CHANGELOG, PROJECT_STATUS, and `docs/book-switcher-readonly-model.md` for the new #13 state.
- Updated backend and frontend static tests for the new diagnostic/status and registry-only wording.

## Verification

Focused RED/GREEN reconstruction:

- RED was verified earlier in the interrupted run: new diagnostics tests failed because existing local non-GnuCash SQLite files were reported as `available` and data routes fell through to the GnuCash service layer.
- Focused GREEN after resume: `cd apps/api && pytest tests/test_multi_book_access.py tests/test_multibook_readonly_access.py tests/test_accounts.py -q` → `138 passed, 4 warnings`.

Required final local checks after resume:

- `cd apps/api && pytest -q` → `617 passed, 38 warnings`.
- `cd apps/web && npm run check` → `svelte-check found 0 errors and 0 warnings`.
- `cd apps/web && npm run test:auth-routes` → `auth route checks passed`.
- `cd apps/web && npm run build` → passed.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` → passed.
- `git diff --check` → passed.
- `gh auth status` → authenticated as `valentusys`.

Warnings were existing/dependency deprecation/SQLAlchemy warnings and did not fail the checks.

## GitHub issues

- #13 (`Book management UI`) was the relevant issue for this cycle.
- Local evidence indicates #13 closure criteria are satisfied for registration, registered list, set default, remove from registry, non-admin blocking, safe unavailable-path/schema errors, docs, and focused/full checks.
- Final GitHub update/closure is expected after the commit/push step if `gh` remains authenticated.

## Commits / push / CI

Local branch state at resume:

- `b991a70 feat: add safe book registry management`
- `f03c71b fix: validate mounted book registration targets`

This resume prepares one additional coherent commit for #13 safe storage diagnostics and final docs. Push and CI status are recorded in the final agent response after the GitHub step.

## Release decision

`NO_RELEASE`.

No stable/production release, GitHub release, tag, package, image, public write claim, or production deployment is authorized or created in this cycle.

## Safety summary

- Public/default app remains read-only.
- `GNUCASH_WRITES_ENABLED=false` remains default.
- GnuCash mutations for this cycle: CREATE 0 / PATCH 0 / DELETE 0.
- No original/private/working/only-copy GnuCash book was mutated.
- No GnuCash file upload, direct file browsing, accounting edit, or file deletion was added.
- Registry actions are app metadata only.
- Diagnostics inspect SQLite table names only and do not read account names, transaction descriptions, memos, amounts, or raw private evidence.
- No private books, app DBs, backups, exports, screenshots, `.env`, secrets, private paths, account names, memos, descriptions, amounts, or raw private evidence were committed.
