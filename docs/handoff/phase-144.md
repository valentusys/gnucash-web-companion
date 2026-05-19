# Phase 144 — Account tree discoverability and heavy-account UX polish

Date: 2026-05-19
Status: DONE

## Goal

Improve read-only account-tree discoverability and large/heavy-account browsing UX without changing backend write paths.

## Scope completed

- Read required project context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-143.md`;
  - analyst roadmap `/home/val/.hermes/logs/gnucash-web-companion/analyst-roadmap-20260519-195139/analyst-roadmap.md`.
- Kept this as Phase 144 only; no PM/auditor was involved and no later roadmap phase was started.
- Added a local account-tree filter in `AccountTree.svelte`:
  - accessible `type="search"` control with status text;
  - searches account `name`, `full_name`, `type`, and `currency`;
  - preserves parent paths when a matching descendant is found;
  - shows filtered/total counts;
  - provides clear no-match copy.
- Kept filtering URL-free and client-local for discoverability only; it does not call API routes, does not persist private account search terms in browser storage, and does not mutate any book data.
- Extended frontend static/route checks to pin:
  - accessible account filter wiring;
  - parent-path preservation for descendant matches;
  - search fields and filtered-count status copy;
  - read-only helper copy;
  - no `localStorage`/`sessionStorage`, fetch/API, or POST/write behavior in the account tree filter.
- Updated `PROJECT_STATUS.md` for Phase 144 completion.

## Verification

- `cd apps/web && npm run test:auth-routes` — passed: `auth route checks passed`.
- `cd apps/web && npm run check` — passed: `svelte-check found 0 errors and 0 warnings`.
- `cd apps/api && pytest -q` — passed: `377 passed, 32 warnings`.
- `cd apps/web && npm run build` — passed.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — passed with no output.
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'` — confirmed API and web remain `"false"`.
- `git diff --check` — passed.
- Sensitive tracked-file hygiene scan — passed with the existing synthetic fixture/docs-image allowlist; no new private GnuCash book, app DB, backup, `.env`, token/key/cert, screenshot, export, or private financial artifact was added.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- No backend API, service-layer, DTO, schema, or write route changed.
- No write UI, book upload, registry editing, default-changing, release/tag, package, or production/security claim was added.
- No localStorage/sessionStorage was introduced for sensitive data or account filters.
- No real/private account names, GnuCash book, app DB, backup, `.env`, screenshot, CSV export, token, key, cert, private path, or real/private financial data was committed.

## Files changed

- `apps/web/src/lib/components/AccountTree.svelte`
- `apps/web/scripts/test-auth-routes.mjs`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-144.md`
