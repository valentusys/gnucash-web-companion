# GnuCash Safety

GnuCash books contain high-trust accounting data. Treat them as sensitive and hard to repair.

## MVP safety boundary

The MVP is read-only. It must not create, edit, delete, migrate, or otherwise mutate the GnuCash book.

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

## Future write mode requirements

Before any write feature is accepted, the project needs:

- Explicit opt-in configuration.
- Backup strategy.
- Locking/concurrency strategy.
- Audit log or write history.
- Validation of double-entry invariants.
- Exact numeric handling.
- Recovery documentation.
- Extensive fixture coverage.
