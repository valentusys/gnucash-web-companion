# Practical-use verdict

Status: Phase 290 verdict.

## Blunt answer

Use the project as read-only. Treat write-alpha as experimental and disabled by default.

## What is reasonable now

### Read-only use

Reasonable for local, trusted-network evaluation with the existing documented caveats. Do not treat this as a security audit or public-internet deployment recommendation.

### Synthetic/disposable write-alpha

Reasonable for development testing only, using synthetic/disposable books and explicit test-mode gates. This includes CREATE and PATCH route testing where covered by the existing tests/rehearsals.

### Owner copied-book dry-run

Accepted as dry-run evidence. A copied/restorable book dry-run can be used as a non-mutating safety check when the owner follows the redaction and stop-condition guidance.

### Owner copied-book CREATE

Accepted for exactly one prior copied/restorable-book CREATE evidence item. This does not mean general CREATE safety. It does not authorize repeated owner mutations without a fresh explicit gate.

### Owner copied-book PATCH

Not accepted yet. A request packet exists for one metadata/memo-only PATCH, but no owner PATCH evidence has been provided. Do not claim owner PATCH support.

### DELETE

Blocked for owner dogfood. Do not prepare or run owner DELETE.

### Original/only-copy/private production books

Forbidden and unsupported for writes. Do not run write-alpha against an original book or only copy.

## Current write gates

- `GNUCASH_WRITES_ENABLED=false` remains the default.
- Enabled write-alpha still requires `APP_ENV=test`.
- Writes must not be enabled by default.
- Private data, raw paths, account names, memos, amounts, screenshots, exports, app DBs, backups, tokens, keys, and certs must not be committed.

## Practical next step

If the owner wants to continue write-alpha dogfood, the only narrow next step is external owner execution of the Phase 285 PATCH-one packet on a copied/restorable book, followed by redacted evidence submission. The agent must not execute that owner PATCH automatically.
