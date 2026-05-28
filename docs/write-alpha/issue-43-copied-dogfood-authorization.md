# Issue #43 copied-dogfood authorization

PM authorization status: CONDITIONAL_ONLY.

Exact operation counts are locked for a future copied-book dogfood attempt:
- 2 CREATE
- 1 metadata/memo-only PATCH on a routed state-machine/write-alpha-created disposable transaction
- 1 DELETE of a routed state-machine/write-alpha-created disposable transaction

Conditions before any mutation:
1. Owner-provided copied/restorable GnuCash SQL book is staged outside git on this host.
2. Preflight passes and returns only redacted evidence.
3. Pre-mutation backup succeeds.
4. Restore helper/plan is available.
5. Read-back, audit row, lock lifecycle, restore verification, compatibility check where tooling exists, and default-disabled reset are all performed.
6. Abort immediately on read-back, restore, compatibility, audit, lock release, or default-reset failure.

Forbidden:
- original/working/private/only-copy mutation;
- historical/manual transaction deletion;
- amount/account/split mutation;
- raw private evidence in git.

Current verdict: BLOCKED_MISSING_OWNER_COPY / BLOCKED_NEEDS_DOGFOOD_RUN. No copied-book mutation occurred in this session.
