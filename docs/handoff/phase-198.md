# Phase 198 — Multi-book read-only registry diagnostics hardening

Date: 2026-05-20
Status: COMPLETE — implemented, tested, committed/pushed
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-112544/cycle-3-roadmap.md` (Phase 7 only)

## Goal

Improve safe multi-book readiness around GitHub #13 without management/write expansion: operators get actionable diagnostics, while users never see raw paths or inaccessible books.

## Scope completed

- Read required context: `AGENTS.md`, `PROJECT_STATUS.md`, latest handoff `docs/handoff/phase-197.md`, roadmap file, backend books/router tests, frontend book-context code, and `/books` UI/static checks.
- Hardened backend `/books` metadata for accessible independent books:
  - added safe `status_severity` values for available, remote/unchecked, missing-file, and not-configured states;
  - added safe access-role labels/descriptions for owner/editor/viewer without exposing inaccessible books;
  - added `can_open_read_only_views` so missing/not-configured books can be listed diagnostically without advertising broken data-view actions;
  - kept `uri_or_path` out of API responses and kept listing app-metadata-only.
- Hardened frontend `/books` flows:
  - renders safe access-role copy and status severity;
  - hides read-only data-view links for missing/not-configured books and shows a safe diagnostics-only message instead;
  - keeps touch-friendly wrapping controls for mobile;
  - server-validated `/books/[bookId]/select` now refuses accessible-but-unavailable books and returns users to `/books` with a safe notice.
- Expanded route/static checks and multi-book backend tests for diagnostics, route-family access, and no raw-path exposure.
- Added synthetic dogfood evidence in `docs/dogfood/phase-198-multibook-readonly-diagnostics.md`.

## Files changed

- `apps/api/app/routers/books.py`
- `apps/api/tests/test_multibook_readonly_access.py`
- `apps/web/src/lib/api/types.ts`
- `apps/web/src/lib/i18n/messages.ts`
- `apps/web/src/routes/books/+page.server.ts`
- `apps/web/src/routes/books/+page.svelte`
- `apps/web/src/routes/books/[bookId]/select/+server.ts`
- `apps/web/scripts/test-auth-routes.mjs`
- `docs/dogfood/phase-198-multibook-readonly-diagnostics.md`
- `docs/handoff/phase-198.md`
- `PROJECT_STATUS.md`

## Verification summary

Commands/results:

```bash
cd apps/api && pytest tests/test_multibook_readonly_access.py tests/test_multi_book_access.py -q
# 76 passed, 1 existing piecash/SQLAlchemy warning

cd apps/web && npm run test:auth-routes
# auth route checks passed

cd apps/web && npm run check
# svelte-check found 0 errors and 0 warnings
```

Additional standard checks were run before commit and are recorded in the final phase report.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains default.
- No GnuCash writes were enabled or executed.
- No upload/delete/default-changing/registry-edit UI was added.
- No collaborative/family-wallet workflow was added.
- No real/private books, app DB, backups, `.env`, tokens, keys, screenshots, exports, or raw paths were committed.
- `selected_book_id` remains a non-secret server-validated cookie; no client-side selected-book cookie writes and no sensitive `localStorage`/`sessionStorage` state were added.
- Listing diagnostics remain app-metadata-only and do not open GnuCash books.

## Risks / follow-up

- This phase improves readiness/diagnostics only; it does not add UI registry management.
- Full Docker/Caddy browser dogfood with a two-book runtime setup remains a useful later release-regression task if a dedicated synthetic two-book runtime helper is added.

## Next

Do not start another roadmap phase from this session. Next work should be explicitly requested and scoped separately.
