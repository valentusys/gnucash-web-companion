# Phase 113 — Russian localization glossary and transaction filter/export UI slice

Date: 2026-05-19
Status: complete
Related GitHub issues: #17, #29
PM brief: `docs/handoff/phase-113-pm-brief.md`

## Summary

Phase 113 implemented the analyst roadmap Phase 8 slice: a controlled Russian localization improvement without making Russian canonical. The phase added a durable accounting/safety glossary and localized one visible read-only UI area: transaction filters and CSV export copy.

## PM decision

Combine GitHub #17/#29 narrowly: improve terminology consistency and one high-value read-only UI slice, while preserving English as canonical, Russian as opt-in/partial, and all read-only/write-safety warnings.

## Implementation

Updated localization catalog and UI:

- `apps/web/src/lib/i18n/messages.ts`
  - added English/Russian keys for transaction filter headings/help, date preset helper copy, active filter summaries, account scope copy, state labels, validation messages, clear/reset action, and CSV export copy;
  - kept explicit safety wording that filters/exports are read-only and do not modify the GnuCash book.
- `apps/web/src/lib/components/TransactionFilters.svelte`
  - accepts the existing locale and renders transaction filter UI from the catalog;
  - localizes split reconciliation state labels and active filter summary labels;
  - keeps URL-only form behavior and does not add localStorage/sessionStorage.
- `apps/web/src/routes/transactions/+page.svelte`
  - localizes CSV export button/helper copy for the general transaction list;
  - preserves the current filter query-string export URL.
- `apps/web/src/routes/accounts/[id]/+page.svelte`
  - passes the locale into the shared transaction filters;
  - localizes the account-scoped CSV export button/helper copy while preserving fixed account scope.
- `apps/web/scripts/test-auth-routes.mjs`
  - adds static checks for the new catalog keys, Russian safety strings, localized transaction filters, and no browser storage for filter values.

Updated docs/status:

- `docs/localization.md`
  - added Phase 113 localized-surface notes;
  - added an English-canonical accounting/safety glossary covering read-only, GnuCash Desktop authority, not production-ready, not security-audited, controlled writes, split reconciliation states, CSV export, filtered view, and partial translation.
- `CHANGELOG.md` and `PROJECT_STATUS.md` updated for Phase 113.

## Safety

- `GNUCASH_WRITES_ENABLED=false` default was not changed.
- No backend write routes, write services, auth/session code, or browser storage for filters were added.
- The UI still treats transaction filters and CSV export as read-only operations.
- English remains canonical; Russian remains opt-in and partial.
- No production-ready, security-audited, hosted-SaaS, family-wallet, collaborative-accounting, or safe write-mode claim was added.
- No real/private GnuCash books, app DBs, backups, `.env`, screenshots, CSV exports, secrets, tokens, certs, keys, private paths, account names, transaction descriptions, memos, amounts, or personal financial data were committed.
- Money logic was not changed; no float money logic or fake currency conversion was added.
- No tag, GitHub release, package, or release artifact was published.

## Verification

Passed:

```bash
cd apps/api && pytest -q
# 349 passed, 27 warnings

cd apps/web && npm run test:auth-routes
# auth route checks passed

cd apps/web && npm run check
# svelte-check found 0 errors and 0 warnings

cd apps/web && npm run build
# passed

JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
# passed

git diff --check
# passed
```

## Files changed

- `apps/web/src/lib/i18n/messages.ts`
- `apps/web/src/lib/components/TransactionFilters.svelte`
- `apps/web/src/routes/transactions/+page.svelte`
- `apps/web/src/routes/accounts/[id]/+page.svelte`
- `apps/web/scripts/test-auth-routes.mjs`
- `docs/localization.md`
- `docs/handoff/phase-113-pm-brief.md`
- `docs/handoff/phase-113.md`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`

## GitHub

- Updated #17 with Phase 113 evidence: https://github.com/valentusys/gnucash-web-companion/issues/17#issuecomment-4482969226
- Updated #29 with Phase 113 evidence: https://github.com/valentusys/gnucash-web-companion/issues/29#issuecomment-4482969359
- Do not close broader localization issues unless their full scope is confirmed complete.

## Commit/push

- Commit: this commit (`Add Russian localization glossary and transaction UI slice`); final SHA is recorded in controller stdout.
- Push: pending at handoff creation time; expected target `origin/main`.
