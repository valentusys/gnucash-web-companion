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
