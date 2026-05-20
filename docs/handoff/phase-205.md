# Phase 205 — Multi-book read-only recovery polish

Date: 2026-05-20
Status: COMPLETE — unavailable selected-book contexts now recover to safe openable read-only books or `/books` review
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-220851/cycle-1/roadmap-cycle-1.md` (Cycle 1, Phase 4 only)

## Goal

Improve read-only multi-book recovery and navigation for inaccessible, archived, missing, and stale selected-book contexts without adding management actions.

## Scope completed

- Read required context: `AGENTS.md`, `PROJECT_STATUS.md`, latest handoff `docs/handoff/phase-204.md`, and the cycle-1 roadmap file.
- Updated frontend active-book resolution so read-only data routes use only books that the backend lists as accessible and openable via `can_open_read_only_views`.
- Added a distinct `unavailable_selected_book` recovery case for selected-book cookies that point to accessible metadata entries whose storage is missing or not configured.
- Kept stale/unauthorized/archived recovery safe: unauthorized and archived books remain hidden or blocked by backend access checks; stale cookies fall back to an openable accessible book when present; otherwise the cookie is cleared and users are redirected to `/books`.
- Kept `/books` as the safe review path with localized notices for stale/invalid, unavailable, and no-accessible-book recovery cases.
- Hardened server-validated book selection links to preserve safe query strings only for approved read-only app paths (`/dashboard`, `/accounts`, `/transactions`, `/scheduled`) and reject external/management destinations.
- Updated frontend route/static checks to pin openable-book fallback, unavailable-book copy, safe query-preserving selection links, no client-side selected-book cookie writes, and no management actions.

## Files changed

- `apps/web/src/lib/api/server.ts`
- `apps/web/src/routes/books/[bookId]/select/+server.ts`
- `apps/web/src/routes/books/+page.svelte`
- `apps/web/src/lib/i18n/messages.ts`
- `apps/web/scripts/test-auth-routes.mjs`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-205.md`

## Verification summary

Commands/results:

```text
cd apps/api && pytest tests/test_multibook_readonly_access.py tests/test_multi_book_access.py -q
# passed: 76 passed; existing piecash/SQLAlchemy warning only

cd apps/api && pytest -q
# passed: 478 passed; existing piecash/SQLAlchemy/FastAPI warnings only

cd apps/web && npm run check
# passed: svelte-check found 0 errors and 0 warnings

cd apps/web && npm run test:auth-routes
# passed: auth route checks passed

cd apps/web && npm run build
# passed

JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config --quiet
# passed

JWT_SECRET=<dummy-local-secret> APP_ADMIN_PASSWORD=<dummy-local-password> docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
# rendered false for API and web

git diff --check
# passed

SMOKE_ADMIN_PASSWORD=<dummy-local-password> scripts/smoke/read-only-api-smoke.py
# passed against local Docker/Caddy with committed synthetic fixture copied to ignored data/books/ and GNUCASH_WRITES_ENABLED=false; validate/create/PATCH/DELETE returned 403
```

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains default.
- Access checks remain backend-enforced; frontend recovery only uses `/books` metadata returned by authenticated backend APIs.
- Archived and unauthorized books remain hidden or blocked by backend route families.
- Missing/not-configured accessible books do not become active data-route contexts; users are sent to `/books` for safe diagnostics.
- Auth remains httpOnly-cookie based; no localStorage/sessionStorage was added.
- No upload/delete/default-changing/registry-edit UI, write route, SaaS/collaborative/family-wallet positioning, real/private book, app DB, backup, committed `.env`, screenshot/export, token, key, cert, raw private path, or private financial data was added.
- The local smoke copied only the committed synthetic fixture into ignored runtime storage and removed `.env`, runtime book, app DB, backups, and locks after teardown.

## Risks / follow-up

- `/books` still shows app-metadata diagnostics only; it does not repair registry entries or mounts.
- Query preservation is intentionally limited to approved read-only route families and same-origin relative paths.
- Browser screenshot evidence was intentionally avoided and not committed.

## Next

Do not start another roadmap phase from this session. Next work should be explicitly requested and scoped separately.
