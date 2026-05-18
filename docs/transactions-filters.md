# Transaction Search and Filter Behavior

This document describes the current read-only transaction search, filtering, pagination, and CSV export behavior.

## Scope

Transaction filters only narrow read-only views and exports. They never create, edit, delete, import, or synchronize GnuCash data. GnuCash Desktop remains the authoritative editor, and `GNUCASH_WRITES_ENABLED=false` remains the safe default.

## Supported filters

The transactions page and API support these filters:

- `query` — text search over transaction descriptions and related split/account context as implemented by the backend service layer.
- `date_from` — inclusive lower date bound, formatted as `YYYY-MM-DD`.
- `date_to` — inclusive upper date bound, formatted as `YYYY-MM-DD`.
- `account_id` — account GUID filter.
- `min_amount` — inclusive lower absolute amount bound, represented as a decimal string.
- `max_amount` — inclusive upper absolute amount bound, represented as a decimal string.
- `transaction_state` — optional split reconciliation-state filter. Supported values are `unreconciled`, `cleared`, `reconciled`, and `voided`, mapped to GnuCash split `reconcile_state` values exposed by piecash. Without an account filter it matches transactions with any split in that state; with `account_id` or account-detail transaction lists it matches the selected account split state.
- `limit` and `offset` — pagination for list views only.

## Validation

The backend rejects invalid or inverted filter ranges before opening/querying the GnuCash book:

- `date_from` later than `date_to` returns HTTP 400.
- malformed `date_from` or `date_to` values return HTTP 400.
- `min_amount` greater than `max_amount` returns HTTP 400.
- unsupported `transaction_state` values return HTTP 400 before opening/querying the book.

The frontend also blocks inverted date and amount ranges before navigating, so normal UI use shows an inline error instead of loading an invalid filtered page.

## URL and pagination behavior

The transactions page reflects active filters in the URL query string:

```text
/transactions?query=ica&date_from=2026-05-01&date_to=2026-05-31&account_id=...&min_amount=10&max_amount=500&transaction_state=cleared&limit=50&offset=0
```

Changing filters resets `offset` to `0`. Pagination preserves the active filters and changes only the offset.

## CSV export parity

The CSV export link preserves the same active filters as the list view:

```text
/books/<book_id>/transactions/export?query=ica&date_from=2026-05-01&date_to=2026-05-31&account_id=...&min_amount=10&max_amount=500&transaction_state=cleared
```

CSV export intentionally does not include `limit` or `offset`; it exports the matching filtered set from the first row, capped at 10,000 rows. This keeps export parity with filters while avoiding page-only pagination limits.

## CSV export cap, truncation, and timeout behavior

CSV export is generated synchronously during the HTTP request. The app does not run CSV export as a background job and does not stream an unbounded full-book export. If an operator, reverse proxy, or browser request times out before completion, narrow the date/account/query/amount filters and retry; no GnuCash data is modified.

The backend always applies `CSV_EXPORT_LIMIT = 10_000` rows. A successful export response includes these advisory headers so operators and the web proxy can detect large-export behavior without parsing the CSV body:

```text
X-CSV-Export-Limit: 10000
X-CSV-Export-Total: <matching row count before cap>
X-CSV-Export-Truncated: true|false
X-CSV-Export-Timeout-Policy: synchronous-request-timeout
```

When `X-CSV-Export-Truncated` is `true`, the CSV contains only the first 10,000 matching transactions for the current filters. Apply narrower filters if a complete subset is needed.

## Safety notes

- Export is read-only.
- Export files may contain sensitive financial data; do not commit real exports.
- State filtering is read-only and reflects the split reconciliation state stored by GnuCash; it does not infer a new transaction workflow or edit cleared/reconciled flags.
- No currency conversion is performed or implied.
- Amounts remain string/Decimal-style values; do not use floats for money in new code.
