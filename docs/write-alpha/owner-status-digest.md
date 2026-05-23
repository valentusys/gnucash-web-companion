# Owner status digest after Phase 314

Status: Phase 314 owner-facing digest.

## Short answer

Use the app as read-only by default. Treat write-alpha as paused/waiting unless there is a fresh owner live-stand need and a new exact confirmation packet.

## What is supported now

- Read-only browsing remains the practical path.
- Current public read-only pre-release: `v0.1.7-readonly`.
- Current public experimental write-alpha pre-release: `v0.2.8-writealpha`.
- Write-alpha code remains disabled by default with `GNUCASH_WRITES_ENABLED=false`.
- If explicitly enabled for test work, write-alpha remains constrained by the backend `APP_ENV=test` gate.

## Accepted write-alpha evidence

Accepted narrowly:

- owner copied-book dry-run evidence as dry-run only;
- exactly one owner copied-book CREATE-one evidence run on one copied/restorable working copy outside git;
- exactly one fresh owner copied-book CREATE-to-PATCH chain: one CREATE followed by one metadata/memo-only PATCH on the same write-alpha-created transaction.

## Still not accepted

- DELETE on an owner copied book: not run, blocked, no request packet.
- Writes on original/private/only-copy books: forbidden.
- Production readiness, security audit, public-internet safety, broad GnuCash compatibility, or general write safety: not claimed.

## Exact next owner action

No immediate owner action is required for write-alpha. Continue read-only use/testing. If a new write-alpha need appears, first provide live-stand feedback describing the practical need; do not run CREATE/PATCH/DELETE until a new exact confirmation packet is prepared and accepted.
