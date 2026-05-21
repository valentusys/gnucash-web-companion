# Phase 243 handoff — write-alpha transaction ownership model

Date: 2026-05-21
Status: COMPLETE

## Summary

Phase 243 defined and implemented the first write-alpha transaction ownership model in the app metadata DB.

Successful write-alpha CREATE now records a `write_alpha_transaction_ownership` row after the existing successful write/audit path. The marker links `book_id`, `transaction_id`, `created_by_user_id`, `created_by_write_alpha`, `created_at`, and `last_mutated_at`, and is unique per `(book_id, transaction_id)`.

The ownership marker is stored only in app metadata. It does not write marker metadata into the GnuCash book, does not store amounts/accounts/memos/descriptions/request payloads/paths, and does not expand mutation scope. Later Phase 244/245 backend guards can use this table to constrain PATCH/DELETE to write-alpha-created transactions.

## Files changed

- `apps/api/app/models/__init__.py` — added `WriteAlphaTransactionOwnership` model and book relationship.
- `apps/api/app/routers/transactions.py` — records ownership metadata after successful write-alpha CREATE.
- `apps/api/tests/test_models.py` — covers ownership marker fields and uniqueness.
- `apps/api/tests/test_transaction_writes.py` — covers CREATE-path ownership marker creation for the disposable write-alpha fixture path.
- `docs/write-alpha/transaction-ownership.md` — ownership model design and safety boundaries.
- `README.md`, `README.ru.md`, `docs/ROADMAP.md`, `PROJECT_STATUS.md`, `CHANGELOG.md`, `scripts/check_public_status.py`, `apps/api/tests/test_public_status_guard.py` — public status/handoff synchronization for Phase 243.
- `docs/handoff/phase-243.md` — this handoff.

## Verification performed

- `cd apps/api && pytest tests/test_models.py tests/test_transaction_writes.py::TestWriteAlphaCreateRouteDisposableFixture::test_enabled_create_route_writes_disposable_fixture_with_backup_audit_and_lock tests/test_public_status_guard.py -q` — passed, 32 tests.
- `python3 scripts/check_public_status.py` — passed.
- `cd apps/api && pytest -q` — passed, 553 tests.
- `JWT_SECRET=dummy-local-secret APP_ADMIN_PASSWORD=dummy-local-password docker compose config --quiet` — passed.
- `git diff --check` — passed.
- Sensitive tracked-file hygiene scan — passed.
- `git status --short` — inspected; only intended tracked files plus untracked `.hermes/` were present before commit.

## Safety boundaries

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- Backend `APP_ENV=test` write-alpha gate was not weakened.
- No amount/account mutation expansion was added.
- No migration or write touches GnuCash book data beyond the existing write-alpha CREATE service behavior.
- Ownership metadata is app metadata only.
- No real/private/only-copy book, runtime book, app DB, backup, `.env`, CSV/export, screenshot, token, key, cert, raw path, account name, memo, amount, or private financial data was committed.
- No release/tag/package/publication was performed.
- No production/security/public-internet/broad-compatibility or real/private-book write-safety claim was added.

## Risks / next phase

- Phase 243 only records ownership for successful CREATE. PATCH/DELETE still need explicit backend ownership guards in Phase 244/245 before the boundary is complete.
- Frontend ownership UX remains a later phase; backend guards must remain authoritative.
