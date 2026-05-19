# Scheduled/recurring transactions

Status: Phase 157 pre-alpha read-only awareness with URL-only display filtering.

`gnucash-web-companion` can show a conservative read-only summary of GnuCash scheduled/recurring transaction metadata when the configured book exposes that metadata through the safe piecash adapter path. The `/scheduled` page can filter and sort the displayed safe metadata with URL query parameters only; it does not persist scheduled metadata or filter values in browser storage.

## What is shown

The API/UI may show:

- scheduled transaction id and name
- enabled/disabled state
- configured start/end/last-occurred dates
- configured occurrence counts when present
- auto-create/auto-notify flags
- advance creation/notification day values
- whether a template account reference exists
- raw recurrence metadata such as period type, multiplier, period start, and weekend adjustment

## What is intentionally not shown

The pre-alpha view does not show or do any of the following:

- create, edit, delete, or instantiate scheduled transactions
- calculate or promise exact upcoming run dates
- expose template split details, memos, transaction descriptions, account names, amounts, or raw SQL dumps
- replace GnuCash Desktop as the scheduled-transaction editor
- enable write mode or change `GNUCASH_WRITES_ENABLED=false` default posture

If no scheduled transactions are present, or if a book/schema cannot expose them through the safe adapter path, the UI shows an empty/limitation state. That is intentional; the app must not fake schedule predictions.

## Display filtering and sorting

The web page supports URL-only display controls for the already-safe metadata returned by the API:

- status filter: all, enabled, or disabled
- template-reference filter: all, template present, or no template reference
- sort display: start date, name, or enabled first

These controls do not call write routes, do not expose additional GnuCash template details, and do not use localStorage/sessionStorage. Filtered empty states explain that the current display filters hide the safe metadata rows and provide a clear-filters link.

## API endpoints

Authenticated read-only endpoints:

- `GET /scheduled-transactions` — default-book alias for the MVP single-book flow.
- `GET /books/{book_id}/scheduled-transactions` — book-aware endpoint for the active accessible book.

Both endpoints preserve the existing book access boundary. Archived or unauthorized books remain hidden/blocked by the existing books API rules.

## Safety note

GnuCash Desktop remains the authoritative editor. Use this app only as a read-only companion, preferably against copied/disposable books while the project is pre-alpha and not production-ready or security-audited.
