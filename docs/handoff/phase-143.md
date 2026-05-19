# Phase 143 — Read-only runtime status banner v2

Date: 2026-05-19
Status: DONE

## Goal

Make the active book and read-only/default-write-disabled runtime state explicit on key authenticated read-only pages after `v0.1.4-readonly`.

## Scope completed

- Read required project context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-142.md`;
  - analyst roadmap `/home/val/.hermes/logs/gnucash-web-companion/analyst-roadmap-20260519-195139/analyst-roadmap.md`.
- Kept this as Phase 143 only; no PM/auditor was involved and no later roadmap phase was started.
- Improved `ReadOnlyStatusBanner.svelte` so the authenticated app shell shows:
  - compact read-only/default status chip;
  - current active accessible book name, with a no-active-book fallback;
  - safe `/books` review link.
- Wired the root app shell to pass `activeBook` into the banner, so the status appears across the key authenticated read-only pages using the shared shell: dashboard, accounts, transactions, books, and scheduled.
- Updated localized safety copy to explicitly state `GNUCASH_WRITES_ENABLED=false` as the safe default and kept GnuCash Desktop as the authoritative editor.
- Extended frontend static/route checks to pin:
  - active-book wiring into the banner;
  - current-book rendering;
  - safe `/books` link;
  - default-disabled write-mode safety copy.
- Updated `PROJECT_STATUS.md` for Phase 143 completion.
- Added GitHub #13 evidence comment because the banner's safe `/books` link and current-book visibility are related to book-management/read-only metadata UX.

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
- No backend API or write route changed.
- No write UI, book upload, registry editing, default-changing, release/tag, package, or production/security claim was added.
- No localStorage/sessionStorage was introduced for sensitive data.
- No real/private GnuCash book, app DB, backup, `.env`, screenshot, CSV export, token, key, cert, private path, or real/private financial data was committed.

## Files changed

- `apps/web/src/lib/components/ReadOnlyStatusBanner.svelte`
- `apps/web/src/routes/+layout.svelte`
- `apps/web/src/lib/i18n/messages.ts`
- `apps/web/scripts/test-auth-routes.mjs`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-143.md`
