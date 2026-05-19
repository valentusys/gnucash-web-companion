# Phase 159 — Release-critical frontend localization pass

Date: 2026-05-19
Status: DONE — release-critical dashboard/scheduled/landing copy now routes through the English/Russian i18n catalog
Starting HEAD: `84ac9e5`
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260519-214704/cycle-1-roadmap.md` (cycle 1/3, phase 8/10 only)

## Goal

Reduce partial-localization friction on the highest-value read-only paths without claiming full Russian translation.

## Scope completed

- Read required project context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-158.md`;
  - roadmap phase 8 and common safety constraints from `cycle-1-roadmap.md`.
- Kept this as Phase 159 only; no neighboring roadmap phases were started.
- Extended the existing typed i18n helper so `t(locale, key, replacements)` supports simple named interpolation for localized count/summary copy.
- Expanded the English/Russian message catalog for release-critical read-only frontend copy:
  - dashboard report cards and drilldown safety helper copy;
  - recent transactions widget labels/actions/empty state;
  - expenses-by-account helper/empty state;
  - cashflow helper/in/out/net labels/empty state;
  - unauthenticated landing subtitle/sign-in action via the catalog;
  - `/scheduled` title, read-only safety copy, active book label, URL-only filters/sorting, metadata labels, recurrence summaries, counts, and empty states.
- Updated dashboard and scheduled UI to render the new strings with `t(locale, '...')`; the root landing page uses the default locale fallback because it has no route locale payload.
- Updated frontend static route checks to pin catalog usage and conservative no-conversion/scheduled safety wording.
- Updated localization/status docs: `docs/localization.md`, `README.ru.md`, `CHANGELOG.md`, and `PROJECT_STATUS.md`.

## Verification

Targeted/frontend checks:

```bash
cd apps/web && npm run test:auth-routes
cd apps/web && npm run check
cd apps/web && npm run build
```

Results: passed. `svelte-check` reported 0 errors and 0 warnings.

Standard checks:

```bash
cd apps/api && pytest -q
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
git diff --check
```

Results: passed. Backend test result: `386 passed, 32 warnings`. Rendered Compose config keeps `GNUCASH_WRITES_ENABLED: "false"`.

Sensitive tracked-file hygiene scan: passed.

## Safety boundaries

- English remains canonical; Russian remains partial/opt-in.
- No full-app translation claim was added.
- Backend/API error localization was not rewritten.
- `GNUCASH_WRITES_ENABLED=false` remains the default.
- Controlled writes remain post-MVP/experimental and were not expanded or enabled.
- No release/tag/package was published.
- No browser `localStorage`/`sessionStorage` persistence was added for sensitive data.
- No real/private GnuCash book, `.env`, app DB, backup, screenshot/export, token, key, cert, private path, or private financial data was committed.

## Files changed

- `apps/web/src/lib/i18n/index.ts`
- `apps/web/src/lib/i18n/messages.ts`
- `apps/web/src/routes/+page.svelte`
- `apps/web/src/routes/dashboard/+page.svelte`
- `apps/web/src/routes/scheduled/+page.svelte`
- `apps/web/src/lib/components/SummaryGrid.svelte`
- `apps/web/src/lib/components/RecentTransactions.svelte`
- `apps/web/src/lib/components/ExpensesByAccount.svelte`
- `apps/web/src/lib/components/CashflowSummary.svelte`
- `apps/web/scripts/test-auth-routes.mjs`
- `docs/localization.md`
- `README.ru.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-159.md`
