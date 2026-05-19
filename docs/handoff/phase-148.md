# Phase 148 — Books page self-hosting readiness slice

Date: 2026-05-19
Status: DONE

## Goal

Improve read-only book metadata and self-hosting operator confidence without adding book-management writes.

## Scope completed

- Read required project context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-147.md`;
  - analyst roadmap `/home/val/.hermes/logs/gnucash-web-companion/analyst-roadmap-20260519-195139/analyst-roadmap.md`.
- Kept this as Phase 148 only; no PM/auditor was involved and no later roadmap phase was started.
- Extended `/books` and `/books/{book_id}` metadata serialization with app-metadata-only operator guidance:
  - `metadata_source=app_metadata_db`;
  - `data_access=gnucash_not_opened_for_listing`;
  - `read_only_default=true`;
  - storage-type label;
  - unsupported MVP management actions: `book_upload`, `book_delete`, `default_book_change`, and `registry_edit`.
- Kept `management_actions=[]` for visible books, so API consumers can distinguish safe read-only view links from unavailable management workflows.
- Updated the `/books` page to show:
  - current vs default book meaning;
  - base currency, storage type, access role, metadata status, and read-only status;
  - safe links only to existing read-only views;
  - localized self-hosting operator guidance explaining that registry/default/upload/delete workflows are intentionally unavailable in the MVP.
- Added route/static checks that `/books` renders operator guidance fields and still does not render `uri_or_path` or raw backend guidance copy.
- Updated `README.md`, `CHANGELOG.md`, and `PROJECT_STATUS.md` for Phase 148 state.

## Verification

- `cd apps/api && pytest -q tests/test_multi_book_access.py` — passed: `32 passed, 1 warning`.
- `cd apps/web && npm run test:auth-routes` — passed: `auth route checks passed`.
- `cd apps/web && npm run check` — passed: `svelte-check found 0 errors and 0 warnings`.
- Full standard checks were run after documentation updates before commit:
  - `cd apps/api && pytest -q` — passed: `380 passed, 32 warnings`;
  - `cd apps/web && npm run build` — passed;
  - `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — passed;
  - `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'` — confirmed API and web remain `"false"`;
  - `git diff --check` — passed;
  - sensitive tracked-file hygiene scan — passed.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- No upload/delete/default-changing UI, registry editing, multi-user admin console, write endpoint, write-mode UI expansion, release/tag/package, browser storage, screenshot, CSV/export artifact, app DB, backup, real/private GnuCash book, `.env`, token, key, cert, private path, or real/private financial data was added.
- `/books` listing guidance is app metadata only and does not open private GnuCash data just for listing.
- The frontend intentionally does not render `uri_or_path` or raw backend guidance copy.

## Files changed

- `apps/api/app/routers/books.py`
- `apps/api/tests/test_multi_book_access.py`
- `apps/web/src/lib/api/types.ts`
- `apps/web/src/lib/i18n/messages.ts`
- `apps/web/src/routes/books/+page.svelte`
- `apps/web/scripts/test-auth-routes.mjs`
- `README.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-148.md`
