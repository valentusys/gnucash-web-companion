# Phase 12 Handoff — Controlled GnuCash Writes

## Status

Phase 12 introduces the first controlled write surface for the v0.2 line. It is intentionally narrow and keeps the v0.1 read-only flows as the stable baseline.

## Scope implemented

Backend:

- `POST /books/{book_id}/transactions/validate`
- `POST /books/{book_id}/transactions`
- `PATCH /books/{book_id}/transactions/{transaction_id}`
- Create transactions with two or more splits.
- Patch transaction metadata only: description, posted date, split memos.
- Per-book in-process write lock.
- Timestamped backup before each write.
- App metadata audit log entries after successful writes.
- Decimal-string validation; no float arithmetic.

Frontend:

- `/transactions/new` simple two-split transaction form.
- Account picker based on existing accounts API.
- Validation action before submit.
- Confirmation before final create.
- Redirect to transaction detail after successful write.
- Link from `/transactions` to the new transaction form.

## Files added

- `apps/api/app/schemas/gnucash_writes.py`
- `apps/api/app/services/backup.py`
- `apps/api/app/services/gnucash_write.py`
- `apps/api/app/services/write_lock.py`
- `apps/api/tests/test_transaction_writes.py`
- `apps/web/src/routes/transactions/new/+page.server.ts`
- `apps/web/src/routes/transactions/new/+page.svelte`
- `docs/handoff/phase-12.md`

## Files changed

- `apps/api/app/routers/transactions.py`
- `apps/web/src/lib/api/types.ts`
- `apps/web/src/routes/transactions/+page.svelte`
- `docs/GNUCASH_SAFETY.md`

## Write flow

1. Validate request.
2. Check authenticated user has `editor` or `owner` role.
3. Acquire per-book write lock.
4. Create backup.
5. Open GnuCash book with `piecash` in write mode.
6. Apply mutation.
7. Save book.
8. Write app metadata audit log.
9. Release lock in `finally`.
10. Return transaction id, backup path, and audit log id.

## Validation rules

- At least two splits.
- Per-currency split totals must equal zero.
- Amounts are decimal strings.
- Currency codes are three uppercase letters.
- Accounts must exist.
- Placeholder accounts are rejected by default.
- Account currency mismatches are rejected when account commodities are available.

## Explicit non-goals

- No transaction delete.
- No recurring transactions.
- No CSV/OFX import.
- No split amount/account edits on existing transactions.
- No direct SQL writes.
- No write without backup.
- No concurrent writes to the same book.

## Known limitations

- The write lock is in-process. It is appropriate for the current single-process container deployment, but multi-worker or multi-host deployments need file/distributed locking before write mode is production-safe.
- The frontend implements the simple two-split form first. Advanced split UI can be added later on top of the same backend create endpoint.
- Tests use fake piecash objects for most write behavior. Real disposable-book integration tests should be added before production write use.

## Verification

Run from repo root:

```bash
cd apps/api && pytest -q
cd ../web && npm run check && npm run test:auth-routes && npm run build
```
