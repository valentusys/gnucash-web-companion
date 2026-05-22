# PATCH-one copied-book plan

Status: prepared in Phase 282. No mutation authorized by this document.

## Purpose

Define a narrow future one-PATCH procedure for a copied/restorable GnuCash working book after Phase 281 allowed planning.

## Preconditions

All must be true before any later PATCH execution is even requested:

1. Owner copied-book dry-run evidence remains accepted.
2. Exactly one owner copied-book CREATE evidence remains accepted.
3. The target transaction was created by write-alpha on the same copied/restorable working copy and is marked as write-alpha-owned in app metadata.
4. The original book is untouched and not used.
5. The copied working book and all backups/evidence remain outside git.
6. `APP_ENV=test` and explicit temporary `GNUCASH_WRITES_ENABLED=true` are used only for the local dogfood runtime.
7. A later PM/Analyst authorization gate approves asking the owner.
8. Owner gives the later exact confirmation block before any owner PATCH execution.

## Exactly one allowed PATCH

A future owner PATCH, if separately authorized, is limited to one metadata-only update on the write-alpha-created test transaction:

- transaction description may be changed to a non-private test marker;
- transaction date may be changed only if the owner intentionally chooses that metadata change;
- one or more split memo fields may be changed to non-private test markers;
- no amount, account, currency, split count, reconciliation state, schedule, import, delete, or account edit is allowed.

## Required evidence

A valid PATCH evidence packet must show only redacted/bounded statuses:

- pre-mutation backup created before PATCH;
- exactly one PATCH attempted and exactly one PATCH performed;
- PATCH target is write-alpha-owned and same-book;
- no amount/account/split-count mutation;
- API read-back matched only metadata/memo markers;
- runtime read-back confirmed amount/account fingerprint unchanged;
- one successful `transaction.patch` audit row;
- no active lock after PATCH;
- compatibility check passed or a documented blocker stopped before owner progression;
- restore verification from pre-PATCH backup passed;
- reset to default-disabled state passed;
- disabled validate/create/PATCH/DELETE probes returned 403 after reset;
- redaction checker passed.

## Abort conditions

Stop immediately and do not retry without review if any of these occur:

- target is original/only-copy/private-only book instead of copied/restorable working copy;
- target/backups/evidence would enter git;
- preflight, backup, read-back, compatibility, restore, reset, or redaction fails;
- PATCH tries to change amount/account/currency/split count;
- PATCH target is not write-alpha-owned for the same book;
- any private path/account/memo/amount/payload appears in evidence;
- any backup-bearing audit row lacks a readable matching backup artifact;
- any active lock remains after mutation;
- disabled-write probes do not return 403 after reset.

## Non-goals

This plan does not authorize mutation, DELETE, release, default write enablement, production use, security claims, broad GnuCash compatibility claims, or original/private/only-copy book write-safety claims.
