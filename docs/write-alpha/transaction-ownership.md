# Write-alpha transaction ownership model

Date: 2026-05-21
Status: Phase 243 implementation baseline

## Purpose

Write-alpha CREATE can produce transaction GUIDs in a GnuCash book. Future PATCH and DELETE guards need an app-owned way to distinguish those write-alpha-created transactions from historical, imported, or manually edited GnuCash transactions.

The ownership model is intentionally app metadata only. It does not write marker metadata into the GnuCash book and it does not expand write scope.

## Storage model

The app metadata database now contains `write_alpha_transaction_ownership` rows with this safe schema:

| Field | Meaning |
| --- | --- |
| `book_id` | App metadata book id for the configured book record. |
| `transaction_id` | GnuCash transaction GUID returned by successful write-alpha CREATE. |
| `created_by_user_id` | App metadata user id that requested CREATE, nullable if the user is later removed. |
| `created_by_write_alpha` | Boolean marker; `true` for rows created by the write-alpha CREATE route. |
| `created_at` | App metadata timestamp when ownership was recorded. |
| `last_mutated_at` | App metadata timestamp for the latest write-alpha mutation known to the app. Phase 243 initializes it to `created_at`; later PATCH/DELETE guard phases can update it. |

`book_id + transaction_id` is unique so one app metadata DB has at most one ownership marker for a given transaction in a given book.

## CREATE path behavior

After a successful write-alpha CREATE returns a transaction GUID, the API records an ownership row in the app metadata DB:

1. write-alpha gates remain enforced first: `GNUCASH_WRITES_ENABLED=true`, edit access, and `APP_ENV=test`;
2. GnuCash write service performs the existing validation/lock/backup/write flow;
3. the existing audit log is updated as before;
4. the app metadata ownership marker is inserted with only safe metadata.

Failed validation, lock, or GnuCash write errors do not create ownership markers because no successful write-alpha transaction GUID exists.

## Safety boundaries

- No ownership metadata is written into the GnuCash book.
- The model stores no amounts, account names, account GUIDs, memos, descriptions, request payloads, backup paths, file paths, CSV/export data, screenshots, tokens, keys, or certs.
- The model does not enable writes by default.
- `GNUCASH_WRITES_ENABLED=false` remains the default and the backend `APP_ENV=test` gate remains required for explicit write-alpha runs.
- This does not make real/private or only-copy books safe for writes; evidence remains synthetic/disposable or copied-test-book only.

## Later guard use

Phase 244/245 can use this table as the authoritative backend guard source:

- PATCH should allow only transactions with an ownership row for the same `book_id` and `transaction_id` where `created_by_write_alpha=true`.
- DELETE should use the same check before destructive mutation.
- Rejected non-owned PATCH/DELETE attempts should fail before GnuCash mutation and should not imply historical/manual transactions are editable.

Frontend hiding remains supporting UX only; backend ownership checks are authoritative.
