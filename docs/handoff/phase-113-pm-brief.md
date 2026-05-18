# Phase 113 PM brief — Russian localization glossary and narrow UI slice

Date: 2026-05-19
Roadmap source: analyst Phase 8
Related GitHub issues: #17, #29

## Decision

Proceed with a narrow, user-visible Russian localization improvement for transaction filters and CSV export copy, supported by an accounting/safety glossary. English remains canonical and the translation stays explicitly partial.

## Goal

Add consistent Russian terminology for a high-value read-only UI slice: transaction filters, active filter summary, date presets, split reconciliation state labels, clear/reset action, and CSV export helper copy.

## Non-goals

- Do not make Russian the canonical/default language.
- Do not claim full Russian localization.
- Do not localize backend/API errors in this phase.
- Do not add browser storage, saved searches, auth/session changes, write-mode UI changes, releases, tags, or publication steps.
- Do not weaken safety warnings or imply production readiness.

## Acceptance criteria

- `docs/localization.md` includes an accounting/safety glossary for stable Russian terms, including read-only, authoritative GnuCash Desktop editor, not production-ready, not security-audited, split reconciliation state, CSV export, and partial translation.
- Transaction filter/export UI strings use the existing catalog and render English/Russian through the existing `ui_locale` cookie path.
- Russian copy preserves safety semantics: filters and CSV export are read-only and never modify the GnuCash book; GnuCash Desktop remains authoritative; write mode remains post-MVP/disabled by default.
- Existing URL filter behavior, CSV export query preservation, and language toggle behavior remain stable.

## Safety checks

- Keep `GNUCASH_WRITES_ENABLED=false` default unchanged.
- Do not touch write endpoints or write services.
- Do not store search strings/account IDs/amounts in localStorage/sessionStorage.
- Do not commit real GnuCash books, app DBs, exports, screenshots, `.env`, backups, certs, tokens, keys, or private data.
- Keep money logic unchanged; no float money logic and no fake currency conversion.

## Verification

- `cd apps/web && npm run test:auth-routes`
- `cd apps/web && npm run check`
- `cd apps/web && npm run build`
- `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet`
- `git diff --check`

## Files/docs to update

- `apps/web/src/lib/i18n/messages.ts`
- `apps/web/src/lib/components/TransactionFilters.svelte`
- `apps/web/src/routes/transactions/+page.svelte`
- `apps/web/src/routes/accounts/[id]/+page.svelte`
- `apps/web/scripts/test-auth-routes.mjs`
- `docs/localization.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `docs/handoff/phase-113.md`

## GitHub/backlog

Update GitHub #17/#29 with concise evidence if `gh` is authenticated. Do not close broader localization issues unless their full scope is clearly complete.
