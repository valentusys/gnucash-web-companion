# Transaction Search and Filter Behavior

This document describes the current read-only transaction search, filtering, pagination, and CSV export behavior.

## Scope

Transaction filters only narrow read-only views and exports. They never create, edit, delete, import, or synchronize GnuCash data. GnuCash Desktop remains the authoritative editor, and `GNUCASH_WRITES_ENABLED=false` remains the safe default.

## Supported filters

The transactions page and API support these filters:

- `query` — case-insensitive substring search over transaction descriptions, transaction notes when exposed by the GnuCash/piecash object, and split memos. The same service-layer matcher is used for list, count, account-scoped, and CSV export paths.
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

The transactions page shows a compact current-view summary above the table: the visible page range, newest-first date ordering, whether filters are active, and a reminder that list pagination and CSV export share the same URL filters. This summary is display-only and does not store filter values in browser storage or app metadata.

Date preset links are plain URLs. They update only `date_from` and `date_to`, preserve other active filters (`query`, `account_id`, `min_amount`, `max_amount`, and `transaction_state`), and reset `offset` to `0`.

The transaction filter form also provides a one-click `Clear filters` link. It removes search, account, date, amount, and state filters, keeps only the current page size (`limit`) plus `offset=0`, and does not store the old filter values anywhere.

Filter presets and reset behavior are URL-only. The app does not save transaction search strings, account IDs, amount ranges, dates, or state filters in `localStorage`, `sessionStorage`, app metadata, or user profiles.

Persistent named/saved presets are intentionally not implemented in the current pre-alpha read-only line because they would store potentially private financial search terms and account identifiers. Use bookmarkable/shareable-by-the-user URLs instead; do not add browser or app-DB persistence for filter values without a separate privacy review.

## CSV export parity

### Explorer and CSV amount semantics

The canonical `/transactions/explorer` endpoint declares `amount_basis` separately
from From/To direction. Without an account/type scope, a balanced two-split
transaction between different accounts in the transaction currency has a
`neutral_magnitude` (unsigned decimal string). Split iteration or split GUID order
must not choose its sign. Composite, mixed-currency, or otherwise unproven totals
use `multiple_amounts` and `representative_amount=null`; inspect the split details.

Account-scoped explorer values use signed net split quantities in the selected
account currency, not transaction-currency split values. A zero net change is a
real zero, not missing data. Multiple selected accounts retain the existing
single configured base-currency restriction; unsupported currency scopes are
still rejected rather than summed or converted. Income/expense type scopes also
use quantities of matching accounts in the configured currency. Both table and
mobile cards label the basis next to the amount.

The legacy CSV columns `amount`, `currency`, `account_id`, and `account_name`
describe a signed quantity of the named account, not the explorer's unscoped
unsigned magnitude. With `account_id`, `amount` is that account's net quantity
(including repeated splits). Without `account_id`, the legacy export identifies
the representative account/split it uses; do not interpret its sign as global
income/expense. Account-scoped amount filters use the absolute net quantity too.
For supported shared filters, CSV and explorer select the same transaction IDs;
the UI continues to disable CSV for unsupported explorer-only filter shapes.
Neither endpoint performs FX conversion or sums different currencies.

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

The transaction list and account-detail pages now show the current matching row count before export. If the matching set is empty, the UI warns that the downloaded CSV would contain only the header row. If the matching set is above the 10,000-row cap, the UI warns that the export will be truncated and recommends narrower filters. These messages are advisory display copy derived from the same read-only list/count metadata; no CSV body is stored in the browser or committed by the app.

Account-detail CSV export is the same endpoint with a fixed `account_id` filter. The account page preserves the account scope plus active query/date/amount/state filters, and the same row-count/empty/truncation guidance applies.

## Safety notes

- Export is read-only.
- Export files may contain sensitive financial data; do not commit real exports.
- Query search is deliberately a simple read-only substring matcher over description/notes/split memo fields, not a database full-text index and not a promise to expose every raw GnuCash text column.
- State filtering is read-only and reflects the split reconciliation state stored by GnuCash; it does not infer a new transaction workflow or edit cleared/reconciled flags.
- No currency conversion is performed or implied.
- Amounts remain string/Decimal-style values; do not use floats for money in new code.
