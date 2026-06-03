# Daytime W3 authorization handoff

Status: AUTHORIZE_W3_COPIED_BOOK_DOGFOOD_WITH_EXACT_COUNTS

## Authorization basis

W3 gate reported a staged outside-git copied/restorable target for this run. The original/source book remains excluded from mutation scope.

## Exact counts

- CREATE: 2
- PATCH: 1 metadata/memo-only, write-alpha-created transaction only
- DELETE: 1 write-alpha-created disposable transaction only

No additional operation is authorized.

## Worker instruction

Run the W3 copied-book dogfood helper against the staged copy only. Evidence must be redacted before it is summarized in committed docs or GitHub comments. Stop on first failed backup, audit, read-back, restore, compatibility, lock/default-reset, or redaction check.
