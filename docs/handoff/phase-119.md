# Phase 119 — Strip Root Account prefix from displayed account full names

Date: 2026-05-19
Status: complete
Previous phase: `docs/handoff/phase-118.md`

## Goal

Remove the extra synthetic GnuCash `Root Account:` prefix from displayed account full names while preserving child account paths and the existing read-only API contract.

## Scope completed

- Updated `apps/api/app/services/gnucash_book.py` so `account_full_name()` skips the GnuCash ROOT account when it is named `Root Account`.
- Preserved child paths, for example:
  - `Assets:Bank:Checking`
  - `Expenses:Food`
  - `Liabilities:Credit Card`
- Preserved account IDs, `parent_id` values, DTO/schema shape, route shape, and read-only service behavior.
- Updated backend tests whose expected values included `Root Account:`:
  - unit regression coverage for `account_full_name()`;
  - synthetic integration fixture split-name expectations;
  - compatibility fixture split-name expectations;
  - multicurrency expenses-by-account expectations.
- Verified the frontend continues to consume the same backend fields (`full_name`, `account_name`, `counter_account_name`) and therefore receives the cleaned display strings without a DTO/schema redesign.

## Non-goals preserved

- No DTO schema redesign.
- No account ID or parent-reference changes.
- No localization of ROOT account names.
- No account tree structure rewrite.
- No write-path or controlled-write changes.
- No release, tag, or package publication.

## Safety

- Read-only service/display cleanup only.
- `GNUCASH_WRITES_ENABLED=false` remains default.
- Controlled writes remain post-MVP/experimental and disabled by default.
- No real/private GnuCash book, app DB, backup, `.env`, screenshot, CSV export, secret, token, cert, key, private path, account name, transaction description, memo, amount, or personal financial data was added.

## Verification

TDD RED/GREEN evidence:

- RED: `cd apps/api && pytest tests/test_gnucash_book.py::test_full_account_name_skips_gnucash_root_account -q` failed before implementation because the value was `Root Account:Assets:Bank:Checking`.
- GREEN: targeted service tests passed after implementation.

Final checks run:

```bash
cd apps/api && pytest -q
cd apps/web && npm run check
cd apps/web && npm run test:auth-routes
cd apps/web && npm run build
JWT_SECRET=dummy-validation-secret APP_ADMIN_PASSWORD=dummy docker compose config --quiet
git diff --check
```

Results:

- Backend pytest: passed (`350 passed, 27 warnings`).
- Frontend check: passed, 0 errors, 0 warnings.
- Frontend auth route/static checks: passed.
- Frontend build: passed.
- Docker Compose config validation: passed.
- `git diff --check`: passed.

## Files changed

- `apps/api/app/services/gnucash_book.py`
- `apps/api/tests/test_gnucash_book.py`
- `apps/api/tests/test_integration_fixture.py`
- `apps/api/tests/test_compatibility_fixture_v1.py`
- `apps/api/tests/test_multicurrency_reports.py`
- `PROJECT_STATUS.md`
- `CHANGELOG.md`
- `docs/handoff/phase-119.md`

## Handoff notes

The cleanup intentionally targets the canonical synthetic ROOT label `Root Account` with type `ROOT`; it does not attempt ROOT-name localization or account-tree restructuring. UI components already render the service-layer `full_name`/`account_name`/`counter_account_name` fields, so no frontend DTO change is required.
