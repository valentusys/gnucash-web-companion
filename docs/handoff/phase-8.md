# Phase 8 Handoff — Dashboard and Basic Read-Only Reports

## Scope

Phase 8 adds a dashboard-oriented reports layer on top of the existing read-only GnuCash service and exposes it through authenticated FastAPI endpoints and a mobile-first SvelteKit dashboard.

This phase remains strictly read-only. It does not write to GnuCash, does not implement budgets, and does not add complex accounting reports or charting dependencies.

## Backend

### New router

- `apps/api/app/routers/reports.py`

Registered from `apps/api/app/main.py`.

### Book-aware endpoints

- `GET /books/{book_id}/reports/summary`
- `GET /books/{book_id}/reports/cashflow`
- `GET /books/{book_id}/reports/expenses-by-account`
- `GET /books/{book_id}/reports/recent-transactions`

### MVP default-book aliases

- `GET /reports/summary`
- `GET /reports/cashflow`
- `GET /reports/expenses-by-account`
- `GET /reports/recent-transactions`

### Auth and access control

All report endpoints require authentication via the existing auth dependency.

Book-aware endpoints resolve the requested book and enforce view access with the existing `BookAccessService` flow used by accounts and transactions. MVP aliases resolve the default viewable book.

### Service layer additions

Updated `apps/api/app/services/gnucash_book.py`:

- `get_report_summary(as_of_date=None)`
- `get_expenses_by_account(date_from=None, date_to=None)`
- `get_cashflow_by_month(date_from, date_to)`

Existing methods reused:

- `get_cashflow(date_from, date_to)`
- `list_transactions(limit, offset)` for recent transactions

### Schemas

Updated `apps/api/app/schemas/gnucash.py`:

- `ReportSummaryDTO`
- `ExpenseByAccountDTO`
- `CashflowPeriodDTO`

Summary response fields:

```json
{
  "currency": "SEK",
  "net_worth": "120000.00",
  "assets": "150000.00",
  "liabilities": "-30000.00",
  "income_this_month": "45000.00",
  "expenses_this_month": "-22000.00",
  "as_of_date": "2026-05-16"
}
```

All money values are strings. Internally report calculations use `Decimal` and never floats.

### Date defaults

For cashflow and expenses-by-account endpoints, if `date_from` or `date_to` is omitted, the endpoint defaults to current month through today.

### Multi-currency limitation

No currency conversion is performed.

Dashboard reports currently aggregate only accounts/splits whose commodity matches the configured book `base_currency`. Accounts and splits in other currencies are excluded from totals rather than converted with guessed or stale FX rates.

This is intentional for MVP safety and correctness. Future multi-currency reporting should add explicit exchange-rate policy and UI disclosure before changing totals.

## Frontend

### Dashboard route

Updated `/dashboard`:

- `apps/web/src/routes/dashboard/+page.server.ts`
- `apps/web/src/routes/dashboard/+page.svelte`

The server load fetches summary, expenses-by-account, monthly cashflow, and recent transactions from the backend using the existing httpOnly-cookie auth flow.

### New components

- `apps/web/src/lib/components/BalanceCard.svelte`
- `apps/web/src/lib/components/SummaryGrid.svelte`
- `apps/web/src/lib/components/RecentTransactions.svelte`
- `apps/web/src/lib/components/ExpensesByAccount.svelte`
- `apps/web/src/lib/components/CashflowSummary.svelte`

### UI behavior

- Mobile-first layout.
- Summary cards for net worth, assets, liabilities, income this month, and expenses this month.
- Recent transactions list.
- Expenses by account list with lightweight CSS bars, no chart library.
- Cashflow monthly summary.
- Empty states for missing reports, transactions, expenses, and cashflow.
- Top-level dashboard load error shown if summary cannot be loaded.

## Tests

New backend tests:

- `apps/api/tests/test_reports.py`

Coverage includes:

- Auth required for reports.
- Summary response shape.
- Summary values and signed expenses.
- Recent transactions response shape and limit.
- Expenses-by-account shape and sorting.
- Cashflow shape and monthly grouping.
- Book-aware report endpoints.
- Access denied behavior.
- Multi-currency limitation: non-base-currency account totals are excluded rather than converted.

## Verification

Backend:

```bash
cd apps/api
pytest -q
```

Result:

```text
129 passed, 1 skipped, 1 warning
```

Frontend:

```bash
cd apps/web
npm run check
npm run test:auth-routes
npm run build
```

Result:

```text
svelte-check found 0 errors and 0 warnings
auth route checks passed
vite build OK
```

## Safety notes

- No GnuCash write operations were added.
- Routes call `GnuCashBookService`; they do not use piecash directly.
- Report calculations use existing read-only book opening.
- No `book.save()`, `session.commit()`, mutation, or write path was introduced.
- No heavy charting library was added.
- No budgets or complex accounting reports were added.

## Next possible phases

- Add lightweight report period controls in UI.
- Add explicit multi-currency disclosure in dashboard UI.
- Add optional report endpoint response metadata for excluded currencies.
- Add Docker runtime testing when Docker is available on the host.
