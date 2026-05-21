# Write-alpha transaction ownership model

Date: 2026-05-21
Status: Phase 249 operator warning baseline

## Purpose

Write-alpha CREATE can produce transaction GUIDs in a GnuCash book. PATCH and DELETE guards use
an app-owned marker to distinguish those write-alpha-created transactions from historical,
imported, or manually edited GnuCash transactions.

The ownership model is intentionally app metadata only. It does not write marker metadata into the
GnuCash book and it does not expand write scope.

Operator rule: write-alpha can only PATCH or DELETE transactions that this app previously created
through the write-alpha CREATE route and then recorded in app metadata. Historical/manual GnuCash
transactions remain read-only in this app, even when write-alpha is explicitly enabled for a local
`APP_ENV=test` run.

## Storage model

The app metadata database now contains `write_alpha_transaction_ownership` rows with this safe schema:

| Field | Meaning |
| --- | --- |
| `book_id` | App metadata book id for the configured book record. |
| `transaction_id` | GnuCash transaction GUID returned by successful write-alpha CREATE. |
| `created_by_user_id` | App metadata user id that requested CREATE, nullable if the user is later removed. |
| `created_by_write_alpha` | Boolean marker; `true` for rows created by the write-alpha CREATE route. |
| `created_at` | App metadata timestamp when ownership was recorded. |
| `last_mutated_at` | App metadata timestamp for the latest write-alpha mutation known to the app. Phase 243 initializes it to `created_at`; Phase 244 refreshes it after allowed PATCH mutations; Phase 245 refreshes it after allowed DELETE mutations. |

`book_id + transaction_id` is unique so one app metadata DB has at most one ownership marker for a given transaction in a given book.

## CREATE path behavior

After a successful write-alpha CREATE returns a transaction GUID, the API records an ownership row in the app metadata DB:

1. write-alpha gates remain enforced first: `GNUCASH_WRITES_ENABLED=true`, edit access, and `APP_ENV=test`;
2. GnuCash write service performs the existing validation/lock/backup/write flow;
3. the existing audit log is updated as before;
4. the app metadata ownership marker is inserted with only safe metadata.

Failed validation, lock, or GnuCash write errors do not create ownership markers because no successful write-alpha transaction GUID exists.

Successful CREATE is the only normal path that creates a write-alpha-owned transaction marker. A
transaction that already existed in the source book before the test run is not considered owned just
because it is visible in the UI or because write-alpha gates are enabled.

## Safety boundaries

- No ownership metadata is written into the GnuCash book.
- The model stores no amounts, account names, account GUIDs, memos, descriptions, request payloads, backup paths, file paths, CSV/export data, screenshots, tokens, keys, or certs.
- The model does not enable writes by default.
- `GNUCASH_WRITES_ENABLED=false` remains the default and the backend `APP_ENV=test` gate remains required for explicit write-alpha runs.
- This does not make real/private or only-copy books safe for writes; evidence remains synthetic/disposable or copied-test-book only.
- Ownership markers are a safety boundary, not a production-readiness claim. They reduce accidental
  edits/deletes of historical/manual transactions, but they do not prove safe writes against
  real/private, original, or only-copy books.

## PATCH guard behavior

Phase 244 uses this table as the authoritative backend guard source for PATCH:

- PATCH allows only transactions with an ownership row for the same `book_id` and `transaction_id`
  where `created_by_write_alpha=true`.
- The check runs after the existing write-enabled, edit-access, and `APP_ENV=test` gates, but before
  constructing `GnuCashWriteService`.
- Rejected non-owned PATCH attempts return 403 before backup, lock, audit row, or GnuCash mutation.
- Allowed PATCH remains limited to description, date, and split memo metadata; amount and account
  changes remain out of scope.
- Successful allowed PATCH refreshes `last_mutated_at` in app metadata only.

## DELETE guard behavior

Phase 245 uses the same table as the authoritative backend guard source for DELETE:

- DELETE allows only transactions with an ownership row for the same `book_id` and `transaction_id`
  where `created_by_write_alpha=true`.
- The check runs after the existing write-enabled, edit-access, and `APP_ENV=test` gates, but before
  constructing `GnuCashWriteService`.
- Rejected non-owned DELETE attempts return 403 before backup, lock, audit row, or GnuCash mutation.
- Allowed DELETE keeps the existing write-alpha lock → backup → piecash delete → audit → unlock flow.
- Successful allowed DELETE refreshes `last_mutated_at` in app metadata only.

Rejected non-owned DELETE attempts should not imply historical/manual transactions are editable or
deletable.

Frontend hiding remains supporting UX only; backend ownership checks are authoritative.

## Operator warning

Do not treat write-alpha as a general GnuCash transaction editor:

- CREATE creates transactions that are owned by this app's write-alpha flow.
- PATCH and DELETE are limited to those write-alpha-owned transaction IDs for the same app metadata
  book record.
- Historical, imported, or manually created GnuCash transactions remain read-only in this app.
- A copied/disposable test book can still be damaged by bugs, operator error, unsupported GnuCash
  semantics, environment mistakes, or restore mistakes.
- This boundary does not make real/private, original, production, shared, or only-copy books safe for
  write-alpha testing.

For copied-book dogfood, create a fresh write-alpha test transaction first and only patch/delete that
transaction if the specific runbook phase authorizes it. Never patch/delete an arbitrary historical
transaction to "try the route".
