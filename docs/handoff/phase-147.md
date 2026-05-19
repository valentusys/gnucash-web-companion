# Phase 147 — Dashboard/reporting limitation clarity

Date: 2026-05-19
Status: DONE

## Goal

Make dashboard/reporting totals honest and understandable for mixed-currency and base-currency-only limitations.

## Scope completed

- Read required project context:
  - `AGENTS.md`;
  - `PROJECT_STATUS.md`;
  - latest handoff `docs/handoff/phase-146.md`;
  - analyst roadmap `/home/val/.hermes/logs/gnucash-web-companion/analyst-roadmap-20260519-195139/analyst-roadmap.md`.
- Kept this as Phase 147 only; no PM/auditor was involved and no later roadmap phase was started.
- Clarified backend dashboard summary limitations in `GnuCashBookService.get_report_summary()`:
  - summary limitations now explicitly state `reporting_basis=base_currency_only`;
  - summary limitations explicitly state that currency conversion is not included;
  - mixed-currency books name detected excluded non-base currencies, e.g. `EUR`, instead of implying converted/combined totals;
  - unknown configured base currency `XXX` explains that zero totals may mean no matching base-currency accounts rather than an empty book.
- Kept `ReportSummaryDTO.reporting_basis="base_currency_only"` and `includes_currency_conversion=false` as explicit API metadata.
- Updated the dashboard page to show reporting basis and currency-conversion status before backend limitation bullets.
- Added backend regression coverage for:
  - mixed-currency summary metadata and no-conversion wording;
  - unknown `XXX` base-currency zero-total explanation.
- Added frontend route/static coverage to pin dashboard rendering of reporting basis, conversion status, and backend limitations.
- Updated `README.md`, `CHANGELOG.md`, and `PROJECT_STATUS.md` for Phase 147 state.

## Verification

- `cd apps/api && pytest -q tests/test_multicurrency_reports.py` — passed: `15 passed, 21 warnings`.
- `cd apps/api && pytest -q tests/test_reports.py::TestReportSummaryMVP tests/test_multicurrency_reports.py` — passed after updating existing report-shape expectations for the new limitation wording: `23 passed, 21 warnings`.
- `cd apps/web && npm run test:auth-routes` — passed: `auth route checks passed`.
- `cd apps/web && npm run check` — passed: `svelte-check found 0 errors and 0 warnings`.
- Full standard checks were run after documentation updates before commit:
  - `cd apps/api && pytest -q` — passed: `379 passed, 32 warnings`;
  - `cd apps/web && npm run build` — passed;
  - `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet` — passed;
  - `JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config | grep -n 'GNUCASH_WRITES_ENABLED'` — confirmed API and web remain `"false"`;
  - `git diff --check` — passed;
  - sensitive tracked-file hygiene scan — passed.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- No fake FX conversion, external rates, production accounting guarantee, write endpoint, write-mode UI expansion, release/tag/package, browser storage, screenshot, CSV/export artifact, app DB, backup, real/private GnuCash book, `.env`, token, key, cert, private path, or real/private financial data was added.
- Money remains Decimal/string-handled; the phase only builds limitation copy from currency codes and renders existing DTO metadata.

## Files changed

- `apps/api/app/schemas/gnucash.py`
- `apps/api/app/services/gnucash_book.py`
- `apps/api/tests/test_multicurrency_reports.py`
- `apps/api/tests/test_reports.py`
- `apps/web/src/lib/api/types.ts`
- `apps/web/src/routes/dashboard/+page.svelte`
- `apps/web/scripts/test-auth-routes.mjs`
- `README.md`
- `CHANGELOG.md`
- `PROJECT_STATUS.md`
- `docs/handoff/phase-147.md`
