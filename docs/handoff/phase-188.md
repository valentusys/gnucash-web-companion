# Phase 188 — read-only reporting correctness edge cases

Date: 2026-05-20
Status: COMPLETE — reporting correctness edge cases hardened before any next release claim
Roadmap source: `/home/val/.hermes/logs/gnucash-web-companion/triple-analyst-10phase-20260520-112544/cycle-2-roadmap.md` (Phase 7 only)

## Goal

Strengthen money/accounting correctness for read-only dashboard/reporting before any next release claim.

## Scope completed

- Read required context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-187.md`;
  - roadmap file named by the phase contract;
  - relevant report service/router tests and dashboard drilldown/UI/static-check files.
- Added backend report edge-case coverage in `apps/api/tests/test_reports.py` for:
  - zero-balance fallback to current base-currency asset/liability splits while keeping JSON money amounts as strings;
  - mixed-currency transactions where non-base split amounts are excluded, not converted, and their currency is disclosed in limitations;
  - signed negative/contra asset and liability balances without sign normalization or float conversion.
- Kept existing real synthetic multi-currency fixture coverage in `apps/api/tests/test_multicurrency_reports.py` for:
  - unknown `XXX` base currency;
  - base-currency-only/no-conversion limitations;
  - excluded EUR accounts/splits from summary, cashflow, and expenses-by-account.
- Hardened `GnuCashBookService.get_report_summary()` limitations so excluded currencies seen in transaction splits are disclosed, not only currencies present in the account listing loop.
- Updated dashboard route/static checks:
  - dashboard drilldowns preserve existing transaction URL-filter parity for `account_id`, date ranges, `limit=50`, and `offset=0`;
  - `dashboard/+page.server.ts` no longer uses `Number()` in reporting/drilldown path parsing.
- Updated `docs/money-model.md` to document mixed-currency split exclusion and unknown-base zero-total semantics.

## Files changed

- `apps/api/app/services/gnucash_book.py`
- `apps/api/tests/test_reports.py`
- `apps/web/src/routes/dashboard/+page.server.ts`
- `apps/web/scripts/test-auth-routes.mjs`
- `docs/money-model.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-188.md`

## Verification summary

Commands/results recorded for this phase:

```bash
cd apps/api && pytest tests/test_reports.py tests/test_multicurrency_reports.py -q
cd apps/api && pytest -q
cd apps/web && npm run check && npm run test:auth-routes && npm run build
# Search checks over dashboard/reporting frontend paths for Number(
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'
git diff --check
# Sensitive tracked-file hygiene scan from AGENTS/phase execution playbook
```

Results:

- Targeted backend report tests passed (`47 passed`, existing piecash/SQLAlchemy warnings only).
- Full backend suite passed (`457 passed`, existing piecash/SQLAlchemy/FastAPI warnings only).
- Frontend `npm run check`, auth-route/static checks, and production build passed.
- Search for `Number(` in the changed dashboard route returned no executable usage; dashboard/components reporting paths have no runtime `Number()` money parsing.
- Docker Compose config passed and kept `GNUCASH_WRITES_ENABLED: "false"` for api/worker services.
- `git diff --check` passed.
- Sensitive tracked-file hygiene scan passed.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- No write behavior, FX conversion, forecasting, external rates, accounting-engine rewrite, release, tag, package, or production accounting guarantee was added.
- Backend report arithmetic remains `Decimal`/string based; JSON money amounts remain strings; no fake conversion is performed.
- No real/private book, runtime app DB, runtime book, backup, lock artifact, `.env`, token, key, cert, screenshot, export, raw path, amount, memo, account name, or private financial data was committed.

## Next

Proceed only to the next roadmap phase when explicitly requested. Do not start fresh-clone smoke, release-candidate dogfood, or release-readiness work from this phase.
