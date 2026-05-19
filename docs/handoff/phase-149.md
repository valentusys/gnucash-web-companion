# Phase 149 — Russian localization coverage for new read-only UX

Date: 2026-05-19
Status: DONE

## Goal

Keep Russian UI/docs usable for the new/changed read-only UX from Phases 143–148 without a full localization rewrite.

## Scope completed

- Read required project context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-148.md`;
  - analyst roadmap `/home/val/.hermes/logs/gnucash-web-companion/analyst-roadmap-20260519-195139/analyst-roadmap.md`.
- Kept this as Phase 149 only; no PM/auditor was involved and no later roadmap phase was started.
- Expanded the existing English/Russian i18n catalog for new read-only UX copy from the recent cycle:
  - account-tree filter label, filtered/all status, loading, empty-title, empty-action copy;
  - dashboard conservative totals, reporting-basis, and no-currency-conversion labels;
  - transaction filter state labels for unreconciled/cleared/reconciled/frozen states;
  - transaction detail helper copy and hidden-by-default write-alpha DELETE confirmation/acknowledgement copy;
  - transaction split memo, reconciliation state labels, and empty-state copy.
- Updated frontend routes/components to use catalog keys instead of hardcoded English for the covered copy.
- Updated route/static checks to pin catalog-key usage for the changed read-only UX.
- Updated localization documentation to document Phase 149 coverage boundaries.
- Synchronized public/status docs: `README.md`, `README.ru.md`, `CHANGELOG.md`, and `PROJECT_STATUS.md`.

## Verification

- `cd apps/web && npm run test:auth-routes` — passed: `auth route checks passed`.
- `cd apps/web && npm run check` — passed: `svelte-check found 0 errors and 0 warnings`.
- Full standard checks before commit:
  - `cd apps/api && pytest -q` — passed: `380 passed, 32 warnings`;
  - `cd apps/web && npm run build` — passed;
  - `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — passed;
  - `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'` — confirmed API and web remain `"false"`;
  - `git diff --check` — passed;
  - sensitive tracked-file hygiene scan — passed: `tracked sensitive scan: 0 unexpected candidate(s)`.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- English remains canonical; Russian remains partial and opt-in.
- No full-app localization rewrite, backend/API localization, production-readiness claim, security-audit claim, write expansion, release/tag/package, browser storage, screenshot, CSV/export artifact, app DB, backup, real/private GnuCash book, `.env`, token, key, cert, private path, or real/private financial data was added.
- Hidden-by-default write-alpha DELETE copy was localized only to keep existing gated UX understandable; the phase did not enable or expand controlled writes.

## Files changed

- `apps/web/src/lib/i18n/messages.ts`
- `apps/web/src/lib/components/AccountTree.svelte`
- `apps/web/src/lib/components/TransactionSplits.svelte`
- `apps/web/src/routes/accounts/+page.svelte`
- `apps/web/src/routes/dashboard/+page.svelte`
- `apps/web/src/routes/transactions/[id]/+page.svelte`
- `apps/web/src/routes/transactions/[id]/+page.server.ts`
- `apps/web/scripts/test-auth-routes.mjs`
- `docs/localization.md`
- `README.md`
- `README.ru.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-149.md`
