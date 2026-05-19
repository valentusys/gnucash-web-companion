# Money Model and Sign Conventions

This document records the current read-only money-handling rules for `gnucash-web-companion`.

## Scope

The MVP remains read-only by default. These rules describe how existing GnuCash values are read, formatted, exported, and displayed. They do not add write scope, currency conversion, import, synchronization, or any production-safety guarantee.

## Representation

- Backend money arithmetic uses Python `Decimal` values.
- API DTOs expose money amounts as decimal strings, not JSON numbers.
- CSV export writes the same decimal string amounts returned by the read-only transaction list DTOs.
- New money-related code must not use floats for core money calculations.
- `GNUCASH_WRITES_ENABLED=false` remains the default; controlled writes remain experimental post-MVP only.

## Read-only API and CSV behavior

Read-only account, transaction, split, report, and CSV-export amounts are formatted as strings such as:

```text
123.45
-320.00
0.00
```

The CSV transaction export includes these money-related columns:

```text
amount,currency
```

The export is read-only and preserves decimal string values. Exported CSV files can contain sensitive financial data; do not commit real exports.

## Sign conventions

The app preserves GnuCash/piecash split signs rather than inventing a separate accounting convention:

- Transaction list item `amount` is the selected/relevant split amount.
- Transaction detail shows every split with its own signed amount.
- Multi-split transaction list rows use `counter_account_name = "Split transaction"` to avoid pretending there is a single counter account.
- Dashboard cashflow/report code interprets income and expense account signs conservatively in the service layer and returns display strings.
- Negative values may represent liabilities, outflows, reversals, or GnuCash account-type-specific sign behavior depending on context.

Do not assume every negative number is “bad” or every positive number is “income” without account-type context.

## Multi-currency behavior

No fake currency conversion is performed.

Current basic report totals include only values whose account/split commodity matches the configured book `base_currency`. Non-base-currency values are excluded from those totals rather than converted using guessed or stale exchange rates.

Future multi-currency reporting must define an explicit exchange-rate source, date policy, and UI disclosure before combining currencies.

## Frontend display note

Frontend components should treat backend money values as strings for display. If the UI needs sign styling or proportional bars, prefer string/sign helpers or a decimal-safe utility over JavaScript floating-point arithmetic. Backend `Decimal` validation remains authoritative for filtering and API behavior.

## Dashboard drilldowns

Dashboard report-card drilldowns are read-only navigation helpers. They preserve the active book through the existing selected-book context and open `/transactions` with URL filters such as `date_from`, `date_to`, `account_id`, `limit=50`, and `offset=0`.

These links do not add a new accounting engine and do not recompute totals in the browser. Summary income/expense links expose the same current-month transaction period behind the card; expense-by-account links add the report account id; cashflow month links add the exact month date range. CSV export remains parity-compatible because the transactions page builds exports from the same URL filter state.

Dashboard totals remain base-currency-only and no FX conversion is inferred from a drilldown transaction view.
