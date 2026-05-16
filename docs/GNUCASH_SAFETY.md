# GnuCash Safety

GnuCash books contain high-trust accounting data. Treat them as sensitive and hard to repair.

## MVP safety boundary

The MVP is read-only. It must not create, edit, delete, migrate, or otherwise mutate the GnuCash book.

This is a design and implementation boundary, not a promise that pre-alpha software is safe for your only copy of real accounting data. Always test with a disposable copy first.

## Rules

- Keep backups before testing any tool against a real book.
- Prefer non-sensitive fixture books for development.
- Do not point early builds at your only copy of a book.
- Do not store app metadata in the GnuCash book.
- Do not alter the GnuCash SQL schema.
- Avoid lossy floating-point representation for money.
- Be careful with concurrent access from GnuCash desktop and this app.

## GnuCash SQL backend warning

GnuCash SQL books are real accounting databases. Direct table edits, low-code database tools, or migrations can corrupt invariants that GnuCash expects.

This project should access GnuCash data through a deliberate data-access layer and tests, not ad-hoc SQL writes.

## Phase 5 read-only piecash boundary

Phase 5 introduces `GnuCashBookService`, the first direct connection point to GnuCash SQL books through `piecash`.

Safety rules for this service:

- `piecash.open_book(uri_or_path, readonly=True)` for filesystem paths
- `piecash.open_book(uri_conn=uri_or_path, readonly=True)` for SQL connection URIs
- Keep all GnuCash access behind a service layer; routes and UI must not call `piecash` directly.
- Do not expose `save`, `commit`, mutation, object creation, or delete methods.
- Close books after every read operation.
- Treat missing books and read failures as controlled application errors, not raw tracebacks.
- Return DTOs only; do not leak mutable piecash ORM objects to API/routes/UI code.
- Represent money as `Decimal` internally and strings externally. Never use floats for money.
- Use fixture or mock-based tests unless validating against a disposable sample book.

## Basic reports and multi-currency limitation

Phase 8 dashboard reports are deliberately basic and read-only. They must not infer exchange rates or perform fake currency conversion.

Current limitation:

- Summary, cashflow, and expenses-by-account reports aggregate only accounts/splits whose commodity matches the configured book `base_currency`.
- Non-base-currency accounts/splits are excluded from totals instead of being converted.
- API responses keep money as strings and expose a single `currency` for aggregated totals.
- Future multi-currency reporting must define an explicit exchange-rate source, date policy, and UI disclosure before totals can combine currencies.

## Phase 12 controlled write boundary

Phase 12 introduces a deliberately narrow v0.2 write surface. The original v0.1 read-only flows remain the stable baseline; write operations are opt-in by capability and endpoint, not a general editing mode.

Allowed first-pass writes:

- Create a transaction with two or more splits.
- Patch transaction metadata only: description, posted date, and split memos.

Still not allowed:

- Delete transactions.
- Edit split amounts or accounts on existing transactions.
- Recurring transactions.
- CSV/OFX import.
- Direct SQL writes.
- Bypassing backups or locks.

Every write must follow this order:

1. Validate the request using exact `Decimal` arithmetic only.
2. Check that the authenticated user has `editor` or `owner` access to the book.
3. Acquire the per-book write lock.
4. Create a timestamped backup of the GnuCash book.
5. Open the book with `piecash` in write mode.
6. Apply the mutation.
7. Save/commit the book.
8. Write an app metadata `AuditLog` entry containing user id, book id, action, transaction id, request summary, backup path, result, and timestamp.
9. Release the lock in a `finally` path.

Validation rules:

- At least two splits are required.
- Splits must balance to zero per currency.
- Amounts must be decimal strings; floats are not accepted.
- All accounts must exist.
- Placeholder accounts are rejected by default.
- Currency codes must be valid three-letter uppercase codes and match account commodities where available.

Backups:

- Backups are timestamped and stored per book under a sibling `backups/<book-stem>/` directory for filesystem books, e.g. `/data/backups/main/...` when the book is under `/data/books/`.
- If backup creation fails, the write must not proceed.
- The backup path is recorded in the audit log payload.

Locking:

- The current lock is an in-process per-book lock and returns a controlled conflict when a second write tries to run concurrently.
- This is safe for the single-process container deployment used by the current MVP.
- Multi-worker or multi-host deployments must replace it with a file or distributed lock before write mode is considered production-safe.

Operational guidance:

- Continue testing with disposable copies first.
- Keep external backups outside the app as well.
- Do not use GnuCash Desktop and this app to write to the same book at the same time.
- Treat Phase 12 as controlled-write pre-alpha, not a full accounting editor.
