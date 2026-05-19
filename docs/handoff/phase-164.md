# Phase 164 — Book context and access edge-case hardening

Date: 2026-05-20
Status: DONE
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-resume-20260520-003549/cycle-2-roadmap.md` (cycle 2/3, phase 3/10 only)

## Goal

Harden the read-only multi-book foundation for GitHub #13 without adding management actions: reduce 403/404 confusion around invalid/stale selected-book cookies, archived/default mismatch, and missing configured books.

## Scope completed

- Read required context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-163.md`;
  - roadmap phase 3 and safety constraints from `cycle-2-roadmap.md`.
- Kept this as Phase 164 only; no neighboring roadmap phases were started.
- Updated frontend book-context resolution in `apps/web/src/lib/api/server.ts`:
  - classifies invalid selected-book cookie, stale/no-longer-accessible selected-book cookie, and no-accessible-book states;
  - keeps fallback order: selected accessible book, accessible default book, first accessible book;
  - replaces the non-secret `selected_book_id` cookie with the accessible fallback or clears it if no accessible book exists;
  - keeps selected-book state cookie-only, with no localStorage/sessionStorage.
- Updated layout/books UX:
  - protected read-only views redirect users with invalid/stale/no-accessible book context to `/books?book_context=...` for safe review;
  - `/books` renders a localized recovery notice and current/default labels before the user opens dashboard/accounts/transactions/scheduled views.
- Added static route checks for:
  - recovery classification;
  - cookie replacement/clearing;
  - `/books` review redirect;
  - allowlisted `/books` recovery notices;
  - absence of browser storage for book-sensitive state.
- Added `docs/book-switcher-readonly-model.md` documenting selected-book cookie scope, fallback order, recovery behavior, redaction, and no-management/no-write boundaries.
- Synchronized `CHANGELOG.md`, `PROJECT_STATUS.md`, and this handoff.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- No production writes were enabled.
- No upload/delete/default-changing/registry-edit UI was added.
- No direct file browser, collaborative workflow, family-wallet workflow, or GnuCash data write path was added.
- Backend access rules continue to hide archived books and block unauthorized books.
- Raw `uri_or_path` and private filesystem paths remain absent from book metadata API/UI.
- No real/private GnuCash book, app DB, backup, `.env`, screenshot/export, token, key, cert, private path, or private financial data was committed.

## Verification

```bash
cd apps/api && pytest tests/test_multi_book_access.py -q
cd apps/web && npm run test:auth-routes
cd apps/web && npm run check
cd apps/api && pytest -q
cd apps/web && npm run build
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
git diff --check
# sensitive tracked-file hygiene scan
```

Results:

- Targeted backend multi-book access tests passed: `36 passed, 1 warning`.
- Frontend auth/static route checks passed.
- Frontend `npm run check` passed with `0 errors and 0 warnings`.
- Backend full suite passed: `388 passed, 32 warnings`.
- Frontend production build passed.
- Docker Compose config validation passed.
- Rendered Compose config kept `GNUCASH_WRITES_ENABLED: "false"` for API and web.
- `git diff --check` passed.
- Sensitive tracked-file hygiene scan passed.

## Files changed

- `apps/web/src/lib/api/server.ts`
- `apps/web/src/routes/+layout.server.ts`
- `apps/web/src/routes/books/+page.server.ts`
- `apps/web/src/routes/books/+page.svelte`
- `apps/web/src/lib/i18n/messages.ts`
- `apps/web/scripts/test-auth-routes.mjs`
- `docs/book-switcher-readonly-model.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-164.md`
