# Autonomous long run — cycle 2

Issue: #13 Book management UI

PM scope:
- Strengthen admin metadata registration validation for mounted paths.
- Ensure the registered target is not merely an existing arbitrary file.
- Keep validation errors path-redacted and avoid opening accounting values.

Non-goals:
- No file upload or browse UI.
- No GnuCash data reads for account/transaction values during registration.
- No write-mode work.

Implementation:
- API registration now checks that the mounted target is a readable SQLite file.
- API registration now checks for core GnuCash SQLite schema marker tables: `versions`, `books`, `accounts`, `transactions`, `splits`, `commodities`.
- Non-SQLite files and plain SQLite databases are rejected with generic, private-path-safe errors.
- Tests use minimal synthetic SQLite schema fixtures rather than arbitrary text files.

Verification:
- `cd apps/api && pytest tests/test_multi_book_access.py -q` — 45 passed.

Safety notes:
- Validation only inspects SQLite schema table names in read-only mode.
- It does not query account names, transaction descriptions, memos, amounts, or private values.
- Error responses do not include private mounted paths.

Remaining #13 work after this cycle:
- Update docs for mounted book registration, default switching, and registry removal limitations.
- Run full gates and decide whether #13 closure criteria are now satisfied.
