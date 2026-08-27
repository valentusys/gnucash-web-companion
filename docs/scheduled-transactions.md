# Scheduled/recurring transactions

Status: pre-alpha, read-only deterministic occurrence forecast.

`gnucash-web-companion` can show a conservative scheduled-transaction forecast from GnuCash metadata. GnuCash Desktop remains the authoritative editor. The backend opens the book read-only, reads every recurrence table row for each schedule, and never creates or updates a scheduled instance.

## What is shown

The API may show:

- scheduled transaction id and name;
- enabled/disabled state;
- configured start, end, and last-occurrence dates;
- configured total and remaining occurrence counts;
- auto-create/auto-notify flags and advance-day values;
- every recurrence row: period type, multiplier, anchor date, and weekend adjustment;
- deterministic next due date and overdue state;
- bounded due-date lists for the next 7 and 30 days;
- a template amount only when one template transaction has balanced constant decimal formulas and a known currency;
- otherwise, a typed redacted `unresolved` or `not_available` amount state;
- `new_transactions_created: 0` as an explicit read-only invariant.

The optional `as_of_date=YYYY-MM-DD` query parameter makes forecast results reproducible. Without it, the backend uses the request date and returns that date in `forecast.as_of_date`.

## Recurrence semantics

Forecasting preserves the GnuCash schedule anchors and supports the stored recurrence period types:

- once;
- day;
- week;
- month;
- end of month;
- nth weekday;
- last weekday;
- year.

Composite schedules use the union of all recurrence rows, including semi-monthly and multiple-weekday schedules. Dates are de-duplicated and ordered. Schedule start, inclusive end date, last occurrence, finite remaining occurrences, short months, leap years, and `none`/`back`/`forward` weekend adjustment are applied deterministically.

The 7-day list contains at most 7 unique dates, starting on `as_of_date`. The 30-day list contains at most 30 unique dates. An overdue `next_due_date` remains visible even though overdue dates are not repeated in the future windows.

## Typed safe failures

Missing, cyclic/non-advancing, inconsistent, or unsupported recurrence metadata does not produce a guessed date. End-date and finite-occurrence limits are mutually exclusive in GnuCash metadata; a conflicting pair or a last occurrence after the end date is rejected. The API returns HTTP 422 with a redacted stable detail code:

- `scheduled_recurrence_invalid_metadata`;
- `scheduled_recurrence_cycle`.

The error does not include schedule names, formulas, account names, book paths, or raw metadata.

## Template amount safety

Template account names, target account names, memos, transaction descriptions, raw formulas, and raw SQL are never returned. Formula text is accepted only when every required formula is a constant decimal string and the template is balanced. Any variable, expression, missing formula slot, unsupported shape, missing currency, or imbalance returns `amount: null` with a redacted reason. It is never converted to a fake zero.

No currency conversion is attempted.

## What is intentionally not done

The forecast does not:

- create, edit, delete, defer, or instantiate scheduled transactions;
- update last-occurrence, remaining-occurrence, or instance-count fields;
- enable write mode or change the `GNUCASH_WRITES_ENABLED=false` default;
- expose template account names, target accounts, memos, descriptions, formula text, private paths, or SQL;
- replace GnuCash Desktop as the scheduled-transaction editor.

## API endpoints

Authenticated read-only endpoints:

- `GET /scheduled-transactions` — default-book alias;
- `GET /books/{book_id}/scheduled-transactions` — active accessible book.

Both accept optional `as_of_date=YYYY-MM-DD` and preserve the existing book access boundary. Archived or unauthorized books remain hidden or blocked by the books API rules.

## Display filtering

The existing `/scheduled` page can filter and sort the safe API rows with URL query parameters only. It does not persist schedule metadata or filters in browser storage. A later frontend block consumes the forecast fields for upcoming, overdue, and next-30-days grouping.

## Safety note

Use the application as a read-only companion. During pre-alpha testing, use generated/disposable books. GnuCash Desktop remains the authoritative accounting application.
